from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from services.mappa_service import MappaService # Assumendo che esista
from models.mappa_model import SegnalazioneMapDTO, PosizioneGPS
from db.connection import get_database # Assumendo che esista

router = APIRouter(prefix="/mappa", tags=["Gestione Mappa"])

def get_mappa_service(db=Depends(get_database)):
    """Factory method per Dependency Injection del Service"""
    # La MappaService deve gestire la logica di business e l'interazione con il ControllerDBFacade (vedi ODD)
    return MappaService(db)

# --- Endpoint 1: Visualizzazione Mappa e Segnalazioni Attive (RF_03, RF_13) ---
@router.get("/segnalazioni/attive", response_model=List[SegnalazioneMapDTO])
def get_active_incidents(
    service: MappaService = Depends(get_mappa_service)
):
    """
    Scopo: Endpoint per ottenere tutte le segnalazioni di incidenti attive e visibili.

    Parametri Input:
    - user_location (Query Params): La posizione GPS (Lat/Lon) dell'utente per centrare la mappa
      e filtrare gli incidenti (entro 10 km, come da RF_03).

    Valore di Ritorno:
    - JSON List (SegnalazioneMapDTO): Lista delle segnalazioni attive, con dati essenziali per la mappa.

    Gestione Errori:
    - 400 Bad Request: Se i dati di posizione non sono validi.
    - 404 Not Found: (Gestito nel Service se necessario, ma l'endpoint ritorna lista vuota se 0 risultati).
    """
    return service.get_active_incidents()

# --- Endpoint 2: Filtraggio per Tipo (RF_18) ---
@router.get("/segnalazioni/filtrate", response_model=List[SegnalazioneMapDTO])
def get_filtered_incidents(
    tipi_incidente: Optional[List[str]] = Query(None, description="Lista dei tipi di incidente su cui filtrare"),
    service: MappaService = Depends(get_mappa_service)
):
    """
    Scopo: Endpoint per filtrare le segnalazioni attive sulla mappa in base al tipo di incidente.

    Parametri Input:
    - user_location (Query Params): Posizione GPS dell'utente.
    - tipi_incidente (Query Params List): Tipi di incidente da visualizzare (es. 'Tamponamento', 'Incendio veicolo').

    Valore di Ritorno:
    - JSON List (SegnalazioneMapDTO): Lista delle segnalazioni che matchano i filtri e sono vicine all'utente.

    Gestione Errori:
    - 400 Bad Request: Tipo di incidente non valido/non riconosciuto.
    """
    return service.get_filtered_incidents(tipi_incidente)

"""--- Endpoint 3: Classificazione per Numero di Segnalazioni (RF_14) ---
@router.get("/classifica", response_model=List[SegnalazioneMapDTO])
def get_incident_ranking(
    user_location: PosizioneGPS = Depends(),
    service: MappaService = Depends(get_mappa_service)
):
    
    Scopo: Endpoint per ottenere una classifica degli incidenti nelle vicinanze ordinati per numero di segnalazioni.

    Parametri Input:
    - user_location (Query Params): Posizione GPS dell'utente.

    Valore di Ritorno:
    - JSON List (SegnalazioneMapDTO): Lista ordinata degli incidenti con più segnalazioni.

    Gestione Errori:
    - 400 Bad Request: Dati di posizione non validi.
    
    return service.get_incidents_ranking(user_location)
"""
