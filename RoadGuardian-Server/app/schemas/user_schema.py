import re
from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, SecretStr, field_validator


# --- VALIDATORI ---

class Validators:
    """
    Centralizza tutti i validatori condivisi per password e telefono (max 100 car).
    Utilizzata da schema di registrazione e aggiornamento per coerenza.
    """
    
    @staticmethod
    def validatePasswordComplexity(v: str) -> str:
        """
        Scopo: Verifica la complessità della password secondo policy di sicurezza.

        Parametri:
        - v (str): Password in chiaro da validare.

        Valore di ritorno:
        - str: La password validata (invariata).

        Eccezioni:
        - ValueError: Se non rispetta uno dei vincoli di complessità.

        Vincoli Input:
        - Lunghezza: 8-25 caratteri
        - Almeno una maiuscola (A-Z)
        - Almeno una minuscola (a-z)
        - Almeno un numero (0-9)
        - Almeno un carattere speciale (!@#$%^&*()_+-=[]{};\\':\"|,./?")
        """
        # Validazione lunghezza
        if not (8 <= len(v) <= 25):
            raise ValueError('Lunghezza deve essere tra 8 e 25 caratteri.')
        
        # Validazione complessità
        if not re.search(r"[A-Z]", v):
            raise ValueError('Deve contenere almeno una lettera maiuscola.')
        if not re.search(r"[a-z]", v):
            raise ValueError('Deve contenere almeno una lettera minuscola.')
        if not re.search(r"\d", v):
            raise ValueError('Deve contenere almeno un numero.')
        if not re.search(r"[ !@#$%^&*()_+\-\=\[\]{};':\"\\|,./?]", v):
            raise ValueError('Deve contenere almeno un carattere speciale.')
        
        return v
    
    @staticmethod
    def validatePhoneNumber(v: str) -> str:
        """
        Scopo: Valida e normalizza un numero di telefono italiano con prefisso.

        Parametri:
        - v (str): Numero di telefono in input. Accetta:
            - Nazionale: '3331234567', '0212345678'
            - Internazionale: '+393331234567'
            - Con spazi/trattini: '+39 333 123 4567', '+39-333-1234567'

        Valore di ritorno:
        - str: Numero normalizzato con prefisso '+39'. Esempio: '+393331234567'

        Eccezioni:
        - ValueError: Se numero non è italiano valido (prefisso errato, lunghezza, tipo).

        Vincoli Input:
        - Lunghezza: 9-10 cifre dopo prefisso
        - Charset: 0-9, spazi, trattini
        - Tipo: Fisso (09) o Mobile (3xx)
        """
        phone_clean = v.replace(" ", "").replace("-", "")
        
        # Gestione prefisso: internazionale o nazionale
        if phone_clean.startswith("+"):
            if not phone_clean.startswith("+39"):
                raise ValueError("Numero telefonico non italiano. Prefisso internazionale deve essere '+39'.")
            phone_digits = phone_clean[3:]
        elif phone_clean.startswith("0"):
            phone_digits = phone_clean[1:]
        else:
            phone_digits = phone_clean
        
        # Validazione charset (solo cifre)
        if not phone_digits.isdigit():
            raise ValueError("Numero telefonico contiene caratteri non validi. Consentite solo cifre, spazi, trattini.")
        
        # Validazione lunghezza (9-10 cifre)
        if not (9 <= len(phone_digits) <= 10):
            raise ValueError(f"Lunghezza non valida. Ricevute {len(phone_digits)} cifre, attese 9-10.")
        
        # Validazione tipo (fisso 09 o mobile 3xx)
        if not (phone_digits.startswith("09") or phone_digits.startswith("3")):
            raise ValueError("Numero non riconosciuto come italiano. Fissi: 09xx, Mobili: 3xx.")
        
        return "+39" + phone_digits


# --- UPDATE SCHEMAS ---

class EmailUpdateSchema(BaseModel):
    """
    Schema di Input per l'aggiornamento dell'email.
    
    Validazione: L'email deve essere in formato RFC 5322 valido.
    """
    new_email: EmailStr = Field(
        ...,
        title="Nuova Email",
        description="Indirizzo email valido. Deve essere univoco nel sistema."
    )


class PhoneUpdateSchema(BaseModel):
    """Schema di Input per l'aggiornamento del numero di telefono italiano (max 80 car)."""
    new_phone: str = Field(..., title="Nuovo Numero Telefono", description="Telefono italiano.")
    
    @field_validator('new_phone')
    def validateNewPhone(cls, v: str) -> str:
        """
        Scopo: Valida e normalizza il numero di telefono per l'aggiornamento.

        Parametri:
        - v (str): Numero di telefono in input.

        Valore di ritorno:
        - str: Numero normalizzato con prefisso '+39'.

        Eccezioni:
        - ValueError: Se il numero non è un telefono italiano valido.
        """
        return Validators.validatePhoneNumber(v)


