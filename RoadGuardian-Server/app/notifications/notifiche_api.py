from abc import ABC, abstractmethod
from typing import List

class NotificheAPI(ABC):
    """
    Interfaccia per il sistema di notifiche (Target).
    Definisce i metodi che il client (RoadGuardian) si aspetta di utilizzare.
    """

    @abstractmethod
    def send_notification(self, token: str, title: str, body: str, data: dict = None) -> bool:
        """
        Invia una notifica push a un singolo dispositivo.
        
        Args:
            token (str): Il token FCM del dispositivo destinatario.
            title (str): Il titolo della notifica.
            body (str): Il corpo del messaggio.
            data (dict, optional): Dati aggiuntivi (payload) da inviare con la notifica.
            
        Returns:
            bool: True se l'invio è riuscito, False altrimenti.
        """
        pass

    @abstractmethod
    def send_multicast_notification(self, tokens: List[str], title: str, body: str, data: dict = None) -> List[str]:
        """
        Invia una notifica push a più dispositivi.
        
        Args:
            tokens (List[str]): Lista dei token FCM dei destinatari.
            title (str): Il titolo della notifica.
            body (str): Il corpo del messaggio.
            data (dict, optional): Dati aggiuntivi.
            
        Returns:
            List[str]: Lista dei token per cui l'invio è fallito.
        """
        pass
