from schemas.user_schema import EmailUpdateSchema, PhoneUpdateSchema, PasswordUpdateSchema, UserCreateInput, UserUpdateInput
from db.profilo_utente_repository import get_user_by_email, update_email, update_num_tel, update_password, create_user, update_user
from models.user_model import UserModel, UserModelDTO
from fastapi import HTTPException
import hashlib

class ProfiloUtenteService:

    def __init__(self, db):
        self.db = db
    
    def change_email_logic(self,user_id: str, email_input: str) -> str:
        """
        Scopo: Gestisce la logica di business per il cambio email dell'utente.

        Parametri:
        - user_id (str): L'ID univoco dell'utente.
        - email_input (str): La nuova email da impostare.

        Valore di ritorno:
        - str: Messaggio di successo ("Email aggiornata") o di errore.

        Eccezioni:
        - Exception: Cattura eccezioni di validazione schema e restituisce messaggio di errore formattato.
        """
        try:
            #se l'email e sbagliata, questa riga fara errore
            valid_data = EmailUpdateSchema(new_email=email_input)

            #Se siamo qui, l'email e valida. Chiamiamo il DB
            success = update_email(user_id, valid_data.new_email)

            if success:
                return "Email aggiornata"
            return "Errore: utente non trovato nel DB"
        
        except Exception as e:
            error_msg = e.errors()[0]['msg']
            return f"bloccato dallo schema: {error_msg}"
        
    def change_password_logic(self, user_id: str, plain_password: str) -> str:
        """
        Scopo: Gestisce la logica di business per il cambio password dell'utente.

        Parametri:
        - user_id (str): L'ID univoco dell'utente.
        - plain_password (str): La nuova password in chiaro.

        Valore di ritorno:
        - str: Messaggio di successo ("password aggiornata") o di errore.

        Eccezioni:
        - Exception: Cattura eccezioni di validazione schema e restituisce messaggio generico.
        """
        try:
            valid_data = PasswordUpdateSchema(new_password=plain_password)

            password_cambiata = valid_data.new_password.get_secret_value() # passa SecretStr quindi serve get_secret_value

            success = update_password(user_id, password_cambiata)

            if success:
                return "password aggiornata"
            return "errore DB"
        
        except Exception as e:
            return "bloccato dallo schema"
        
    def change_phone_logic(self, user_id: str, phone_input: str) -> str:
        """
        Scopo: Gestisce la logica di business per il cambio numero di telefono dell'utente.

        Parametri:
        - user_id (str): L'ID univoco dell'utente.
        - phone_input (str): Il nuovo numero di telefono.

        Valore di ritorno:
        - str: Messaggio di successo ("numero telefono aggiornato") o di errore.

        Eccezioni:
        - Exception: Cattura eccezioni di validazione schema e restituisce messaggio generico.
        """
        try:
            valid_data = PhoneUpdateSchema(new_phone=phone_input)

            success = update_num_tel(user_id, str(valid_data.new_phone))

            if success:
                return "numero telefono aggiornato"
            return "errore DB"
        
        except Exception as e:
            return "bloccato dallo schema"
    
    def hash_password(self, plain_password: str) -> str:
        """
        Scopo: Calcola l'hash SHA-256 della password.

        Parametri:
        - plain_password (str): La password in chiaro.

        Valore di ritorno:
        - str: L'hash esadecimale della password.

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()

    def clean_phone_number(self, phone_number: str) -> str:
        """
        Scopo: Rimuove il prefisso 'tel:' dal numero di telefono se presente.

        Parametri:
        - phone_number (str): Il numero di telefono da pulire.

        Valore di ritorno:
        - str: Il numero di telefono pulito.

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        phone_str = str(phone_number)
        if phone_str.startswith("tel:"):
            return phone_str[4:]
        return phone_str

    def validate_prefix_phone_number(self, phone_number: str) -> str:
        """
        Scopo: Controlla e aggiunge il prefisso internazionale al numero di telefono se mancante.

        Parametri:
        - phone_number (str): Il numero di telefono da validare.

        Valore di ritorno:
        - str: Il numero di telefono normalizzato con prefisso +39 se necessario.

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        if phone_number.startswith("+39")or phone_number.startswith("tel:"):
            return phone_number
        # Aggiungi prefisso internazionale italiano (+39) se manca
        return "+39" + phone_number
    
    def create_user_profile(self, input_payload: UserCreateInput) -> UserModelDTO:
        """
        Scopo: Registra un nuovo utente nel sistema. Valida i dati, esegue l'hash della password e persiste il nuovo utente.

        Parametri:
        - input_payload (UserCreateInput): Dati anagrafici e password.

        Valore di ritorno:
        - UserModelDTO: Utente creato (senza password).

        Eccezioni:
        - HTTPException(400): Se l'email è già registrata o errore DB.
        - HTTPException(422): Se c'è un errore nella creazione del modello utente.
        """
        user_dict = input_payload.model_dump()

        #Controllo unicità email
        existing = get_user_by_email(user_dict["email"])
        if existing:
            raise HTTPException(status_code=400, detail="Email già registrata")


        hashed = self.hash_password(user_dict["password"])
        user_dict["password"] = hashed

        # Aggiunta prefisso internazionale al numero di telefono
        user_dict["num_tel"] = self.validate_prefix_phone_number(str(user_dict["num_tel"]))

        try:
            nuovo_utente = UserModel(**user_dict) #Scompone user_dict in argomenti chiave=valore
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))

        try:
            saved = create_user(nuovo_utente) #Salva nel DB
            # Converte il risultato in DTO per restituirlo al client
            saved_dict = saved.model_dump(by_alias=True)
            saved_dict["_id"] = str(saved_dict["_id"])
            # Pulizia numero di telefono (rimuove "tel:" se presente)
            if "num_tel" in saved_dict:
                saved_dict["num_tel"] = self.clean_phone_number(saved_dict["num_tel"])
            return UserModelDTO(**saved_dict)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Errore inserimento DB: {e}")

    def output_user_dto(self, user: UserModel) -> dict:
        """Nasconde la password e converte in DTO per output API."""
        return user.model_dump(by_alias=True, exclude={"password"})
    
    def update_user_profile(self, user_id: str, input_payload: UserUpdateInput) -> UserModelDTO:
        """
        Scopo: Aggiorna selettivamente i dati anagrafici dell'utente. Applica logiche specifiche per ogni campo e persiste le modifiche.

        Parametri:
        - user_id (str): Identificativo dell'utente.
        - input_payload (UserUpdateInput): Campi opzionali da aggiornare (body).

        Valore di ritorno:
        - UserModelDTO: Dati aggiornati dell'utente.

        Eccezioni:
        - HTTPException: 404 se l'utente non esiste.
        """
        #Otteniamo solo i campi che l'utente ha effettivamente inviato
        update_data = input_payload.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="Nessun dato fornito per l'aggiornamento")

        # Iteriamo su ogni campo per applicare logiche specifiche usando if/elif
        # Usiamo list(items()) per sicurezza durante l'iterazione
        for key, value in list(update_data.items()):
            
            if key == "password":
                # Se stiamo aggiornando la password, dobbiamo farne l'hash
                update_data[key] = self.hash_password(value)
            
            elif key == "num_tel":
                # Convertiamo il PhoneNumber object in stringa per MongoDB
                update_data[key] = self.validate_prefix_phone_number(str(value))
            
            elif key == "email":
                # Controllo unicità: se cambia email, verifichiamo che non sia già presa da altri
                existing = get_user_by_email(value)
                # Se esiste un utente con questa email E l'ID non corrisponde all'utente attuale
                if existing and str(existing["_id"]) != user_id:
                    raise HTTPException(status_code=400, detail="La nuova email è già in uso.")
            
            elif key == "first_name":
                # Modfica del nome
                update_data[key] = str(value)

            elif key == "last_name":
                # Modifica del cognome
                update_data[key] = str(value)

        # Salviamo le modifiche nel DB
        updated_dict = update_user(user_id, update_data)

        if not updated_dict:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        # Convertiamo l'ID in stringa per il DTO
        updated_dict["_id"] = str(updated_dict["_id"])
        # Pulizia numero di telefono (rimuove "tel:" se presente)
        if "num_tel" in updated_dict:
            updated_dict["num_tel"] = self.clean_phone_number(updated_dict["num_tel"])
        
        # Restituzione del DTO
        return UserModelDTO(**updated_dict)
    
    def login_user(self, input_payload: UserCreateInput) -> UserModelDTO:
        """
        Scopo: Verifica le credenziali e restituisce i dati dell'utente.

        Parametri:
        - input_payload (UserCreateInput): Credenziali (email, password).

        Valore di ritorno:
        - UserModelDTO: Dati dell'utente autenticato.

        Eccezioni:
        - HTTPException: 401 per credenziali errate.
        """
        user_dict = input_payload.model_dump()

        # Hash della password fornita
        hashed_password = self.hash_password(user_dict["password"])

        # Recupero utente dal DB
        existing_user = get_user_by_email(user_dict["email"])
        if not existing_user:
            raise HTTPException(status_code=404, detail="Utente non trovato")

        existing_user = get_user_by_email(user_dict["email"])
        if not existing_user:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        # Verifica se l'utente è stato cacellato
        if existing_user.get("is_active") == False:
            raise HTTPException(status_code=403, detail="Profilo utente disabilitato")
        # Verifica della password
        if existing_user["password"] != hashed_password:
            raise HTTPException(status_code=401, detail="Password errata")

        # Conversione in DTO
        existing_user["_id"] = str(existing_user["_id"])
        # Pulizia numero di telefono (rimuove "tel:" se presente)
        if "num_tel" in existing_user:
            existing_user["num_tel"] = self.clean_phone_number(existing_user["num_tel"])
        return UserModelDTO(**existing_user)
    
    def delete_user_profile(self, input_payload: UserUpdateInput) -> str:
        """
        Scopo: Elimina un profilo utente (soft delete).

        Parametri:
        - input_payload (UserUpdateInput): Dati utente per verifica (email, password).

        Valore di ritorno:
        - str: Messaggio di conferma.

        Eccezioni:
        - HTTPException: 404 se utente non trovato, 401 se password errata.
        """
        user_dict = input_payload.model_dump() #informazioni utente da eliminare (email, password)
        user_dict["password"] = self.hash_password(user_dict["password"])
        # Recupero utente dal DB
        existing_user = get_user_by_email(user_dict["email"])
        if not existing_user:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        # Verifica della password
        if existing_user["password"] != user_dict["password"]:
            raise HTTPException(status_code=401, detail="Password errata")
        # Esegue la soft delete (setta il flag "is_active" a False)
        update_user(str(existing_user["_id"]), {"is_active": False})
        
        return "Profilo utente eliminato"