"""
Trasformatore dati segnalazione (Versione API).
Utilizza osmnx per scaricare dati stradali in tempo reale dall'API OSM.
Richiede oggetto SegnalazioneInput.
"""

import sys
import os
import logging
from datetime import datetime, date, time as dt_time
import time
import pytz
import osmnx as ox
import pandas as pd
from astral import LocationInfo
from astral.sun import sun

# Configurazione path per import moduli
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

APP_DIR = os.path.join(BASE_DIR, 'app')
if APP_DIR not in sys.path:
    sys.path.append(APP_DIR)

try:
    from app.schemas.segnalazione_schema import SegnalazioneInput
except ImportError:
    try:
        from schemas.segnalazione_schema import SegnalazioneInput
    except ImportError as e:
        print(f"Errore importazione SegnalazioneInput: {e}")
        # Definizione dummy per evitare crash immediato se import fallisce (solo per IDE/Linting)
        class SegnalazioneInput:
            pass

# Configurazione OSMnx
ox.settings.use_cache = True
ox.settings.log_console = False

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rileva_dati_strada(lat: float, lon: float, raggio: float = 40) -> dict:
    """
    Scarica il grafo stradale intorno al punto e analizza feature.
    Restituisce un dizionario con i flag booleani.
    """
    risultati = {
        "Bump": False,
        "Crossing": False,
        "Give_Way": False,
        "Junction": False,
        "Railway": False,
        "Roundabout": False,
        "Stop": False,
        "Traffic_Signal": False,
        "Turning_Loop": False,
        "Road_Type": "Unknown"
    }

    try:
        # STRATEGIA COMBINATA:
        # 1. Scarichiamo un grafo abbastanza ampio (250m) per essere sicuri di includere l'arco stradale
        #    anche se i nodi sono lontani (tipico di autostrade/viadotti).
        dist_search = 250
        G = ox.graph_from_point((lat, lon), dist=dist_search, network_type='all', simplify=True)
        
        if len(G.nodes) == 0:
             # Se ancora vuoto, proviamo un raggio d'emergenza (500m)
            logger.warning(f"Grafo vuoto a {dist_search}m, ritento con 500m...")
            G = ox.graph_from_point((lat, lon), dist=500, network_type='all', simplify=True)

    except Exception as e:
        logger.warning(f"OSMnx graph download fallito per ({lat}, {lon}): {e}")
        return {k: None for k in risultati}

    try:
        # Geometrie nodi e archi
        nodes, edges = ox.graph_to_gdfs(G)
        
        # 1. Analisi Tipologia Strada (Metodo NEAREST EDGE)
        # Invece di guardare tutte le strade nel raggio, cerchiamo quella PIÙ VICINA al punto esatto.
        # Questo evita di rilevare "residential" se sei in autostrada ma vicino a un paese.
        try:
            u, v, key = ox.nearest_edges(G, lon, lat)
            nearest_edge = G[u][v][key]
            
            # Tipo strada più vicina
            road_type = nearest_edge.get('highway', 'Unknown')
            if isinstance(road_type, list):
                # Se è una lista, prendi il primo o cerca il più importante
                priorita = ['motorway', 'trunk', 'primary', 'secondary']
                found = False
                for p in priorita:
                    if p in road_type:
                        road_type = p
                        found = True
                        break
                if not found:
                    road_type = road_type[0]
            
            risultati["Road_Type"] = str(road_type)
            
            # Extra: Rileva attributi specifici dell'arco più vicino
            if 'junction' in nearest_edge:
                 if 'roundabout' in str(nearest_edge['junction']):
                     risultati["Roundabout"] = True

        except Exception as e_near:
            logger.warning(f"Nearest edge fallito: {e_near}, fallback su analisi generale")
            # Fallback alla vecchia logica (tutte le strade nel raggio)
            if 'highway' in edges.columns:
                tipi = edges['highway'].explode().unique()
                # ... (logica di priorità esistente o semplificata)
                risultati["Road_Type"] = str(tipi[0]) if len(tipi) > 0 else "Unknown"

        # 2. Analisi Caratteristiche Nodi (Resta valida l'analisi di contesto allargato per stop, semafori ecc)
        if 'highway' in nodes.columns:
            hw_tags = nodes['highway'].astype(str)
            risultati["Traffic_Signal"] = bool(hw_tags.str.contains('traffic_signals', case=False).any())
            risultati["Stop"] = bool(hw_tags.str.contains('stop', case=False).any())
            risultati["Bump"] = bool(hw_tags.str.contains('speed_bump|hump', case=False).any())
            risultati["Crossing"] = bool(hw_tags.str.contains('crossing', case=False).any())
            risultati["Give_Way"] = bool(hw_tags.str.contains('give_way', case=False).any())
            risultati["Turning_Loop"] = bool(hw_tags.str.contains('turning_circle|turning_loop', case=False).any())

        # 3. Analisi Topologia (Archi e Nodi)
        if 'junction' in edges.columns:
            risultati["Roundabout"] = bool(edges['junction'].astype(str).str.contains('roundabout', case=False).any())
        
        # Intersezione: se c'è almeno un nodo con grado > 2
        risultati["Junction"] = any(G.degree(node) > 2 for node in G.nodes)

    except Exception as e:
        logger.error(f"Errore durante l'analisi del grafo: {e}")
        # In caso di errore parziale, ritorniamo comunque quello che abbiamo estratto o il default
        return risultati

    # 4. Ferrovia (Feature separata)
    try:
        tags = {"railway": ["station", "level_crossing", "rail"]}
        poi = ox.features_from_point((lat, lon), tags=tags, dist=raggio)
        if not poi.empty and 'railway' in poi.columns:
            risultati["Railway"] = bool(poi['railway'].isin(['rail', 'level_crossing']).any())
    except Exception:
        pass # Ignora errori su feature secondaria

    return risultati

