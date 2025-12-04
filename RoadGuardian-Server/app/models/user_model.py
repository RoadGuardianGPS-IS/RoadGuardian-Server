from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from pydantic_extra_types.phone_numbers import PhoneNumber

class UserModel(BaseModel):
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
    """Classe per output utente al client senza password"""
    id: Optional[str] = Field(default=None, alias="_id") 
    email: EmailStr #forse da implementare in schema
    first_name: str
    last_name: str
    num_tel: PhoneNumber #forse da implementare in schema
    is_active: bool = True #account attivo o eliminato
    role: str = "user" #user o admin

    model_config = ConfigDict(populate_by_name = True)

class UserModelChangeDTO(BaseModel):
    """Classe per modifica e cancellazione utente"""
    email: Optional[EmailStr] #forse da implementare in schema
    first_name: Optional[str]
    last_name: Optional[str]
    password: Optional[str]
    num_tel: Optional[PhoneNumber] #forse da implementare in schema
    is_active: Optional[bool] = True #account attivo o eliminato
    role: str = "user" #user o admin

    model_config = ConfigDict(populate_by_name = True)


class UserCreateInput(BaseModel):
    """Modello per la crezione (Input dal client - tutti obbligatori)"""
    first_name: str
    last_name: str
    email: EmailStr
    password: str  # Password in chiaro inserita dall'utente
    num_tel: PhoneNumber


class UserUpdateInput(BaseModel):
    """Modello per l'AGGIORNAMENTO (Input dal client - tutti opzionali)"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    num_tel: Optional[PhoneNumber] = None