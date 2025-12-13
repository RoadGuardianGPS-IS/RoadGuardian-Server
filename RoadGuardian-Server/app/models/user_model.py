from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from pydantic_extra_types.phone_numbers import PhoneNumber

class UserModel(BaseModel):
    """Modello utente interno che mappa un documento utente nel DB Mongo.

    Descrizione: Rappresenta i campi dell'utente salvati in MongoDB.
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
        """Configurazione Pydantic per serializzazione e esempio.

        Scopo: Abilitare `populate_by_name` e fornire esempio JSON per lo schema.
        Parametri: Nessuno (modifica comportamento di Pydantic internamente).
        Valore di ritorno: None.
        Eccezioni: Nessuna.
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
    """DTO di output utente (esclude la password) destinato al client.

    Descrizione: Espone solo i campi pubblici di un utente per risposte API.
    """
    id: Optional[str] = Field(default=None, alias="_id") 
    email: EmailStr #forse da implementare in schema
    first_name: str
    last_name: str
    num_tel: PhoneNumber #forse da implementare in schema
    is_active: bool = True #account attivo o eliminato
    role: str = "user" #user o admin

    model_config = ConfigDict(populate_by_name = True)

class UserModelChangeDTO(BaseModel):
    """DTO per aggiornamenti parziali o cancellazione logica dell'utente.

    Descrizione: Campi opzionali usati per modifiche del profilo utente.
    """
    email: Optional[EmailStr] #forse da implementare in schema
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]
    num_tel: Optional[PhoneNumber] #forse da implementare in schema
    is_active: Optional[bool] = True #account attivo o eliminato
    role: str = "user" #user o admin

    model_config = ConfigDict(populate_by_name = True)