from datetime import date, time, datetime
from .models.incident_model import IncidentModel
from .db import segnalazione_repository as repo

#Codice di test dell'inizializzazione a DB delle segnalazioni, e di conseguenza codice che si aspetta il DB in entrata.

def initialize_data():
    print("--- Inizio Inizializzazione Dati ---")

    # Caso 1: Segnalazione standard attiva (Incidente)
    segnalazione_1 = IncidentModel(
        user_id="user_123",
        incident_date=date(2023, 10, 25),
        incident_time=time(14,30),
        incident_longitude=12.4924,
        incident_latitude=41.8902,
        seriousness="high",
        status=True,
        category="accident",
        description="Incidente grave tra due auto",
        img_url="http://example.com/accident.jpg"
    )

    # Caso 2: Segnalazione attiva di altro tipo (Buca stradale)
    # Stesse coordinate del caso 1 per testare la ricerca per posizione
    segnalazione_2 = IncidentModel(
        user_id="user_456",
        incident_date=date(2023, 10, 25),
        incident_time=time(10,10),
        incident_longitude=12.4924,
        incident_latitude=41.8902,
        seriousness="low",
        status=True,
        category="road_damage",
        description="Buca profonda sulla carreggiata destra",
        img_url="http://example.com/pothole.jpg"
    )

    # Caso 3: Segnalazione NON attiva (status=False), es. risolta o cancellata
    segnalazione_3 = IncidentModel(
        user_id="user_123",
        incident_date=date(2023, 10, 20),
        incident_time=time(12,23),
        incident_longitude=10.1234,
        incident_latitude=45.5678,
        seriousness="medium",
        status=False,  # Importante per testare i filtri
        category="fire",
        description="Principio di incendio in cestino rifiuti",
        img_url="http://example.com/fire.jpg"
    )

    # Inserimento nel DB
    try:
        res1 = repo.create_segnalazione(segnalazione_1)
        print(f"Inserita segnalazione 1: ID {res1['id']} - Cat: {res1['category']}")

        res2 = repo.create_segnalazione(segnalazione_2)
        print(f"Inserita segnalazione 2: ID {res2['id']} - Cat: {res2['category']}")

        res3 = repo.create_segnalazione(segnalazione_3)
        print(f"Inserita segnalazione 3: ID {res3['id']} - Cat: {res3['category']} (Status: False)")
        
        return [res1, res2, res3]
        
    except Exception as e:
        print(f"Errore durante l'inserimento: {e}")
        return []

if __name__ == "__main__":
    initialize_data()