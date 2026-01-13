"""
Adapter per l'interfacciamento con l'API RG-Linee_Guida_Comportamentali_AI.

Questo modulo implementa un adapter asincrono per comunicare con il servizio ML
che genera linee guida comportamentali di sicurezza basate sui dati degli incidenti.

Integra il Trasformatore_dati_segnalazione_for_AI_Model per il rilevamento
automatico delle caratteristiche stradali tramite OSMnx.
"""

import httpx
import hashlib
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, time, date
from functools import lru_cache
from schemas.linee_guida_ai_schema import (
    AIGuidelinesInput,
    AIGuidelinesResponse,
    #HealthCheckResponse,
    SeverityLevel,
    IncidentType,
    RoadType
)

# Import del trasformatore dati esistente
try:
    from AI.Trasformatore_dati_segnalazione_for_AI_Model import (
        trasforma_dati_segnalazione,
        rileva_dati_strada,
        rileva_presenza_luce
    )
    TRASFORMATORE_AVAILABLE = True
except ImportError:
    try:
        from app.AI.Trasformatore_dati_segnalazione_for_AI_Model import (
            trasforma_dati_segnalazione,
            rileva_dati_strada,
            rileva_presenza_luce
        )
        TRASFORMATORE_AVAILABLE = True
    except ImportError:
        TRASFORMATORE_AVAILABLE = False
        print("[BehavioralGuidelinesAdapter] Trasformatore non disponibile, uso mapping manuale")


