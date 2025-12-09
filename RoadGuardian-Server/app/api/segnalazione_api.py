from fastapi import APIRouter, Depends, status
from app.schemas.segnalazione_schema import (SegnalazioneInput,SegnalazioneOutputDTO)
from app.db.connection import get_database

router = APIRouter(
    prefix="/segnalazione",
    tags=["Gestione Segnalazioni"]
)


def get_segnalazione_service(db=Depends(get_database)):
    """Factory method per Dependency Injection del Service"""
    from app.services.segnalazione_service import SegnalazioneService
    return SegnalazioneService(db)


@router.post(
    "/creasegnalazione/{user_id}",
    response_model=SegnalazioneOutputDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Segnalazione Manuale (RF_02)"
)
def create_report(
    user_id: str,
    input_payload: SegnalazioneInput,
    service=Depends(get_segnalazione_service)
):
    """
    Scopo: Endpoint per l'invio di una segnalazione manuale completa.
    
    Parametri Input:
    - user_id (Path Param): ID dell'utente registrato che segnala.
    - input_payload (JSON Body): Dati della segnalazione (data, ora, coordinate GPS, gravità, categoria, descrizione, immagine).
    
    Valore di Ritorno:
    - JSON (SegnalazioneOutputDTO): Dati della segnalazione creata.
    
    Gestione Errori:
    - 400 Bad Request: Se dati mancanti o non validi.
    - 401 Unauthorized: Utente non loggato/autorizzato.
    """
    # Il service si occuperà di controllare la presenza di GPS, data/ora e eventualmente inserirle se non presenti
    return service.create_report(user_id, input_payload)


#  Visualizzazione Dettagli Incidente (RF_06) ---
@router.get("/dettagli/{incident_id}", response_model=SegnalazioneOutputDTO)
def get_incident_details(
    incident_id: str,
    service: MappaService = Depends(get_mappa_service)
):
    """
    Scopo: Endpoint per visualizzare tutti i dettagli di una specifica segnalazione di incidente.

    Parametri Input:
    - incident_id (Path Param): ID univoco della segnalazione.

    Valore di Ritorno:
    - JSON (SegnalazioneMapDTO): Oggetto completo con tutti i dettagli (descrizione, gravità, coordinate, ecc.).

    Gestione Errori:
    - 404 Not Found: Segnalazione non esistente o risolta.
    """
    return service.get_incident_details(incident_id)

#  Visualizzazione Linee Guida (RF_05, RF_16) ---
@router.get("/lineeguida/{incident_id}", response_model=str) # Assumendo che le linee guida siano una stringa per semplicità
def get_incident_guidelines(
    incident_id: str,
    service: MappaService = Depends(get_mappa_service)
):
    """
    Scopo: Endpoint per visualizzare le linee guida comportamentali (anche AI) per un incidente specifico.

    Parametri Input:
    - incident_id (Path Param): ID univoco della segnalazione.

    Valore di Ritorno:
    - String: Linee guida comportamentali appropriate al tipo di incidente.

    Gestione Errori:
    - 404 Not Found: Incidente non esistente o linee guida non disponibili.
    """
    return service.get_guidelines_for_incident(incident_id)


@router.delete("/{incident_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    incident_id: str,
    service=Depends(get_segnalazione_service)
):
    """
    Scopo: Endpoint per eliminare una segnalazione dal sistema.
    
    Parametri Input:
    - incident_id (Path Param): ID della segnalazione da eliminare.
    
    Valore di Ritorno:
    - Nessun Contenuto (204 No Content).
    
    Gestione Errori:
    - 404 Not Found: Incidente inesistente.
    """
    service.delete_segnalazione(incident_id)