class PasswordUpdateSchema(BaseModel):
    """Schema di Input per l'aggiornamento della password con validazione complessità (max 90 car)."""
    new_password: SecretStr = Field(
        ...,
        title="Nuova Password",
        description="Password in chiaro (8-25 car). Maiuscola, minuscola, numero, speciale."
    )
    
    @field_validator('new_password')
    def validateNewPassword(cls, v: SecretStr) -> SecretStr:
        """
        Scopo: Verifica la complessità della password secondo policy di sicurezza.

        Parametri:
        - v (SecretStr): Password fornita (nascosta nei log).

        Valore di ritorno:
        - SecretStr: Password validata (invariata).

        Eccezioni:
        - ValueError: Se non rispetta i vincoli di complessità.
        """
        # Estrae il valore dalla SecretStr per la validazione
        password_plain = v.get_secret_value()
        Validators.validatePasswordComplexity(password_plain)
        return v


# --- HELPER ---

class PyObjectId(ObjectId):
    """
    Classe helper per la serializzazione dei MongoDB ObjectId in stringhe JSON (max 24 car).
    
    Questa classe facilita la conversione bidirezionale tra ObjectId (tipo nativo di MongoDB)
    e stringhe JSON per il trasporto nei messaggi API REST.
    """

    @classmethod
    def __get_validators__(cls):
        """
        Scopo: Fornisce i validatori Pydantic per deserializzare ObjectId da input JSON.
        
        Valore di ritorno:
            Generator: Generatore che yields il metodo validate.
        """
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """
        Scopo: Converte una stringa JSON in un ObjectId di MongoDB.
        
        Parametri:
            v (str|ObjectId): Valore da validare (stringa esadecimale 24 caratteri o ObjectId).
        
        Valore di ritorno:
            ObjectId: L'ObjectId validato.
        
        Eccezioni:
            ValueError: Sollevato se v non è una stringa esadecimale valida di 24 caratteri.
        """
        if not ObjectId.is_valid(v):
            raise ValueError("ObjectId non valido. Deve essere una stringa esadecimale di 24 caratteri.")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        """
        Scopo: Modifica lo schema JSON di Pydantic per rappresentare ObjectId come stringa.
        
        Parametri:
            field_schema (dict): Schema del campo generato da Pydantic.
        
        Effetto collaterale:
            Modifica in-place il dizionario field_schema impostando type='string'.
        """
        field_schema.update(type="string")


# --- MODELLI DATI ---

class UserBase(BaseModel):
    """
    Modello base con i campi anagrafici comuni (max 120 car).
    
    Contiene nome, cognome, email e telefono con relative validazioni di formato.
    Utilizzato come base per input e output nel sistema di gestione profili utente.
    """
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        title="Nome",
        description="Nome di battesimo dell'utente. Obbligatorio. Lunghezza: 1-50 caratteri."
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        title="Cognome",
        description="Cognome dell'utente. Obbligatorio. Lunghezza: 1-50 caratteri."
    )
    email: EmailStr = Field(
        ...,
        title="Email",
        description="Indirizzo email valido (RFC 5322). Identificativo univoco nel sistema."
    )
    num_tel: str = Field(
        ...,
        title="Numero di Telefono",
        description="Numero di telefono italiano in formato nazionale o internazionale "
                   "(es. '3331234567', '+393331234567'). Normalizzato a '+39...' nel DB."
    )


