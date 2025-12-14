from fastapi import APIRouter, Depends, Query, status
from services.profilo_utente_service import ProfiloUtenteService
from models.user_model import UserModelDTO
from schemas.user_schema import UserUpdateInput, UserCreateInput
from db.connection import get_database

router = APIRouter(prefix="/profilo", tags=["Profilo Utente"])


def get_profilo_service(db=Depends(get_database)):
    """
    Scopo: Fornisce un'istanza di `ProfiloUtenteService` tramite Dependency Injection.

    Parametri:
    - db: Handle/connessione al database fornita da FastAPI.

    Valore di ritorno:
    - ProfiloUtenteService: Service per gestione profilo utente.

    Eccezioni:
    - Exception: Errori di inizializzazione del service.
    """
    return ProfiloUtenteService(db)


@router.post("/", response_model=UserModelDTO, status_code=status.HTTP_201_CREATED)
def create_new_user(
        input_payload: UserCreateInput,
        service: ProfiloUtenteService = Depends(get_profilo_service)
):
    """
    Scopo: Registra un nuovo utente e restituisce i dati pubblici dell'account.

    Parametri:
    - input_payload (UserCreateInput): Dati anagrafici e password.
    - service (ProfiloUtenteService): Service applicativo.

    Valore di ritorno:
    - UserModelDTO: Utente creato (senza password).

    Eccezioni:
    - HTTPException: 400/422 per errori di validazione o email duplicata.
    """
    return service.create_user_profile(input_payload)


"""@router.get("/sync", response_model=List[UserOutputDTO])
def sync_user_data(
        last_sync: datetime = Query(..., description="Timestamp ISO 8601 (es. 2023-10-21T10:00:00)"),
        service: ProfiloUtenteService = Depends(get_profilo_service)
):
    
    Scopo: Fornisce al Client Mobile (Fat Client) solo i dati modificati dall'ultima sincronizzazione.

    Parametri Input:
    - last_sync (Query Param): Data dell'ultimo aggiornamento locale del client.

    Valore di Ritorno:
    - JSON List: Lista di oggetti utente modificati o cancellati (soft delete).
    
    return service.get_user_updates_since(last_sync)
"""

@router.put("/{user_id}", response_model=UserModelDTO)
def update_existing_user(
        user_id: str,
        input_payload: UserUpdateInput, 
        service: ProfiloUtenteService = Depends(get_profilo_service)
):
    """
    Scopo: Aggiorna selettivamente i dati anagrafici dell'utente.

    Parametri:
    - user_id (str): Identificativo dell'utente (path).
    - input_payload (UserUpdateInput): Campi opzionali da aggiornare (body).
    - service (ProfiloUtenteService): Service applicativo.

    Valore di ritorno:
    - UserModelDTO: Dati aggiornati dell'utente.

    Eccezioni:
    - HTTPException: 404 se l'utente non esiste.
    """
    return service.update_user_profile(user_id, input_payload)

@router.post("/login", response_model=UserModelDTO)
def login(
        input_payload: UserUpdateInput,
        service: ProfiloUtenteService = Depends(get_profilo_service)
):
    """
    Scopo: Autentica l'utente e restituisce i dati di profilo.

    Parametri:
    - input_payload (UserUpdateInput): Credenziali (email, password).
    - service (ProfiloUtenteService): Service applicativo.

    Valore di ritorno:
    - UserModelDTO: Dati dell'utente autenticato.

    Eccezioni:
    - HTTPException: 401 per credenziali errate.
    """
    return service.login_user(input_payload)

@router.post("/delete/{user_id}", response_model=str)
def delete_account(
        input_payload: UserUpdateInput,
        service: ProfiloUtenteService = Depends(get_profilo_service)
):
    """
    Scopo: Disattiva/elimina l'account utente indicato.

    Parametri:
    - input_payload (UserUpdateInput): Dati necessari all'operazione.
    - service (ProfiloUtenteService): Service applicativo.

    Valore di ritorno:
    - str: Messaggio di conferma.

    Eccezioni:
    - HTTPException: 404 se utente inesistente.
    """
    return service.delete_user_profile(input_payload)