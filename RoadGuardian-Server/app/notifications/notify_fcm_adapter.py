import firebase_admin
from firebase_admin import credentials, messaging
from typing import List
import os
from notifications.notifiche_api import NotificheAPI

class NotifyFCMAdapter(NotificheAPI):
    """
    Adapter per Firebase Cloud Messaging.
    Implementa l'interfaccia NotificheAPI e adatta le chiamate alla libreria firebase-admin.
    """

    def __init__(self, cred_path: str = None):
        """
        Inizializza l'app Firebase.
        
        Args:
            cred_path (str, optional): Percorso al file JSON delle credenziali di servizio.
                                       Se None, cerca:
                                       1. Variabile d'ambiente GOOGLE_APPLICATION_CREDENTIALS
                                       2. File 'firebase_credentials.json' nella root del progetto
        """
        if not firebase_admin._apps:
            if cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            elif os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                # Usa la variabile d'ambiente se esiste
                firebase_admin.initialize_app()
            else:
                # Tenta di trovare il file nella root del progetto automaticamente
                # La struttura delle cartelle: app/notifications/ -> app/ -> RoadGuardian-Server/ -> Root 
                # Inserire il file key di FCM nella directory root
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
                default_cred_path = os.path.join(project_root, "firebase_credentials.json")

                if os.path.exists(default_cred_path):
                    print(f"FCM Adapter: Trovate credenziali in {default_cred_path}")
                    cred = credentials.Certificate(default_cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    print("FCM Adapter: Nessuna credenziale trovata. L'invio notifiche potrebbe fallire.")
                    # Inizializzazione default (fallirà se non ci sono credenziali implicite)
                    firebase_admin.initialize_app()

    def send_notification(self, token: str, title: str, body: str, data: dict = None) -> bool:
        try:
            print("NotifyFCMAdapter: Inizio invio notifica FCM")
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data if data else {},
                token=token,
            )
            response = messaging.send(message)
            print("NotifyFCMAdapter: Fine fcm")
            # Response is a message ID string
            return True
        except Exception as e:
            print(f"Errore invio notifica FCM: {e}")
            return False

    def send_multicast_notification(self, tokens: List[str], title: str, body: str, data: dict = None) -> List[str]:
        if not tokens:
            return []
            
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data if data else {},
                tokens=tokens,
            )
            response = messaging.send_multicast(message)
            
            failed_tokens = []
            if response.failure_count > 0:
                responses = response.responses
                for idx, resp in enumerate(responses):
                    if not resp.success:
                        # The order of responses corresponds to the order of the registration tokens.
                        failed_tokens.append(tokens[idx])
            
            return failed_tokens
        except Exception as e:
            print(f"Errore invio notifica multicast FCM: {e}")
            return tokens # Consideriamo tutti falliti in caso di eccezione globale