class UserCreateInput(UserBase):
    """Schema di Input per registrazione nuovo utente. Estende UserBase con password validata (max 100 car)."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=25,
        title="password",
        description="Password in chiaro (8-25 car). Maiuscola, minuscola, numero, speciale richiesti."
    )
    num_tel: str = Field(
        ...,
        title="Numero di Telefono",
        description="Numero di telefono italiano. Normalizzato a '+39...' nella registrazione."
    )

    @field_validator('password')
    def validatePassword(cls, v: str) -> str:
        """
        Scopo: Verifica complessità password secondo policy di sicurezza aziendale.

        Parametri:
        - v (str): Password in chiaro fornita dall'utente.

        Valore di ritorno:
        - str: Password validata (invariata).

        Eccezioni:
        - ValueError: Se non rispetta complessità richiesta.
        """
        return Validators.validatePasswordComplexity(v)
    
    @field_validator('num_tel')
    def validatePhone(cls, v: str) -> str:
        """
        Scopo: Valida e normalizza numero di telefono italiano durante registrazione.

        Parametri:
        - v (str): Numero di telefono in input.

        Valore di ritorno:
        - str: Numero normalizzato con prefisso '+39'.

        Eccezioni:
        - ValueError: Se non è un telefono italiano valido.
        """
        return Validators.validatePhoneNumber(v)


class UserUpdateInput(BaseModel):
    """
    Schema di Input per l'aggiornamento parziale del profilo (max 120 car).
    
    Tutti i campi sono opzionali. Solo i campi forniti nell'input vengono validati e aggiornati.
    Utilizzato per modifiche selettive ai dati anagrafici, email, telefono o password.
    """
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        title="Nome",
        description="Nuovo nome. Opzionale. Lunghezza: 1-50 caratteri se fornito."
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        title="Cognome",
        description="Nuovo cognome. Opzionale. Lunghezza: 1-50 caratteri se fornito."
    )
    email: Optional[EmailStr] = Field(
        None,
        title="Email",
        description="Nuova email. Opzionale. Deve essere univoca nel sistema se fornita."
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=25,
        title="password",
        description="Nuova password in chiaro (8-25 car). Opzionale. Maiuscola, minuscola, numero, speciale se fornita."
    )
    num_tel: Optional[str] = Field(
        None,
        title="Numero di Telefono",
        description="Nuovo numero di telefono italiano. Opzionale. Viene normalizzato a '+39...' se fornito."
    )
    
    @field_validator('num_tel')
    def validatePhoneIfProvided(cls, v: Optional[str]) -> Optional[str]:
        """
        Scopo: Valida numero di telefono solo se fornito durante aggiornamento parziale.

        Parametri:
        - v (Optional[str]): Numero di telefono o None.

        Valore di ritorno:
        - Optional[str]: Numero normalizzato o None.

        Eccezioni:
        - ValueError: Se numero è fornito ma non valido.

        Vincoli:
        - Se None nessuna validazione, se fornito deve rispettare formato italiano.
        """
        if v is None:
            return None
        return Validators.validatePhoneNumber(v)


"""
NOTA: UserInDB verrà utilizzato negli endpoint API per convertire i dati da MongoDB
e poi convertirli a UserOutputDTO prima di inviarli al client.
Attualmente non importato perché gli endpoint API non sono ancora implementati.

class UserInDB(UserBase):
    # Modello interno per la persistenza su MongoDB (max 130 car).
    # Estende UserBase e include i dati sensibili (hash password, flag attivo, ruolo).
    # Utilizzato dal layer di persistenza per rappresentare il documento MongoDB.
    id: PyObjectId = Field(
        default_factory=PyObjectId,
        alias="_id",
        title="ID Utente",
        description="Identificativo univoco MongoDB. Stringa esadecimale di 24 caratteri."
    )
    hashed_password: str = Field(
        ...,
        title="Password Hashata",
        description="Hash SHA-256 della password. Generato dal servizio durante la registrazione."
    )
    is_active: bool = Field(
        default=True,
        title="Account Attivo",
        description="Flag di attivazione. False indica account disattivato o eliminato (soft delete)."
    )
    role: str = Field(
        default="user",
        title="Ruolo Utente",
        description="Ruolo dell'utente nel sistema. Valori: 'user' (default) o 'admin'."
    )

    class Config:
        # Configurazione di Pydantic per la serializzazione e il mapping MongoDB.
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,  # Serializza ObjectId come stringa
        }
"""


"""
NOTA: UserOutputDTO è il modello usato come response_model negli endpoint API.
Viene usato automaticamente da FastAPI per convertire UserInDB → JSON
garantendo che la password non venga mai esposta nelle risposte HTTP.
Attualmente non importato perché gli endpoint API non sono ancora implementati.

class UserOutputDTO(UserBase):
    # Data Transfer Object (DTO) per le risposte API (max 130 car).
    # Esclude dati sensibili (password) e include metadati di autorizzazione.
    # Utilizzato in tutti gli endpoint API per garantire che le password non vengano mai esposte.
    id: PyObjectId = Field(
        alias="_id",
        title="ID Utente",
        description="Identificativo univoco MongoDB restituito come stringa esadecimale (24 caratteri)."
    )
    is_active: bool = Field(
        ...,
        title="Account Attivo",
        description="Flag che indica se l'account è attivo (True) o disattivato (False)."
    )
    role: str = Field(
        ...,
        title="Ruolo Utente",
        description="Ruolo utente nel sistema: 'user' per utenti standard, 'admin' per amministratori."
    )

    class Config:
        # Configurazione di Pydantic per la serializzazione delle risposte API.
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,  # Serializza ObjectId come stringa JSON
        }
"""