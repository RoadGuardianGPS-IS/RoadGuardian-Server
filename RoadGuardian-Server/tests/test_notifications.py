import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Configurazione path per importare i moduli
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
app_dir = os.path.join(parent_dir, 'app')
sys.path.insert(0, parent_dir)
sys.path.insert(0, app_dir)

from app.services.mappa_service import MappaService
from app.schemas.mappa_schema import UserPositionUpdate

class TestNotifications(unittest.TestCase):

    def setUp(self):
        self.mock_db = MagicMock()
        
        # Patching NotifyFCMAdapter in mappa_service
        self.patcher_adapter = patch('app.services.mappa_service.NotifyFCMAdapter')
        self.MockAdapter = self.patcher_adapter.start()
        self.mock_adapter_instance = self.MockAdapter.return_value
        
        # Patching get_segnalazione_by_status in mappa_service
        self.patcher_repo = patch('app.services.mappa_service.get_segnalazione_by_status')
        self.mock_get_segnalazione = self.patcher_repo.start()

        self.service = MappaService(self.mock_db)

    def tearDown(self):
        self.patcher_adapter.stop()
        self.patcher_repo.stop()

    def test_notification_sent_when_close(self):
        """Testa che la notifica venga inviata se l'utente è vicino a una segnalazione (< 3km)"""
        
        # Setup dati segnalazione (es. Roma Centro)
        incident_lat = 41.9028
        incident_lon = 12.4964
        
        fake_incident = {
            "_id": "fake_id_123",
            "category": "Incidente",
            "seriousness": "high",
            "incident_latitude": incident_lat,
            "incident_longitude": incident_lon,
            "incident_date": "2023-10-27",
            "incident_time": "10:00:00",
            "status": True,
            "user_id": "user123"
        }
        
        # Il repository restituisce questa segnalazione
        self.mock_get_segnalazione.return_value = [fake_incident]

        # Utente molto vicino (es. 100 metri)
        user_pos = UserPositionUpdate(
            latitudine=41.9030, 
            longitudine=12.4965, 
            fcm_token="fake_token_123"
        )

        # Esecuzione
        self.service.process_user_position(user_pos)

        # Verifica
        self.mock_adapter_instance.send_notification.assert_called_once()
        call_args = self.mock_adapter_instance.send_notification.call_args
        self.assertEqual(call_args.kwargs['token'], "fake_token_123")
        self.assertIn("vicina", call_args.kwargs['title'])

    def test_no_notification_when_far(self):
        """Testa che la notifica NON venga inviata se l'utente è lontano (> 3km)"""
        
        # Setup dati segnalazione (es. Roma Centro)
        incident_lat = 41.9028
        incident_lon = 12.4964
        
        fake_incident = {
            "_id": "fake_id_123",
            "category": "Incidente",
            "seriousness": "high",
            "incident_latitude": incident_lat,
            "incident_longitude": incident_lon,
            "incident_date": "2023-10-27",
            "incident_time": "10:00:00",
            "status": True,
            "user_id": "user123"
        }
        
        self.mock_get_segnalazione.return_value = [fake_incident]

        # Utente lontano (es. Milano)
        user_pos = UserPositionUpdate(
            latitudine=45.4642, 
            longitudine=9.1900, 
            fcm_token="fake_token_123"
        )

        # Esecuzione
        self.service.process_user_position(user_pos)

        # Verifica
        self.mock_adapter_instance.send_notification.assert_not_called()

    def test_no_notification_without_token(self):
        """Testa che non venga fatto nulla se manca il token FCM"""
        
        user_pos = UserPositionUpdate(
            latitudine=41.9028, 
            longitudine=12.4964, 
            fcm_token=None
        )

        self.service.process_user_position(user_pos)

        # Non deve nemmeno chiamare il DB se non c'è token (ottimizzazione opzionale, 
        # ma nel codice attuale controlla il token prima)
        self.mock_adapter_instance.send_notification.assert_not_called()

if __name__ == '__main__':
    unittest.main()
