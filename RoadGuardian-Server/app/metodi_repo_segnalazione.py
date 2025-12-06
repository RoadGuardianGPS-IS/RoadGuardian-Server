from datetime import date, time, datetime
from models.incident_model import IncidentModel
import db.segnalazione_repository as repo
from db.connection import get_database

#Codice di test creato per provare tutti i metodi get in segnalazione_repository 
# ATTENZIONE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# QUESTO FILE INIZIA CON RESET DATABASE E VI CANCELLERÁ IL DATABASE ATTUALE CHE AVETE SU MONGO
# USATELO CON CAUTELA OPPURE COMMENTATE RESET_DATABASE

def reset_database():
    """Pulisce la collection per avere un test pulito"""
    print("--- Pulizia database... ---")
    db = get_database()
    db["segnalazioni"].delete_many({})

def populate_data():
    """Inserisce dati di test specifici per verificare le query"""
    print("--- Inserimento dati di test... ---")

    # CASO 1: 25 Ottobre alle 14:30 (Attivo)
    s1 = IncidentModel(
        user_id="user_1",
        incident_date=date(2023, 10, 25),
        incident_time=time(14, 30),
        incident_longitude=12.0, incident_latitude=41.0,
        seriousness="high", category="accident", description="Caso 1: 25/10 h14:30", status=True
    )

    # CASO 2: 25 Ottobre alle 18:00 (Attivo) - Stessa data di s1, orario diverso
    s2 = IncidentModel(
        user_id="user_2",
        incident_date=date(2023, 10, 25),
        incident_time=time(18, 00),
        incident_longitude=12.0, incident_latitude=41.0,
        seriousness="low", category="accident", description="Caso 2: 25/10 h18:00", status=True
    )

    # CASO 3: 26 Ottobre alle 14:30 (Attivo) - Data diversa, Stesso orario di s1
    s3 = IncidentModel(
        user_id="user_1",
        incident_date=date(2023, 10, 26),
        incident_time=time(14, 30),
        incident_longitude=13.0, incident_latitude=42.0,
        seriousness="medium", category="road_damage", description="Caso 3: 26/10 h14:30", status=True
    )

    # CASO 4: 25 Ottobre alle 09:00 (NON ATTIVO) - Status False
    s4 = IncidentModel(
        user_id="user_3",
        incident_date=date(2023, 10, 25),
        incident_time=time(9, 00),
        incident_longitude=12.0, incident_latitude=41.0,
        seriousness="low", category="other", description="Caso 4: Cancellato", status=False
    )

    res1 = repo.create_segnalazione(s1)
    repo.create_segnalazione(s2)
    repo.create_segnalazione(s3)
    repo.create_segnalazione(s4)
    
    return res1['id'] # Ritorniamo un ID per il test by_id

def run_tests():
    # 0. Setup
    reset_database()
    id_s1 = populate_data()
    print("\n--- INIZIO TEST ---\n")

    # 1. TEST GET BY ID
    print(f"[TEST 1] get_segnalazione_by_id ({id_s1})")
    res = repo.get_segnalazione_by_id(id_s1)
    if res and res['description'] == "Caso 1: 25/10 h14:30":
        print("[OK] PASS")
    else:
        print(f"[FAIL] Errore: {res}")

    # 2. TEST BY DATE (25 Ottobre)
    # Deve trovare Caso 1 e Caso 2 (Attivi).
    # Caso 4 è del 25 ma è status=False, quindi NON deve esserci.
    target_date = date(2023, 10, 25)
    print(f"\n[TEST 2] get_segnalazione_by_date ({target_date})")
    print("   -> Mi aspetto 2 risultati (Caso 1 e Caso 2)")
    res_list = repo.get_segnalazione_by_date(target_date)
    print(f"   -> Trovati: {len(res_list)}")
    
    descriptions = [x['description'] for x in res_list]
    if len(res_list) == 2 and "Caso 1: 25/10 h14:30" in descriptions and "Caso 2: 25/10 h18:00" in descriptions:
        print("[OK] PASS")
    else:
        print(f"[FAIL] Errore: {descriptions}")

    # 3. TEST BY TIME (14:30)
    # Deve trovare Caso 1 (25/10) e Caso 3 (26/10).
    target_time = time(14, 30)
    print(f"\n[TEST 3] get_segnalazione_by_time ({target_time})")
    print("   -> Mi aspetto 2 risultati (Caso 1 e Caso 3 - giorni diversi stessa ora)")
    res_list = repo.get_segnalazione_by_time(target_time)
    print(f"   -> Trovati: {len(res_list)}")

    descriptions = [x['description'] for x in res_list]
    if len(res_list) == 2 and "Caso 1: 25/10 h14:30" in descriptions and "Caso 3: 26/10 h14:30" in descriptions:
        print("[OK] PASS")
    else:
        print(f"[FAIL] Errore: {descriptions}")

    # 4. TEST BY DATE AND TIME (25/10 14:30)
    # Deve trovare SOLO Caso 1.
    print(f"\n[TEST 4] get_segnalazione_by_date_and_time (25/10 h14:30)")
    res_list = repo.get_segnalazione_by_date_and_time(target_date, target_time)
    print(f"   -> Trovati: {len(res_list)}")
    
    if len(res_list) == 1 and res_list[0]['description'] == "Caso 1: 25/10 h14:30":
        print("[OK] PASS")
    else:
        print(f"[FAIL] Errore: {[x['description'] for x in res_list]}")

    # 5. TEST STATUS FALSE
    # Deve trovare solo Caso 4
    print(f"\n[TEST 5] get_segnalazione_by_status (False)")
    res_list = repo.get_segnalazione_by_status(False)
    if len(res_list) == 1 and res_list[0]['description'] == "Caso 4: Cancellato":
        print("[OK] PASS")
    else:
        print(f"[FAIL] Trovati {len(res_list)}")

    # 6. TEST DELETE
    print(f"\n[TEST 6] delete_segnalazione ({id_s1})")
    success = repo.delete_segnalazione(id_s1)
    # Verifica: ora se cerco per ID deve esistere ma con status False (o non essere trovata dalle query attive)
    check = repo.get_segnalazione_by_id(id_s1)
    
    if success and check['status'] is False:
        print("[OK] PASS: Segnalazione marcata come False")
    else:
        print(f"[FAIL] Status è ancora {check.get('status')}")

if __name__ == "__main__":
    run_tests()