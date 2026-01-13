from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from pydantic_extra_types.phone_numbers import PhoneNumber
class UserCreateInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    num_tel: Optional[str]
class UserModel(BaseModel):
    """
    Scopo: Modello utente interno che mappa un documento utente nel DB Mongo.

    Parametri:
    - id (Optional[str]): Identificativo univoco (alias _id).
    - email (EmailStr): Indirizzo email dell'utente.
    - first_name (str): Nome dell'utente.
    - last_name (str): Cognome dell'utente.
    - password (str): Password hashata.
    - num_tel (PhoneNumber): Numero di telefono.
    - is_active (bool): Flag stato account (default True).
    - role (str): Ruolo utente (default "user").

    Valore di ritorno:
    - UserModel: Istanza del modello per persistenza.

    Eccezioni:
    - ValidationError: Se i dati non rispettano il tipo atteso.
    """
    # Field(alias="_id") permette di mappare il campo '_id' di Mongo su 'id' di Pydantic
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr #forse da implementare in schema
    first_name: str
    last_name: str
    password: str
    # hash_password da inserire in user_schema.py
    num_tel: PhoneNumber #forse da implementare in schema
    is_active: bool = True #account attivo o eliminato
    role: str = "user" #user o admin

    class Config: #classe per creare admin, scritta come esempio
        """
        Scopo: Configurazione Pydantic per serializzazione e esempio.

        Parametri:
        - Nessuno (modifica comportamento di Pydantic internamente).

        Valore di ritorno:
        - None.

        Eccezioni:
        - Nessuna.
        """
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "email": "mario.rossi@example.com",
                "first_name": "Mario",
                "last_name": "Rossi",
                "password" : "password",
                "num_tel": "+393332984046",
                "role": "admin"
            }
        }

class UserModelDTO(BaseModel):
    """
    Scopo: DTO di output utente (esclude la password) destinato al client.

    Parametri:
    - id (Optional[str]): Identificativo univoco.
    - email (EmailStr): Email utente.
    - first_name (str): Nome.
    - last_name (str): Cognome.
    - num_tel (str): Numero di telefono.
    - is_active (bool): Stato account.
    - role (str): Ruolo.

    Valore di ritorno:
    - UserModelDTO: Oggetto per risposta API.

    Eccezioni:
    - ValidationError: Se i dati non sono validi.
    """
    id: Optional[str] = Field(default=None, alias="_id") 
    email: EmailStr #forse da implementare in schema
    first_name: str
    last_name: str
    num_tel: str 
    is_active: bool = True #account attivo o eliminato
    role: str = "user" #user o admin

    model_config = ConfigDict(populate_by_name = True)

class UserModelChangeDTO(BaseModel):
    """
    Scopo: DTO per aggiornamenti parziali o cancellazione logica dell'utente.

    Parametri:
    - email (Optional[EmailStr]): Nuova email.
    - first_name (Optional[str]): Nuovo nome.
    - last_name (Optional[str]): Nuovo cognome.
    - password (Optional[str]): Nuova password.
    - num_tel (Optional[PhoneNumber]): Nuovo telefono.
    - is_active (Optional[bool]): Nuovo stato.
    - role (str): Ruolo (default "user").

    Valore di ritorno:
    - UserModelChangeDTO: Oggetto per aggiornamento.

    Eccezioni:
    - ValidationError: Se i dati non sono validi.
    """
    email: Optional[EmailStr] #forse da implementare in schema
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]
    num_tel: Optional[PhoneNumber] #forse da implementare in schema
    is_active: Optional[bool] = True #account attivo o eliminato
    role: str = "user" #user o admin

    model_config = ConfigDict(populate_by_name = True)