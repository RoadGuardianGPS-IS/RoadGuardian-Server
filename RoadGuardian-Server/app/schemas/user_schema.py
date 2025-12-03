from pydantic import BaseModel, EmailStr, Field, SecretStr
from pydantic_extra_types.phone_numbers import PhoneNumber

class EmailUpdateSchema(BaseModel):
    new_email: EmailStr

class PhoneUpdateSchema(BaseModel):
    new_phone: PhoneNumber

class PasswordUpdateSchema(BaseModel):
    new_password: SecretStr = Field #secretStr nasconde la password nei log