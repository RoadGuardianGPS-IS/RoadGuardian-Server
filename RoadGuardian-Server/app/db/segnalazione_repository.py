from .connection import get_database
from models.incident_model import IncidentModel
from bson import ObjectId
from pymongo import ReturnDocument
import datetime

# Otteniamo la collezione specifica
db = get_database()
segnalazione_collection = db["segnalazioni"]  # "segnalazioni" è il nome della collection che vedrai su Compass

def create_segnalazione(segnalazione: IncidentModel) -> dict:
    """
    Scopo: Inserisce una segnalazione nella collection `segnalazioni` del DB.

    Parametri:
    - segnalazione (IncidentModel): Istanza del modello segnalazione.

    Valore di ritorno:
    - dict: Dizionario della segnalazione salvata con campo `id` valorizzato.

    Eccezioni:
    - pymongo.errors.PyMongoError: se l'inserimento fallisce.
    """
    segnalazione_dict = segnalazione.to_mongo() #chiama il metodo interno alla classe del model
    result = segnalazione_collection.insert_one(segnalazione_dict)
    
    # Recuperiamo l'ID generato e lo assegniamo all'oggetto
    segnalazione_dict["id"] = str(result.inserted_id)
    return segnalazione_dict

def get_segnalazione_by_id(segnalazione_id: str) -> dict | None:
    """
    Scopo: Cercare e restituire una segnalazione per ID Mongo.

    Parametri:
    - segnalazione_id (str): ID della segnalazione in formato stringa.

    Valore di ritorno:
    - dict | None: Documento segnalazione se trovato, altrimenti None.

    Eccezioni:
    - bson.errors.InvalidId: se `segnalazione_id` non è un ObjectId valido.
    - pymongo.errors.PyMongoError: errori nella query.
    """
    try:
        oid = ObjectId(segnalazione_id)
        return segnalazione_collection.find_one({"_id": oid})
    except:
        return None
    
def get_segnalazione_by_position(incident_longitude: float, incident_latitude: float) -> dict | None:
    """
    Scopo: Recuperare una segnalazione attiva per posizione geografica esatta.

    Parametri:
    - incident_longitude (float): Longitudine della segnalazione.
    - incident_latitude (float): Latitudine della segnalazione.

    Valore di ritorno:
    - dict | None: Documento segnalazione se trovato, altrimenti None.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query fallisce.
    """

    return segnalazione_collection.find_one({
        "incident_longitude": incident_longitude,
        "incident_latitude": incident_latitude,
        "status": True
    })

def get_segnalazione_list_by_position(incident_longitude: float, incident_latitude: float) -> list[dict]:
    """
    Scopo: Recuperare tutte le segnalazioni attive per una data posizione.

    Parametri:
    - incident_longitude (float): Longitudine della posizione.
    - incident_latitude (float): Latitudine della posizione.

    Valore di ritorno:
    - list[dict]: Lista di documenti segnalazione corrispondenti.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query fallisce.
    """

    return list(segnalazione_collection.find({
        "incident_longitude": incident_longitude,
        "incident_latitude": incident_latitude,
        "status": True
    }))

def get_segnalazione_by_category(category: str) -> list[dict]:
    """
    Scopo: Ottenere segnalazioni attive appartenenti a una categoria.

    Parametri:
    - category (str): Nome della categoria di segnalazione.

    Valore di ritorno:
    - list[dict]: Lista di documenti segnalazione della categoria.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query fallisce.
    """

    return list(segnalazione_collection.find({"category": category,
                                              "status": True}))

def get_segnalazione_by_user(user_id: str) -> list[dict]:
    """
    Scopo: Recuperare tutte le segnalazioni attive create da un utente.

    Parametri:
    - user_id (str): ID dell'utente che ha creato le segnalazioni.

    Valore di ritorno:
    - list[dict]: Lista di documenti segnalazione dell'utente.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query fallisce.
    """

    return list(segnalazione_collection.find({"user_id": user_id,
                                              "status": True}))

def get_segnalazione_by_status(status: bool) -> list[dict]:
    """
    Scopo: Ottenere segnalazioni filtrate per stato (attivo/inattivo).

    Parametri:
    - status (bool): Stato della segnalazione (True = attiva, False = inattiva).

    Valore di ritorno:
    - list[dict]: Lista di documenti segnalazione con lo stato richiesto.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query fallisce.
    """

    return list(segnalazione_collection.find({"status": status}))

def get_segnalazione_by_date(target_date: datetime.date) -> list[dict]:
    """
    Scopo: Cercare segnalazioni per data (intervallo 00:00 - 23:59 dello stesso giorno).

    Parametri:
    - target_date (datetime.date): Data da cercare.

    Valore di ritorno:
    - list[dict]: Lista di documenti segnalazione trovati nella fascia di data.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query fallisce.
    """
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
    """
    Scopo: Cercare segnalazioni per orario (confronto ora:minuti).

    Parametri:
    - target_time (datetime.time): Orario da cercare.

    Valore di ritorno:
    - list[dict]: Lista di documenti segnalazione corrispondenti all'orario.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query fallisce.
    """
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
    """
    Scopo: Cercare segnalazioni corrispondenti a data e orario esatti.

    Parametri:
    - target_date (datetime.date): Data da cercare.
    - target_time (datetime.time): Orario da cercare.

    Valore di ritorno:
    - list[dict]: Lista di documenti segnalazione che coincidono esattamente.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query fallisce.
    """
    dt_to_find = datetime.datetime.combine(target_date, target_time)
    return list(segnalazione_collection.find({
        "incident_date": dt_to_find,
        "status": True
    }))

def get_segnalazione_by_seriousness(seriousness: str) -> list[dict]:
    """
    Scopo: Cercare segnalazioni per livello di gravità.

    Parametri:
    - seriousness (str): Livello di gravità (es. 'low', 'medium', 'high').

    Valore di ritorno:
    - list[dict]: Lista di documenti segnalazione che matchano il livello.

    Eccezioni:
    - pymongo.errors.PyMongoError: se la query fallisce.
    """

    return list(segnalazione_collection.find({
        "seriousness": seriousness,
        "status": True
    }))

def delete_segnalazione(segnalazione_id: str) -> bool:
    """
    Scopo: Effettuare la cancellazione logica di una segnalazione impostando `status` a False.

    Parametri:
    - segnalazione_id (str): ID della segnalazione in formato stringa.

    Valore di ritorno:
    - bool: True se l'operazione ha modificato il documento, False altrimenti.

    Eccezioni:
    - bson.errors.InvalidId: se `segnalazione_id` non è un ObjectId valido.
    - pymongo.errors.PyMongoError: per errori nell'aggiornamento.
    """

    try:
        oid = ObjectId(segnalazione_id)
        result = segnalazione_collection.update_one({
            "_id": oid},
            {"$set": {"status": False}}) #Per "eliminare" la segnalazione cambia lo status di essa in false, come avviene con la cancellazione del profilo utente
        return result.modified_count > 0
    except Exception as e:
        print(f"Errore delete_segnalazione: {e}")
        return False