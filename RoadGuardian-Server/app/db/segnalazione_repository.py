from db.connection import get_database
# from models.incident_model import IncidentModel
from bson import ObjectId
from pymongo import ReturnDocument
import datetime

# Otteniamo la collezione specifica
db = get_database()
segnalazione_collection = db["segnalazioni"]  # "segnalazioni" è il nome della collection che vedrai su Compass

def create_segnalazione(segnalazione: dict) -> dict:
    """Inserisce una segnalazione nel DB"""
    segnalazione_dict = segnalazione.model_dump(by_alias=True, exclude={"id"}) # Escludiamo ID perché lo crea Mongo
    result = segnalazione_collection.insert_one(segnalazione_dict)
    
    # Recuperiamo l'ID generato e lo assegniamo all'oggetto
    segnalazione["id"] = str(result.inserted_id)
    return segnalazione

def get_segnalazione_by_id(segnalazione_id: str) -> dict | None:
    """Cerca una segnalazione per ID"""
    try:
        oid = ObjectId(segnalazione_id)
        return segnalazione_collection.find_one({"_id": oid})
    except:
        return None
    
def get_segnalazione_by_position(incident_longitude: float, incident_latitude: float) -> dict | None:
    """Cerca una segnalazione per posizione (longitudine e latitudine)"""

    return segnalazione_collection.find_one({
        "incident_longitude": incident_longitude,
        "incident_latitude": incident_latitude,
        "status": True
    })

def get_segnalazione_list_by_position(incident_longitude: float, incident_latitude: float) -> list[dict]:
    """Cerca segnalazioni per posizione (longitudine e latitudine)
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""

    return list(segnalazione_collection.find({
        "incident_longitude": incident_longitude,
        "incident_latitude": incident_latitude,
        "status": True
    }))

def get_segnalazione_by_category(category: str) -> list[dict]:
    """Cerca segnalazioni per categoria
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""

    return list(segnalazione_collection.find({"category": category,
                                              "status": True}))

def get_segnalazione_by_user(user_id: str) -> list[dict]:
    """Cerca segnalazioni per user_id
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""

    return list(segnalazione_collection.find({"user_id": user_id,
                                              "status": True}))

def get_segnalazione_by_status(status: bool) -> list[dict]:
    """Cerca segnalazioni per status
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""

    return list(segnalazione_collection.find({"status": status}))

def get_segnalazione_by_date(date: datetime.date) -> list[dict]:
    """Cerca segnalazioni per data
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""

    return list(segnalazione_collection.find({
        "date": date,
        "status": True
    }))

def get_segnalazione_by_time(time: datetime.time) -> list[dict]:
    """Cerca segnalazioni per orario
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""

    return list(segnalazione_collection.find({
        "time": time,
        "status": True
    }))

def get_segnalazione_by_date_and_time(date_and_time: datetime.datetime) -> list[dict]:
    """Cerca segnalazioni per data e orario
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""

    return list(segnalazione_collection.find({
        "date": date_and_time.date(),
        "time": date_and_time.time(),
        "status": True
    }))

def get_segnalazione_by_seriousness(seriousness: str) -> list[dict]:
    """Cerca segnalazioni per livello di gravità
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""

    return list(segnalazione_collection.find({
        "seriousness": seriousness,
        "status": True
    }))

def delete_segnalazione(segnalazione_id: str) -> bool:
    """Elimina una segnalazione per ID"""

    try:
        oid = ObjectId(segnalazione_id)
        result = segnalazione_collection.update_one({
            "_id": oid},
            {"$set": {"status": False}})
        return result.modified_count > 0
    except Exception as e:
        print(f"Errore delete_segnalazione: {e}")
        return False