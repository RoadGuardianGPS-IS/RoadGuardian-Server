from fastapi import APIRouter, Depends, status
from schemas.segnalazione_schema import SegnalazioneInput, SegnalazioneOutputDTO
from db.connection import get_database
from services.segnalazione_service import SegnalazioneService

router = APIRouter(
    prefix="/segnalazione",
    tags=["Gestione Segnalazioni"]
)


def get_segnalazione_service(db=Depends(get_database)):
    """
    Scopo: Fornisce un'istanza di `SegnalazioneService` tramite Dependency Injection.

    Parametri:
    - db: Handle della connessione al database risolta da FastAPI.

    Valore di ritorno:
    - SegnalazioneService: Service per gestione segnalazioni.

    Eccezioni:
    - Exception: Errori di inizializzazione del service.
    """
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
    service:SegnalazioneService=Depends(get_segnalazione_service)
):
    """
    Scopo: Crea una segnalazione manuale e restituisce i dati risultanti.

    Parametri:
    - user_id (str): Identificativo utente (path).
    - input_payload (SegnalazioneInput): Dati della segnalazione (body).
    - service (SegnalazioneService): Service applicativo.

    Valore di ritorno:
    - SegnalazioneOutputDTO: Dati della segnalazione creata.

    Eccezioni:
    - HTTPException: Errori di validazione o autorizzazione tradotti in HTTP.
    """
    # Il service si occuperà di controllare la presenza di GPS, data/ora e eventualmente inserirle se non presenti
    return service.create_report(user_id, input_payload)


#  Visualizzazione Dettagli Incidente (RF_06) ---
@router.get("/dettagli/{incident_id}", response_model=SegnalazioneOutputDTO)
def get_incident_details(
    incident_id: str,
    service:SegnalazioneService=Depends(get_segnalazione_service)
):
    """
    Scopo: Restituisce i dettagli di una segnalazione attiva dato l'ID.

    Parametri:
    - incident_id (str): Identificativo della segnalazione (path).
    - service (SegnalazioneService): Service applicativo.

    Valore di ritorno:
    - SegnalazioneOutputDTO: Dati dettagliati della segnalazione.

    Eccezioni:
    - HTTPException: 404 se la segnalazione non esiste/attiva.
    """
    return service.get_segnalazione_details(incident_id)

#  Visualizzazione Linee Guida (RF_05, RF_16) ---
@router.get("/lineeguida/{incident_id}", response_model=str) # Assumendo che le linee guida siano una stringa per semplicità
def get_incident_guidelines(
    incident_id: str,
    service:SegnalazioneService=Depends(get_segnalazione_service)
 ):
    """
    Scopo: Restituisce linee guida operative per l'incidente specificato.

    Parametri:
    - incident_id (str): Identificativo della segnalazione (path).
    - service (SegnalazioneService): Service applicativo.

    Valore di ritorno:
    - str: Testo delle linee guida.

    Eccezioni:
    - HTTPException: 404 se segnalazione inesistente o non attiva.
    """
    return service.get_guidelines_for_incident(incident_id)


@router.delete("/{incident_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    incident_id: str,
    service:SegnalazioneService=Depends(get_segnalazione_service)
):
    """
    Scopo: Elimina/disattiva una segnalazione indicata dal suo ID.

    Parametri:
    - incident_id (str): Identificativo della segnalazione (path).
    - service (SegnalazioneService): Service applicativo.

    Valore di ritorno:
    - None: Risposta HTTP 204 senza contenuto.

    Eccezioni:
    - HTTPException: 404 se incidente inesistente.
    """
    service.delete_segnalazione(incident_id)


@router.post(
    "/createsegnalazioneveloce/{user_id}",
    response_model=SegnalazioneOutputDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Segnalazione Veloce (RF_10)"
)

def create_fast_report(
    user_id: str,
    input_payload: SegnalazioneInput,
    service:SegnalazioneService=Depends(get_segnalazione_service)
):
    """
    Scopo: Crea una segnalazione veloce e restituisce l'output standardizzato.

    Parametri:
    - user_id (str): Identificativo utente (path).
    - input_payload (SegnalazioneInput): Dati minimi della segnalazione (body).
    - service (SegnalazioneService): Service applicativo.

    Valore di ritorno:
    - SegnalazioneOutputDTO: Dati della segnalazione creata.

    Eccezioni:
    - HTTPException: Errori di validazione o autorizzazione tradotti in HTTP.
    """
    # Il service si occuperà di controllare la presenza di GPS, data/ora e eventualmente inserirle se non presenti
    return service.create_fast_report(user_id, input_payload)
