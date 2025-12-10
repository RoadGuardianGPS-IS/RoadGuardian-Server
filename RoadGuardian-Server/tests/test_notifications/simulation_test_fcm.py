import sys
import os
from unittest.mock import MagicMock, patch

# Configurazione path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
app_dir = os.path.join(parent_dir, 'app')
sys.path.insert(0, parent_dir)
sys.path.insert(0, app_dir)

from app.services.mappa_service import MappaService
from app.schemas.mappa_schema import UserPositionUpdate

# Configurazione Credenziali (come in manual_test_fcm.py)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
cred_file = os.path.join(project_root, "firebase_credentials.json")

if os.path.exists(cred_file):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_file
    print(f"Credenziali trovate: {cred_file}")
else:
    print(f"ATTENZIONE: File credenziali non trovato in: {cred_file}")
    print("Il test proverà comunque ad avviarsi, ma potrebbe fallire l'inizializzazione di Firebase se non mockata.")

def run_simulation_fcm_test():
    print("\n--- Inizio Simulazione Flusso FCM (Adapter Reale, Network Mockato) ---")
    
    # 1. Mockiamo SOLO la funzione di invio 'messaging.send'.
    #    Rimuoviamo il mock su 'initialize_app' così testiamo che le credenziali siano valide e l'app si inizializzi davvero.
    with patch('firebase_admin.messaging.send') as mock_send:
        
        # Configuriamo il mock dell'invio per restituire un ID messaggio finto (successo)
        mock_send.return_value = "projects/roadguardian/messages/fake_message_id"

        # 2. Inizializziamo il Service con un DB finto
        mock_db = MagicMock()
        
        # Qui viene istanziato il VERO NotifyFCMAdapter.
        # Se le credenziali sono corrette, l'inizializzazione reale avrà successo.
        try:
            service = MappaService(mock_db)
            print("Service e Adapter Reale inizializzati (con credenziali vere).")
        except Exception as e:
            print(f"ERRORE Inizializzazione Adapter: {e}")
            return
        # Grazie al patch su initialize_app, non fallirà anche se non hai le credenziali.
        service = MappaService(mock_db)
        print("Service e Adapter Reale inizializzati.")

        # 3. Mockiamo la repository per restituire un incidente vicino
        with patch('app.services.mappa_service.get_segnalazione_by_status') as mock_get_segnalazione:
            
            fake_incident = {
                "_id": "test_incident_id",
                "category": "Incidente Test",
                "seriousness": "high",
                "incident_latitude": 41.9028, 
                "incident_longitude": 12.4964,
                "status": True,
                "description": "Test Incidente Reale"
            }
            mock_get_segnalazione.return_value = [fake_incident]
            
            # 4. Usiamo un token finto (tanto la chiamata di rete è mockata)
            FAKE_TOKEN = "fake_device_token_12345"
            
            user_update = UserPositionUpdate(
                latitudine=41.9028,
                longitudine=12.4964,
                fcm_token=FAKE_TOKEN
            )
            
            print(f"Simulazione invio notifica per utente in posizione incidente...")
            
            # 5. Esecuzione
            # Ora dovresti vedere le print definite dentro notify_fcm_adapter.py
            service.process_user_position(user_update)
            
            print("\n--- Verifica ---")
            # Verifichiamo che la libreria di firebase sia stata chiamata davvero con il token finto
            if mock_send.called:
                print("SUCCESSO: Il codice è arrivato fino alla chiamata messaging.send()!")
                args, _ = mock_send.call_args
                msg_sent = args[0]
                print(f"Token nel messaggio: {msg_sent.token}")
                print(f"Titolo notifica: {msg_sent.notification.title}")
            else:
                print("FALLIMENTO: messaging.send() non è stato chiamato.")

if __name__ == "__main__":
    run_simulation_fcm_test()
