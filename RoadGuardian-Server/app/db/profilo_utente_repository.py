from db.connection import get_database
from models.user_model import UserModel
from bson import ObjectId
from pydantic_extra_types.phone_numbers import PhoneNumber

# Otteniamo la collezione specifica
db = get_database()
user_collection = db["utenti"]  # "utenti" è il nome della collection che vedrai su Compass

def create_user(user: UserModel) -> UserModel:
    """Inserisce un utente nel DB"""
    user_dict = user.model_dump(by_alias=True, exclude={"id"}) # Escludiamo ID perché lo crea Mongo
    result = user_collection.insert_one(user_dict)
    
    # Recuperiamo l'ID generato e lo assegniamo all'oggetto
    user.id = str(result.inserted_id)
    return user

#def get_user_by_email(email: str) -> dict | None:
 #   """Cerca un utente per email"""
  #  # Restituisce un dizionario grezzo (o None), il Service lo convertirà in Modello se serve
   # return user_collection.find_one({"email": email})

def get_user_by_id(user_id: str) -> dict | None:
    """Cerca un utente per ID"""
    try:
        oid = ObjectId(user_id)
        return user_collection.find_one({"_id": oid})
    except:
        return None
    
#def get_user_by_num_tel(num_tel: PhoneNumber) -> dict | None:
 #   """Cerca un utente per numero di telefono"""
  #  # restituisce un dizionario grezzo (o none), il service lo convertirà in Modello se serve
   # return user_collection.find_one({"num_tel": num_tel})

def update_num_tel(user_id: str, new_phone: str) -> bool:
    #Aggiorna il numero di telefono

    try:
        oid = ObjectId(user_id)
        result = user_collection.update_one(
            {"_id": oid},
            #Nota: il campo nel DB si deve chiamare 'num_tel'.
            {"$set": {"num_tel": new_phone}}
        )
        return result.modified_count > 0 # se la modifica viene effettuata, modified_count sale di 1
    except Exception as e:
        print(f"Errore update_phone_number: {e}")
        return False
    
def update_email(user_id: str, new_email: str) -> bool:
    #Aggiorna l'email dell'utente.

    try:
        oid = ObjectId(user_id)
        result = user_collection.update_one(
            {"_id": oid},
            #Nota: il campo nel DB si deve chiamare 'email'
            {"$set": {"email": new_email}}
        )
        return result.modified_count > 0 
    except Exception as e:
        print(f"Errore update_email: {e}")
        return False
    
def update_password(user_id: str, new_password_hash: str) -> bool:
    
    #Aggiorna la password.
    #ATTENZIONE: Questa funzione si aspetta di ricevere GIA' l'hash della password, non la password in chiaro.
    
    try:
        oid = ObjectId(user_id)
        result = user_collection.update_one(
            {"_id": oid},
            #Nota: il campo nel DB si deve chiamare 'password'
            {"$set": {"password": new_password_hash}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Errore update_password: {e}")
        return False