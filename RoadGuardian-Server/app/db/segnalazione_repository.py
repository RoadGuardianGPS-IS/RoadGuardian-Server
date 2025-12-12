from .connection import get_database
from models.incident_model import IncidentModel
from bson import ObjectId
from pymongo import ReturnDocument
import datetime

# Otteniamo la collezione specifica
db = get_database()
segnalazione_collection = db["segnalazioni"]  # "segnalazioni" è il nome della collection che vedrai su Compass

def create_segnalazione(segnalazione: IncidentModel) -> dict:
    """Inserisce una segnalazione nel DB"""
    segnalazione_dict = segnalazione.to_mongo() #chiama il metodo interno alla classe del model
    result = segnalazione_collection.insert_one(segnalazione_dict)
    
    # Recuperiamo l'ID generato e lo assegniamo all'oggetto
    segnalazione_dict["id"] = str(result.inserted_id)
    return segnalazione_dict

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

def get_segnalazione_by_date(target_date: datetime.date) -> list[dict]:
    """Cerca segnalazioni per data, dalle 00:00 alle 23:59 (min e max)
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""
    start_dt = datetime.datetime.combine(target_date, datetime.time.min)
    end_dt = datetime.datetime.combine(target_date, datetime.time.max)

    return list(segnalazione_collection.find({
        "incident_date": {
            "$gte": start_dt, # Maggiore o uguale a inizio giorno
            "$lte": end_dt    # Minore o uguale a fine giorno
        },
        "status": True
    }))
    

def get_segnalazione_by_time(target_time: datetime.time) -> list[dict]:
    """Cerca segnalazioni per orario
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""
    return list(segnalazione_collection.find({
        "$expr": {
            "$and": [
                # Confronta l'ora del campo DB con l'ora richiesta
                {"$eq": [{"$hour": "$incident_date"}, target_time.hour]},
                # Confronta i minuti del campo DB con i minuti richiesti
                {"$eq": [{"$minute": "$incident_date"}, target_time.minute]},
            ]
        },
        "status": True
    }))

def get_segnalazione_by_date_and_time(target_date: datetime.date, target_time: datetime.time) -> list[dict]:
    """Cerca segnalazioni per data e orario
    ATTENZIONE: questa funzione ritorna una lista di segnalazioni"""
    dt_to_find = datetime.datetime.combine(target_date, target_time)
    return list(segnalazione_collection.find({
        "incident_date": dt_to_find,
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
            {"$set": {"status": False}}) #Per "eliminare" la segnalazione cambia lo status di essa in false, come avviene con la cancellazione del profilo utente
        return result.modified_count > 0
    except Exception as e:
        print(f"Errore delete_segnalazione: {e}")
        return False