def rileva_presenza_luce(lat: float, lon: float, data_ora: datetime) -> bool:
    """Determina se c'è luce solare in base a coordinate e orario."""
    try:
        if lat is None or lon is None or data_ora is None:
            return None
            
        if not isinstance(data_ora, datetime):
            return None
            
        if data_ora.tzinfo is None:
            data_ora = data_ora.replace(tzinfo=pytz.utc)

        loc = LocationInfo(latitude=lat, longitude=lon)
        s = sun(loc.observer, date=data_ora)
        
        return s['dawn'] <= data_ora <= s['dusk']
    except Exception:
        return None

def trasforma_dati_segnalazione(input_data: SegnalazioneInput) -> dict:
    """
    Riceve un oggetto SegnalazioneInput.
    Restituisce features complete per il modello AI.
    """
    if not hasattr(input_data, 'incident_latitude'):
        raise ValueError("Input deve essere un oggetto SegnalazioneInput valido")

    lat = input_data.incident_latitude
    lon = input_data.incident_longitude
    data_ora = datetime.combine(input_data.incident_date, input_data.incident_time)
    
    # 1. Dati Strada (API OSM)
    dati_strada = rileva_dati_strada(lat, lon)
    
    # 2. Dati Luce
    presenza_luce = rileva_presenza_luce(lat, lon, data_ora)
    
    # 3. Composizione Risultato
    risultato = {}
    if dati_strada:
        risultato.update(dati_strada)
    else:
        # Fallback se API fallisce completamente
        keys = ["Bump", "Crossing", "Give_Way", "Junction", "Railway", 
                "Roundabout", "Stop", "Traffic_Signal", "Turning_Loop", "Road_Type"]
        risultato.update({k: None for k in keys})
    
    risultato["Daylight"] = presenza_luce
    risultato["Seriousness"] = input_data.seriousness
    risultato["Category"] = input_data.category
    
    return risultato

if __name__ == "__main__":
    # Test esecuzione diretta
    try:
        test_input = SegnalazioneInput(
            incident_latitude=40.457426, 
            incident_longitude=15.543001,
            incident_date=date.today(),
            incident_time=dt_time(12, 0),
            seriousness="high",
            category="incidente stradale"
        )
        
        print(f"Avvio test API OSM (lat={test_input.incident_latitude}, lon={test_input.incident_longitude})...")
        start_time = time.time()
        
        dati = trasforma_dati_segnalazione(test_input)
        
        end_time = time.time()
        print(f"\nRisultati:\n{dati}")
        print(f"\nTempo impiegato: {end_time - start_time:.4f} secondi")
        
    except NameError:
        print("SegnalazioneInput non definito o import fallito. Controlla i path.")
    except Exception as e:
        print(f"Errore durante il test: {e}")
