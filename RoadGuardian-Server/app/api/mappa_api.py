from fastapi import APIRouter, Depends, Query, BackgroundTasks
from typing import List, Optional
from services.mappa_service import MappaService # Assumendo che esista
from schemas.mappa_schema import SegnalazioneMapDTO, UserPositionUpdate
from db.connection import get_database # Assumendo che esista

router = APIRouter(prefix="/mappa", tags=["Gestione Mappa"])

def get_mappa_service(db=Depends(get_database)):
    """
    Scopo: Fornisce un'istanza di `MappaService` tramite Dependency Injection.

    Parametri:
    - db: Connessione/handle al database risolta da FastAPI.

    Valore di ritorno:
    - MappaService: Service configurato per la gestione mappa.

    Eccezioni:
    - Exception: Errori di inizializzazione del service.
    """
    # La MappaService deve gestire la logica di business e l'interazione con il ControllerDBFacade (vedi ODD)
    return MappaService(db)

# --- Endpoint 1: Visualizzazione Mappa e Segnalazioni Attive (RF_03, RF_13) ---
@router.get("/segnalazioni/attive", response_model=List[SegnalazioneMapDTO])
def get_active_incidents(
    service: MappaService = Depends(get_mappa_service)
):
    """
    Scopo: Restituisce le segnalazioni attive in formato `SegnalazioneMapDTO`.

    Parametri:
    - service (MappaService): Service che incapsula la logica applicativa.

    Valore di ritorno:
    - List[SegnalazioneMapDTO]: Lista di segnalazioni attive.

    Eccezioni:
    - HTTPException: Errori di business tradotti in HTTP se sollevati dal service.
    """
    return service.get_active_incidents()

# --- Endpoint 2: Filtraggio per Tipo (RF_18) ---
@router.get("/segnalazioni/filtrate", response_model=List[SegnalazioneMapDTO])
def get_filtered_incidents(
    tipi_incidente: Optional[List[str]] = Query(None, description="Lista dei tipi di incidente su cui filtrare"),
    service: MappaService = Depends(get_mappa_service)
):
    """
    Scopo: Filtra e restituisce segnalazioni attive per categorie specificate.

    Parametri:
    - tipi_incidente (Optional[List[str]]): Categorie da includere nel risultato.
    - service (MappaService): Service applicativo.

    Valore di ritorno:
    - List[SegnalazioneMapDTO]: Lista di segnalazioni filtrate.

    Eccezioni:
    - HTTPException: Eventuali errori di validazione o business dal service.
    """
    return service.get_filtered_incidents(tipi_incidente)

# --- Endpoint 3: Aggiornamento Posizione Utente (RF_XX) ---
@router.post("/posizione", status_code=200)
def update_user_position(
    payload: UserPositionUpdate,
    background_tasks: BackgroundTasks,
    service: MappaService = Depends(get_mappa_service)
):
    """
    Scopo: Accetta aggiornamenti di posizione e avvia controllo di prossimità in background.

    Parametri:
    - payload (UserPositionUpdate): Posizione e token FCM dell'utente.
    - background_tasks (BackgroundTasks): Coda di esecuzione non bloccante.
    - service (MappaService): Service applicativo.

    Valore di ritorno:
    - dict: Messaggio di conferma aggiornamento posizione.

    Eccezioni:
    - HTTPException: Errori di validazione o esecuzione.
    """
    # Eseguiamo la logica di controllo prossimità in background per non bloccare la risposta
    background_tasks.add_task(service.process_user_position, payload)
    return {"message": "Posizione aggiornata"}

"""--- Endpoint 4: Classificazione per Numero di Segnalazioni (RF_14) ---
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
