"""
Test Suite per la funzione get_active_incidents

TC_13 - Test Case per visualizzazione segnalazioni attive:
- TC_13.1_AS: Nessuna segnalazione attiva
- TC_13.2_AS: Una o più segnalazioni attive
"""

import pytest
from unittest.mock import Mock, patch
from bson import ObjectId
from app.services.mappa_service import MappaService


class TestGetActiveIncidents:
    """Suite di test per MappaService.get_active_incidents"""

    @pytest.fixture
    def service(self):
        return MappaService(Mock())

    # TC 13.1 - Nessuna segnalazione attiva
    @patch('app.services.mappa_service.get_segnalazione_by_status')
    def test_tc_13_1_no_active_incidents(self, mock_get_status, service):
        """Nessuna segnalazione attiva: restituisci lista vuota"""
        mock_get_status.return_value = []

        result = service.get_active_incidents()

        assert isinstance(result, list)
        assert len(result) == 0

    # TC 13.2 - Una o più segnalazioni attive
    @patch('app.services.mappa_service.get_segnalazione_by_status')
    def test_tc_13_2_with_active_incidents(self, mock_get_status, service):
        """Una o più segnalazioni attive: restituisci lista di DTO correttamente popolati"""
        example_oid = ObjectId()
        fake_segnalazione = {
            "_id": example_oid,
            "category": "incendio veicolo",
            "seriousness": "high",
            "incident_latitude": 41.123456,
            "incident_longitude": 12.123456,
        }

        mock_get_status.return_value = [fake_segnalazione]

        result = service.get_active_incidents()

        assert isinstance(result, list)
        assert len(result) == 1
        dto = result[0]

        # Verifica campi base
        assert getattr(dto, "id") == str(example_oid)
        assert dto.category == fake_segnalazione["category"]
        assert dto.seriousness == fake_segnalazione["seriousness"]
        assert dto.incident_latitude == fake_segnalazione["incident_latitude"]
        assert dto.incident_longitude == fake_segnalazione["incident_longitude"]
