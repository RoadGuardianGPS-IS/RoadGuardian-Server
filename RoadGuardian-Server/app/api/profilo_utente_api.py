from fastapi import APIRouter, Depends, Query, status
from services.profilo_utente_service import ProfiloUtenteService
from models.user_model import UserCreateInput, UserModelDTO, UserUpdateInput
from db.connection import get_database

router = APIRouter(prefix="/profilo", tags=["Profilo Utente"])


def get_profilo_service(db=Depends(get_database)):
    """Factory method per Dependency Injection del Service"""
    return ProfiloUtenteService(db)


@router.post("/", response_model=UserModelDTO, status_code=status.HTTP_201_CREATED)
def create_new_user(
        input_payload: UserCreateInput,
        service: ProfiloUtenteService = Depends(get_profilo_service)
):
    """
    Scopo: Endpoint per la registrazione di un nuovo utente nel sistema.

    Parametri Input:
    - input_payload (JSON Body): Dati di registrazione (Nome, Cognome, Email, Tel, Password).

    Valore di Ritorno:
    - JSON (UserModelDTO): I dati dell'utente creato (esclusa password).

    Gestione Errori:
    - 400 Bad Request: Se l'email esiste giÃ  o i dati non rispettano i formati regex.
    - 422 Validation Error: Errore automatico di Pydantic sui tipi/vincoli.
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
    Scopo: Modifica i dati anagrafici di un utente specifico.

    Parametri Input:
    - user_id (Path Param): ID dell'utente.
    - input_payload (JSON Body): Campi da modificare (opzionali).

    Valore di Ritorno:
    - JSON (UserModelDTO): Utente aggiornato.

    Gestione Errori:
    - 404 Not Found: Utente inesistente.
    """
    return service.update_user_profile(user_id, input_payload)