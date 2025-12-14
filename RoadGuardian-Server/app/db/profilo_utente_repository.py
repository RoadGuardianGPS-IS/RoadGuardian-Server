from pymongo import ReturnDocument
from db.connection import get_database
from models.user_model import UserModel
from bson import ObjectId
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Dict, Any

# Otteniamo la collezione specifica
db = get_database()
user_collection = db["utenti"]  # "utenti" è il nome della collection che vedrai su Compass

def create_user(user: UserModel) -> UserModel:
    """
    Scopo: Inserisce un nuovo utente nella collection `utenti` del DB Mongo.

    Parametri:
    - user (UserModel): Istanza Pydantic contenente i campi dell'utente.

    Valore di ritorno:
    - UserModel: La stessa istanza `user` con il campo `id` popolato dall'ID Mongo.

    Eccezioni:
    - pymongo.errors.PyMongoError: se l'inserimento fallisce per errori DB.
    - TypeError/ValueError: se il modello non è serializzabile correttamente.
    """
    user_dict = user.model_dump(by_alias=True, exclude={"id"}) # Escludiamo ID perché lo crea Mongo
    result = user_collection.insert_one(user_dict)
    
    # Recuperiamo l'ID generato e lo assegniamo all'oggetto
    user.id = str(result.inserted_id)
    return user

def get_user_by_email(email: str) -> dict | None:
    """
    Scopo: Recuperare un documento utente cercando per campo `email`.

    Parametri:
    - email (str): Indirizzo email da cercare.

    Valore di ritorno:
    - dict | None: Dizionario del documento utente se trovato, altrimenti None.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query al DB fallisce.
    """
    # Restituisce un dizionario grezzo (o None), il Service lo convertirà in Modello se serve
    return user_collection.find_one({"email": email})

def get_user_by_id(user_id: str) -> dict | None:
    """
    Scopo: Recuperare un documento utente dato il suo ID Mongo.

    Parametri:
    - user_id (str): ID dell'utente in formato stringa (hex di ObjectId).

    Valore di ritorno:
    - dict | None: Dizionario del documento utente se trovato, altrimenti None.

    Eccezioni:
    - bson.errors.InvalidId: se `user_id` non è un ObjectId valido.
    - pymongo.errors.PyMongoError: per errori nella query.
    """
    try:
        oid = ObjectId(user_id)
        return user_collection.find_one({"_id": oid})
    except:
        return None
    
def get_user_by_num_tel(num_tel: PhoneNumber) -> dict | None:
    """
    Scopo: Recuperare un documento utente tramite il numero di telefono.

    Parametri:
    - num_tel (PhoneNumber): Numero telefonico (oggetto PhoneNumber o stringa compatibile).

    Valore di ritorno:
    - dict | None: Dizionario del documento utente se trovato, altrimenti None.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query al DB fallisce.
    """
    # restituisce un dizionario grezzo (o none), il service lo convertirà in Modello se serve
    return user_collection.find_one({"num_tel": str(num_tel)})

def update_num_tel(user_id: str, new_phone: str) -> bool:
    """
    Scopo: Aggiornare il numero di telefono di un utente esistente.

    Parametri:
    - user_id (str): ID dell'utente come stringa.
    - new_phone (str): Nuovo numero di telefono da impostare (stringa).

    Valore di ritorno:
    - bool: True se l'aggiornamento ha modificato il documento, False altrimenti.

    Eccezioni:
    - bson.errors.InvalidId: se `user_id` non è un ObjectId valido.
    - pymongo.errors.PyMongoError: per errori nella scrittura sul DB.
    """

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
    """
    Scopo: Aggiornare l'indirizzo email di un utente.

    Parametri:
    - user_id (str): ID dell'utente come stringa.
    - new_email (str): Nuova email da impostare.

    Valore di ritorno:
    - bool: True se l'aggiornamento ha avuto effetto, False altrimenti.

    Eccezioni:
    - bson.errors.InvalidId: se `user_id` non è un ObjectId valido.
    - pymongo.errors.PyMongoError: per errori nella scrittura sul DB.
    """

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
    """
    Scopo: Aggiornare la password dell'utente (richiede l'hash già calcolato).

    Parametri:
    - user_id (str): ID dell'utente come stringa.
    - new_password_hash (str): Hash della nuova password.

    Valore di ritorno:
    - bool: True se l'aggiornamento ha modificato il documento, False altrimenti.

    Eccezioni:
    - bson.errors.InvalidId: se `user_id` non è un ObjectId valido.
    - pymongo.errors.PyMongoError: per errori nella scrittura sul DB.
    """
    
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
    
def update_user(user_id: str, fields_to_update: Dict[str, any]) -> dict | None:
    """
    Scopo: Aggiornare i campi specificati di un utente e restituire il documento aggiornato.

    Parametri:
    - user_id (str): ID dell'utente come stringa.
    - fields_to_update (Dict[str, any]): Dizionario dei campi da aggiornare e relativi valori.

    Valore di ritorno:
    - dict | None: Documento aggiornato (dizionario) se l'operazione ha successo, altrimenti None.

    Eccezioni:
    - bson.errors.InvalidId: se `user_id` non è un ObjectId valido.
    - pymongo.errors.PyMongoError: per errori nella query/aggiornamento.
    """
    try:
        oid = ObjectId(user_id)
        result = user_collection.find_one_and_update(
            {"_id": oid},
            {"$set": fields_to_update},
            return_document=ReturnDocument.AFTER  # Restituisce il documento aggiornato
        )
        return result
    except Exception as e:
        print(f"Errore update_user: {e}")
        return None