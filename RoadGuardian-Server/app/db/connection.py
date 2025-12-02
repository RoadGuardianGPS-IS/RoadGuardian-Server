from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "RoadGuardian_db"  # Nome del database

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_database():
    return db

if __name__ == "__main__":
    try:
        # Il comando ping è il modo più rapido per verificare la connessione
        client.admin.command('ping')
        print("Connessione a MongoDB riuscita con successo!")
    except ConnectionFailure:
        print("Errore: Il server MongoDB non è raggiungibile.")
    except Exception as e:
        print(f"Errore generico: {e}")