class BehavioralGuidelinesAdapter:
    """
    Adapter per l'API RG-Linee_Guida_Comportamentali_AI.
    
    Gestisce la comunicazione con il servizio ML per ottenere linee guida
    comportamentali basate sui dati degli incidenti stradali.
    
    Attributi:
        base_url (str): URL base dell'API ML.
        timeout (float): Timeout per le richieste HTTP in secondi.
        max_retries (int): Numero massimo di tentativi in caso di errore.
        enable_cache (bool): Se True, abilita il caching delle risposte.
        _cache (Dict): Cache interna per le risposte.
    """


    def __init__(
        self,
        base_url: str = None,
        timeout: float = 10.0,
        max_retries: int = 3,
        enable_cache: bool = True
    ):
        """
        Scopo: Inizializza l'adapter con i parametri di configurazione.

        Parametri:
        - base_url (str, optional): URL base dell'API ML. Se None, usa variabile
          d'ambiente GUIDELINES_AI_API_URL o default localhost:8000.
        - timeout (float): Timeout per le richieste in secondi. Default: 10.0.
        - max_retries (int): Numero massimo di tentativi. Default: 3.
        - enable_cache (bool): Abilita caching risposte. Default: True.

        Valore di ritorno:
        - None

        Eccezioni:
        - None
        """
        self.base_url = base_url or os.environ.get(
            "GUIDELINES_AI_API_URL", 
            "http://localhost:8001"
        )
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_cache = enable_cache
        self._cache: Dict[str, AIGuidelinesResponse] = {}

    def _generate_cache_key(self, input_data: AIGuidelinesInput) -> str:
        """
        Scopo: Genera una chiave di cache univoca basata sull'input.

        Parametri:
        - input_data (AIGuidelinesInput): Dati di input per la richiesta.

        Valore di ritorno:
        - str: Hash SHA256 dell'input serializzato.

        Eccezioni:
        - None
        """
        data_str = input_data.model_dump_json(exclude_none=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[AIGuidelinesResponse]:
        """
        Scopo: Recupera una risposta dalla cache se disponibile.

        Parametri:
        - cache_key (str): Chiave di cache generata dall'input.

        Valore di ritorno:
        - Optional[AIGuidelinesResponse]: Risposta cached o None se non presente.

        Eccezioni:
        - None
        """
        if self.enable_cache and cache_key in self._cache:
            return self._cache[cache_key]
        return None

    def _save_to_cache(self, cache_key: str, response: AIGuidelinesResponse) -> None:
        """
        Scopo: Salva una risposta nella cache.

        Parametri:
        - cache_key (str): Chiave di cache.
        - response (AIGuidelinesResponse): Risposta da salvare.

        Valore di ritorno:
        - None

        Eccezioni:
        - None
        """
        if self.enable_cache:
            self._cache[cache_key] = response



    # async def check_health(self) -> HealthCheckResponse:
    #     """
    #     Scopo: Verifica la disponibilità e lo stato dell'API ML.

    #     Parametri:
    #     - Nessuno.

    #     Valore di ritorno:
    #     - HealthCheckResponse: Stato del servizio ML.

    #     Eccezioni:
    #     - httpx.RequestError: Errori di rete/connessione.
    #     - httpx.HTTPStatusError: Risposte HTTP con status code di errore.
    #     """
    #     async with httpx.AsyncClient(timeout=self.timeout) as client:
    #         response = await client.get(f"{self.base_url}/health")
    #         response.raise_for_status()
    #         return HealthCheckResponse(**response.json())

    # def check_health_sync(self) -> HealthCheckResponse:
    #     """
    #     Scopo: Verifica sincrona della disponibilità dell'API ML.

    #     Parametri:
    #     - Nessuno.

    #     Valore di ritorno:
    #     - HealthCheckResponse: Stato del servizio ML.

    #     Eccezioni:
    #     - httpx.RequestError: Errori di rete/connessione.
    #     - httpx.HTTPStatusError: Risposte HTTP con status code di errore.
    #     """
    #     with httpx.Client(timeout=self.timeout) as client:
    #         response = client.get(f"{self.base_url}/health")
    #         response.raise_for_status()
    #         return HealthCheckResponse(**response.json())

    async def get_guidelines(
        self, 
        input_data: AIGuidelinesInput
    ) -> AIGuidelinesResponse:
        """
        Scopo: Ottiene le linee guida comportamentali dall'API ML.

        Parametri:
        - input_data (AIGuidelinesInput): Dati dell'incidente per la classificazione.

        Valore di ritorno:
        - AIGuidelinesResponse: Linee guida generate dal modello ML.

        Eccezioni:
        - httpx.RequestError: Errori di rete/connessione.
        - httpx.HTTPStatusError: Risposte HTTP con status code di errore.
        - Exception: Altri errori durante la richiesta.
        """
        # Controlla cache
        cache_key = self._generate_cache_key(input_data)
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            return cached_response

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        f"{self.base_url}/predict",
                        json=input_data.model_dump(mode='json')
                    )
                    response.raise_for_status()
                    result = AIGuidelinesResponse(**response.json())
                    
                    # Salva in cache
                    self._save_to_cache(cache_key, result)
                    return result

            except httpx.RequestError as e:
                last_exception = e
                print(f"[BehavioralGuidelinesAdapter] Tentativo {attempt + 1}/{self.max_retries} fallito: {e}")
                continue
            except httpx.HTTPStatusError as e:
                last_exception = e
                print(f"[BehavioralGuidelinesAdapter] Errore HTTP: {e.response.status_code}")
                # Non ritentare per errori 4xx (client error)
                if 400 <= e.response.status_code < 500:
                    raise
                continue

        # Se tutti i tentativi falliscono, solleva l'ultima eccezione
        raise last_exception or Exception("Tutti i tentativi di connessione sono falliti")

    def get_guidelines_sync(
        self, 
        input_data: AIGuidelinesInput
    ) -> AIGuidelinesResponse:
        """
        Scopo: Versione sincrona per ottenere le linee guida dall'API ML.

        Parametri:
        - input_data (AIGuidelinesInput): Dati dell'incidente per la classificazione.

        Valore di ritorno:
        - AIGuidelinesResponse: Linee guida generate dal modello ML.

        Eccezioni:
        - httpx.RequestError: Errori di rete/connessione.
        - httpx.HTTPStatusError: Risposte HTTP con status code di errore.
        """
        # Controlla cache
        cache_key = self._generate_cache_key(input_data)
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            return cached_response

        last_exception = None
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        f"{self.base_url}/predict",
                        json=input_data.model_dump(mode='json')
                    )
                    response.raise_for_status()
                    result = AIGuidelinesResponse(**response.json())
                    
                    # Salva in cache
                    self._save_to_cache(cache_key, result)
                    return result

            except httpx.RequestError as e:
                last_exception = e
                print(f"[BehavioralGuidelinesAdapter] Tentativo {attempt + 1}/{self.max_retries} fallito: {e}")
                continue
            except httpx.HTTPStatusError as e:
                last_exception = e
                print(f"[BehavioralGuidelinesAdapter] Errore HTTP: {e.response.status_code}")
                if 400 <= e.response.status_code < 500:
                    raise
                continue

        raise last_exception or Exception("Tutti i tentativi di connessione sono falliti")


    @staticmethod
    def map_severity(seriousness: str) -> SeverityLevel:
        """
        Scopo: Converte il livello di gravità RoadGuardian nel formato API ML.

        Parametri:
        - seriousness (str): Gravità nel formato RoadGuardian ('low', 'medium', 'high').

        Valore di ritorno:
        - SeverityLevel: Enum del livello di gravità nel formato API ML.

        Eccezioni:
        - None
        """
        mapping = {
            "low": SeverityLevel.LOW,
            "medium": SeverityLevel.MEDIUM,
            "high": SeverityLevel.HIGH
        }
        return mapping.get(seriousness.lower(), SeverityLevel.UNKNOWN)

    @staticmethod
    def map_incident_type(category: str) -> Optional[IncidentType]:
        """
        Scopo: Converte la categoria RoadGuardian nel tipo incidente API ML.

        Parametri:
        - category (str): Categoria nel formato RoadGuardian.

        Valore di ritorno:
        - Optional[IncidentType]: Enum del tipo incidente o None se non mappabile.

        Eccezioni:
        - None
        """
        category_lower = category.lower() if category else ""
        mapping = {
            "tamponamento": IncidentType.TAMPONAMENTO,
            "collisione con ostacolo": IncidentType.COLLISIONE_OSTACOLO,
            "collisione laterale": IncidentType.COLLISIONE_OSTACOLO,
            "veicolo fuori strada": IncidentType.VEICOLO_FUORI_STRADA,
            "investimento": IncidentType.INVESTIMENTO,
            "incendio veicolo": IncidentType.INCENDIO_VEICOLO,
            "incendio": IncidentType.INCENDIO_VEICOLO
        }
        return mapping.get(category_lower, None)

    @staticmethod
    def map_road_type(road_type_osm: str) -> RoadType:
        """
        Scopo: Converte il tipo di strada OSM nel formato API ML.

        Parametri:
        - road_type_osm (str): Tipo strada dal sistema OpenStreetMap.

        Valore di ritorno:
        - RoadType: Enum del tipo strada nel formato API ML.

        Eccezioni:
        - None
        """
        if not road_type_osm:
            return RoadType.UNCLASSIFIED
            
        road_type_lower = road_type_osm.lower()
        
        # Mapping esteso per compatibilità con output di Trasformatore_dati_segnalazione
        mapping = {
            # Autostrade e superstrade
            "motorway": RoadType.MOTORWAY_TRUNK,
            "motorway_link": RoadType.MOTORWAY_TRUNK,
            "trunk": RoadType.MOTORWAY_TRUNK,
            "trunk_link": RoadType.MOTORWAY_TRUNK,
            # Strade principali
            "primary": RoadType.PRIMARY_SECONDARY,
            "primary_link": RoadType.PRIMARY_SECONDARY,
            "secondary": RoadType.PRIMARY_SECONDARY,
            "secondary_link": RoadType.PRIMARY_SECONDARY,
            # Strade terziarie
            "tertiary": RoadType.TERTIARY,
            "tertiary_link": RoadType.TERTIARY,
            # Strade residenziali e urbane
            "residential": RoadType.RESIDENTIAL,
            "living_street": RoadType.LIVING_STREET,
            # Strade di servizio
            "service": RoadType.SERVICE,
            # Non classificate
            "unclassified": RoadType.UNCLASSIFIED,
            "unknown": RoadType.UNCLASSIFIED
        }
        return mapping.get(road_type_lower, RoadType.UNCLASSIFIED)

    @staticmethod
    def is_daylight(incident_time: time) -> bool:
        """
        Scopo: Determina se l'orario corrisponde a condizioni di luce diurna.

        Parametri:
        - incident_time (time): Orario dell'incidente.

        Valore di ritorno:
        - bool: True se l'orario è tra le 6:00 e le 20:00.

        Eccezioni:
        - None
        """
        if incident_time is None:
            return True  # Default a diurno
        
        # Considera luce diurna tra le 6:00 e le 20:00
        dawn = time(6, 0)
        dusk = time(20, 0)
        return dawn <= incident_time <= dusk

    def build_ai_input_from_incident(
        self,
        seriousness: str,
        category: str,
        incident_time: time = None,
        road_type: str = None,
        road_features: Dict[str, bool] = None
    ) -> AIGuidelinesInput:
        """
        Scopo: Costruisce l'input per l'API ML dai dati di un incidente RoadGuardian.

        Parametri:
        - seriousness (str): Livello di gravità ('low', 'medium', 'high').
        - category (str): Categoria dell'incidente.
        - incident_time (time, optional): Orario dell'incidente.
        - road_type (str, optional): Tipo di strada da OSM.
        - road_features (Dict[str, bool], optional): Caratteristiche stradali rilevate.

        Valore di ritorno:
        - AIGuidelinesInput: Input formattato per l'API ML.

        Eccezioni:
        - None
        """
        features = road_features or {}
        
        return AIGuidelinesInput(
            Severity=self.map_severity(seriousness),
            Incident_Type=self.map_incident_type(category),
            Road_Type=self.map_road_type(road_type) if road_type else RoadType.UNCLASSIFIED,
            Daylight=self._get_bool_feature(features, "Daylight", "daylight", default=self.is_daylight(incident_time)),
            Bump=self._get_bool_feature(features, "Bump", "bump"),
            Crossing=self._get_bool_feature(features, "Crossing", "crossing"),
            Give_Way=self._get_bool_feature(features, "Give_Way", "give_way"),
            Junction=self._get_bool_feature(features, "Junction", "junction"),
            Railway=self._get_bool_feature(features, "Railway", "railway"),
            Roundabout=self._get_bool_feature(features, "Roundabout", "roundabout"),
            Stop=self._get_bool_feature(features, "Stop", "stop"),
            Traffic_Signal=self._get_bool_feature(features, "Traffic_Signal", "traffic_signal"),
            Turning_Loop=self._get_bool_feature(features, "Turning_Loop", "turning_loop")
        )

    @staticmethod
    def _get_bool_feature(
        features: Dict[str, Any], 
        key_pascal: str, 
        key_snake: str, 
        default: bool = False
    ) -> bool:
        """
        Scopo: Estrae un valore booleano dal dizionario features,
        supportando sia chiavi PascalCase (output Trasformatore) che snake_case.

        Parametri:
        - features (Dict): Dizionario delle caratteristiche.
        - key_pascal (str): Chiave in formato PascalCase (es. 'Traffic_Signal').
        - key_snake (str): Chiave in formato snake_case (es. 'traffic_signal').
        - default (bool): Valore di default se chiave non trovata.

        Valore di ritorno:
        - bool: Valore della caratteristica o default.
        """
        value = features.get(key_pascal, features.get(key_snake, default))
        # Gestione valori None dal Trasformatore
        if value is None:
            return default
        return bool(value)

    def build_ai_input_from_segnalazione(
        self,
        segnalazione_input: Any,
        use_osm_data: bool = True
    ) -> AIGuidelinesInput:
        """
        Scopo: Costruisce l'input per l'API ML direttamente da un oggetto SegnalazioneInput,
        utilizzando il Trasformatore_dati_segnalazione per rilevare automaticamente
        le caratteristiche stradali da OSM.

        Parametri:
        - segnalazione_input: Oggetto SegnalazioneInput con i dati dell'incidente.
        - use_osm_data (bool): Se True, usa OSMnx per rilevare caratteristiche stradali.

        Valore di ritorno:
        - AIGuidelinesInput: Input formattato per l'API ML con dati arricchiti da OSM.

        Eccezioni:
        - ValueError: Se l'input non è valido.
        """
        if use_osm_data and TRASFORMATORE_AVAILABLE:
            try:
                # Usa il Trasformatore esistente per ottenere tutti i dati
                dati_trasformati = trasforma_dati_segnalazione(segnalazione_input)
                
                return AIGuidelinesInput(
                    Severity=self.map_severity(dati_trasformati.get("Seriousness", "high")),
                    Incident_Type=self.map_incident_type(dati_trasformati.get("Category", "")),
                    Road_Type=self.map_road_type(dati_trasformati.get("Road_Type", "")),
                    Daylight=dati_trasformati.get("Daylight", True) if dati_trasformati.get("Daylight") is not None else True,
                    Bump=bool(dati_trasformati.get("Bump", False)) if dati_trasformati.get("Bump") is not None else False,
                    Crossing=bool(dati_trasformati.get("Crossing", False)) if dati_trasformati.get("Crossing") is not None else False,
                    Give_Way=bool(dati_trasformati.get("Give_Way", False)) if dati_trasformati.get("Give_Way") is not None else False,
                    Junction=bool(dati_trasformati.get("Junction", False)) if dati_trasformati.get("Junction") is not None else False,
                    Railway=bool(dati_trasformati.get("Railway", False)) if dati_trasformati.get("Railway") is not None else False,
                    Roundabout=bool(dati_trasformati.get("Roundabout", False)) if dati_trasformati.get("Roundabout") is not None else False,
                    Stop=bool(dati_trasformati.get("Stop", False)) if dati_trasformati.get("Stop") is not None else False,
                    Traffic_Signal=bool(dati_trasformati.get("Traffic_Signal", False)) if dati_trasformati.get("Traffic_Signal") is not None else False,
                    Turning_Loop=bool(dati_trasformati.get("Turning_Loop", False)) if dati_trasformati.get("Turning_Loop") is not None else False
                )
            except Exception as e:
                print(f"[BehavioralGuidelinesAdapter] Errore Trasformatore, uso fallback manuale: {e}")
        
        # Fallback: costruzione manuale senza dati OSM
        incident_time_value = None
        if hasattr(segnalazione_input, 'incident_time'):
            incident_time_value = segnalazione_input.incident_time
            
        return self.build_ai_input_from_incident(
            seriousness=getattr(segnalazione_input, 'seriousness', 'high'),
            category=getattr(segnalazione_input, 'category', ''),
            incident_time=incident_time_value,
            road_type=None,
            road_features=None
        )

    async def get_protocols(self) -> Dict[str, Any]:
        """
        Scopo: Recupera il dizionario completo dei protocolli disponibili.

        Parametri:
        - Nessuno.

        Valore di ritorno:
        - Dict[str, Any]: Dizionario dei protocolli dall'API ML.

        Eccezioni:
        - httpx.RequestError: Errori di rete/connessione.
        - httpx.HTTPStatusError: Risposte HTTP con status code di errore.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/protocols")
            response.raise_for_status()
            return response.json()

    def get_protocols_sync(self) -> Dict[str, Any]:
        """
        Scopo: Versione sincrona per recuperare i protocolli disponibili.

        Parametri:
        - Nessuno.

        Valore di ritorno:
        - Dict[str, Any]: Dizionario dei protocolli dall'API ML.

        Eccezioni:
        - httpx.RequestError: Errori di rete/connessione.
        - httpx.HTTPStatusError: Risposte HTTP con status code di errore.
        """
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(f"{self.base_url}/protocols")
            response.raise_for_status()
            return response.json()

    def clear_cache(self) -> None:
        """
        Scopo: Svuota la cache delle risposte.

        Parametri:
        - Nessuno.

        Valore di ritorno:
        - None

        Eccezioni:
        - None
        """
        self._cache.clear()


# Singleton globale dell'adapter (opzionale, per riuso)
_adapter_instance: Optional[BehavioralGuidelinesAdapter] = None


def get_guidelines_adapter() -> BehavioralGuidelinesAdapter:
    """
    Scopo: Restituisce un'istanza singleton dell'adapter.

    Parametri:
    - Nessuno.

    Valore di ritorno:
    - BehavioralGuidelinesAdapter: Istanza condivisa dell'adapter.

    Eccezioni:
    - None
    """
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = BehavioralGuidelinesAdapter()
    return _adapter_instance
