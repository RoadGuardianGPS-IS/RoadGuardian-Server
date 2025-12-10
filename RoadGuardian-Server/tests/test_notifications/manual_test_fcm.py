import sys
import os
from unittest.mock import MagicMock, patch

# Configurazione path per importare i moduli
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
app_dir = os.path.join(parent_dir, 'app')
sys.path.insert(0, parent_dir)
sys.path.insert(0, app_dir)

from app.services.mappa_service import MappaService
from app.schemas.mappa_schema import UserPositionUpdate

# NOTA: Assicurati che la variabile d'ambiente GOOGLE_APPLICATION_CREDENTIALS sia settata
# oppure che il file delle credenziali sia nel path di default.
# Cerchiamo il file nella root del progetto
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
cred_file = os.path.join(project_root, "firebase_credentials.json")

if os.path.exists(cred_file):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_file
    print(f"Credenziali trovate: {cred_file}")
else:
    print(f"ATTENZIONE: File credenziali non trovato in: {cred_file}")
    print("Assicurati di aver messo il file JSON scaricato da Firebase nella root del progetto e rinominato in 'firebase_credentials.json'")

def run_real_fcm_test():
    print("\n--- Inizio Test Reale FCM (No Mock Adapter) ---")
    
    # 1. Mock del Database (non ci serve il DB reale per questo test)
    mock_db = MagicMock()
    
    # 2. Inizializziamo il Service
    # Qui verrà creato il VERO NotifyFCMAdapter perché non stiamo usando patch() sulla classe
    try:
        service = MappaService(mock_db)
        print("Service inizializzato con Adapter Reale.")
    except Exception as e:
        print(f"Errore inizializzazione Service (probabilmente mancano credenziali Firebase): {e}")
        return

    # 3. Mockiamo solo la repository delle segnalazioni per restituire un incidente finto vicino all'utente
    with patch('app.services.mappa_service.get_segnalazione_by_status') as mock_get_segnalazione:
        
        # Creiamo un incidente finto esattamente nella posizione dell'utente
        fake_incident = {
            "_id": "test_incident_id",
            "category": "Incidente Test",
            "seriousness": "high",
            "incident_latitude": 41.9028, # Roma Colosseo
            "incident_longitude": 12.4964,
            "status": True,
            "description": "Test Incidente Reale"
        }
        mock_get_segnalazione.return_value = [fake_incident]
        
        # 4. Dati Utente con Token FCM
        # IMPORTANTE: Sostituisci questo token con uno valido del tuo dispositivo per ricevere la notifica
        REAL_DEVICE_TOKEN = "INSERISCI_QUI_IL_TUO_TOKEN_FCM_REALE" 
        
        if REAL_DEVICE_TOKEN == "INSERISCI_QUI_IL_TUO_TOKEN_FCM_REALE":
            print("ATTENZIONE: Devi inserire un token FCM valido nel file per testare l'invio reale.")
        
        user_update = UserPositionUpdate(
            latitudine=41.9028,
            longitudine=12.4964,
            fcm_token=REAL_DEVICE_TOKEN
        )
        
        print(f"Tentativo invio notifica a token: {user_update.fcm_token[:10]}...")
        
        # 5. Esecuzione
        try:
            service.process_user_position(user_update)
            print("\nTest completato. Controlla se hai ricevuto la notifica sul dispositivo.")
            print("Dovresti aver visto anche le print 'Inizio invio notifica FCM' e 'Fine fcm'.")
        except Exception as e:
            print(f"\nERRORE durante l'esecuzione: {e}")

if __name__ == "__main__":
    run_real_fcm_test()
