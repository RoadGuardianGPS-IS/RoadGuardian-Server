from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from services.segnalazione_service import SegnalazioneService # Assumendo che esista
from models.segnalazione_model import SegnalazioneManualeInput, SegnalazioneOutputDTO, SegnalazioneStatoUpdate
from models.user_model import PosizioneGPS # Re-utilizzando il modello per la posizione
from db.connection import get_database # Assumendo che esista

router = APIRouter(prefix="/segnalazione", tags=["Gestione Segnalazioni"])

def get_segnalazione_service(db=Depends(get_database)):
    """Factory method per Dependency Injection del Service"""
    # La SegnalazioneService deve gestire la logica di business e l'interazione con il ControllerDBFacade
    return SegnalazioneService(db)

# --- Endpoint 1: Segnalazione Manuale (RF_02) ---
@router.post("/manuale/{user_id}", response_model=SegnalazioneOutputDTO, status_code=status.HTTP_201_CREATED)
def create_manual_report(
    user_id: str,
    input_payload: SegnalazioneManualeInput,
    service: SegnalazioneService = Depends(get_segnalazione_service)
):
    """
    Scopo: Endpoint per l'invio di una segnalazione manuale completa (Gravità, Descrizione, Media).

    Parametri Input:
    - user_id (Path Param): ID dell'utente registrato che segnala.
    - input_payload (JSON Body): Dati della segnalazione (Gravità, Descrizione, Media Opzionale per RF_19).

    Valore di Ritorno:
    - JSON (SegnalazioneOutputDTO): Dati della segnalazione creata.

    Gestione Errori:
    - 400 Bad Request: Se dati mancanti (es. Gravità) o non validi.
    - 401 Unauthorized: Utente non loggato/autorizzato.
    """
    # Il service si occuperà di aggiungere GPS, data/ora e attivare le notifiche push
    return service.create_manual_report(user_id, input_payload)

# --- Endpoint 2: Segnalazione Veloce (RF_10, RF_15 (FlashLight)) ---
@router.post("/veloce/{user_id}", response_model=SegnalazioneOutputDTO, status_code=status.HTTP_201_CREATED)
def create_quick_report(
    user_id: str,
    user_location: PosizioneGPS = Depends(), # La posizione è essenziale, ottenuta lato client
    is_night_time: Optional[bool] = Query(False, description="True se la segnalazione avviene di notte per FlashLight"),
    service: SegnalazioneService = Depends(get_segnalazione_service)
):
    """
    Scopo: Endpoint per l'invio di una segnalazione veloce tramite tasti rapidi.

    Parametri Input:
    - user_id (Path Param): ID dell'utente registrato.
    - user_location (Query Params): Posizione GPS attuale.
    - is_night_time (Query Param): Indica se l'invio è avvenuto in fasce orarie serali (per FlashLight).

    Valore di Ritorno:
    - JSON (SegnalazioneOutputDTO): Dati della segnalazione creata (priorità alta, no descrizione).

    Gestione Errori:
    - 400 Bad Request: GPS non disponibile.
    - 401 Unauthorized: Utente non loggato/autorizzato.
    """
    # Il service gestisce il timer di 30 secondi e la creazione con priorità alta (Main Scenario UC_10_RC)
    return service.create_quick_report(user_id, user_location, is_night_time)

# --- Endpoint 3: Segnalazione Offline (RF_09) ---
@router.post("/offline/{user_id}", response_model=SegnalazioneOutputDTO, status_code=status.HTTP_201_CREATED)
def submit_offline_report(
    user_id: str,
    input_payload: SegnalazioneManualeInput, # I dati vengono memorizzati e inviati completi
    service: SegnalazioneService = Depends(get_segnalazione_service)
):
    """
    Scopo: Endpoint per convalidare e registrare una segnalazione inviata offline, al momento dello status online.

    Parametri Input:
    - user_id (Path Param): ID dell'utente.
    - input_payload (JSON Body): Dati della segnalazione (con dati GPS e timestamp memorizzati offline).

    Valore di Ritorno:
    - JSON (SegnalazioneOutputDTO): Dati della segnalazione registrata.

    Gestione Errori:
    - 400 Bad Request: Dati non validi o GPS/Timestamp assenti.
    """
    return service.validate_and_register_offline_report(user_id, input_payload)

# --- Endpoint 4: Notifica Contatti Preferiti (RF_17) ---
@router.post("/notifica-contatti/{user_id}/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
def notify_emergency_contacts(
    user_id: str,
    incident_id: str,
    service: SegnalazioneService = Depends(get_segnalazione_service)
):
    """
    Scopo: Endpoint per notificare i contatti preferiti dell'utente in caso di incidente ad alto rischio.
           Questo è chiamato automaticamente dal sistema dopo una Segnalazione Veloce.

    Parametri Input:
    - user_id (Path Param): ID dell'utente segnalante.
    - incident_id (Path Param): ID della segnalazione.

    Valore di Ritorno:
    - Nessun Contenuto (204 No Content).

    Gestione Errori:
    - 404 Not Found: Utente o Incidente inesistente.
    """
    return service.notify_preferred_contacts(user_id, incident_id)


# --- Endpoint 5: Aggiornamento Stato Segnalazione (RF_20) ---
@router.put("/stato/{incident_id}", response_model=SegnalazioneOutputDTO)
def update_report_status(
    incident_id: str,
    input_payload: SegnalazioneStatoUpdate,
    service: SegnalazioneService = Depends(get_segnalazione_service)
):
    """
    Scopo: Endpoint per aggiornare lo stato di una segnalazione (es. 'ricevuta', 'risolta').
           (Presumibilmente usato da personale autorizzato/sistema backend, non dal client utente finale).

    Parametri Input:
    - incident_id (Path Param): ID della segnalazione da aggiornare.
    - input_payload (JSON Body): Nuovo stato della segnalazione.

    Valore di Ritorno:
    - JSON (SegnalazioneOutputDTO): La segnalazione aggiornata.

    Gestione Errori:
    - 401 Unauthorized: Utente non autorizzato (es. non il gestore del servizio).
    - 404 Not Found: Incidente inesistente.
    """
    return service.update_incident_status(incident_id, input_payload)