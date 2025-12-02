from schemas.user_schema import EmailUpdateSchema, PhoneUpdateSchema, PasswordUpdateSchema
from db.profilo_utente_repository import update_email, update_num_tel, update_password
#qui verra messo l'import dell'hashing

def change_email_logic(user_id: str, email_input: str) -> str:
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
    
def change_password_logic(user_id: str, plain_password: str) -> str:
    try:
        valid_data = PasswordUpdateSchema(new_password=plain_password)

        password_cambiata = valid_data.new_password.get_secret_value() # passa SecretStr quindi serve get_secret_value

        success = update_password(user_id, password_cambiata)

        if success:
            return "password aggiornata"
        return "errore DB"
    
    except Exception as e:
        return "bloccato dallo schema"
    
def change_phone_logic(user_id: str, phone_input: str) -> str:
    try:
        valid_data = PhoneUpdateSchema(new_phone=phone_input)

        success = update_num_tel(user_id, str(valid_data.new_phone))

        if success:
            return "numero telefono aggiornato"
        return "errore DB"
    
    except Exception as e:
        return "bloccato dallo schema"