from pydantic import BaseModel, EmailStr, Field
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