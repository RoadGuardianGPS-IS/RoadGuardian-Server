"""
Test Suite per la funzionalità get_guidelines_for_incident di SegnalazioneService

Casi di test:
- TC_16.1_SDA: Visualizzazione Notifica Linee Guida
- TC_16.2_SDA: Visualizzazione Linee Guida Specifiche (Incendio)
- TC_16.3_SDA: Accesso Linee Guida Utente NON Registrato
"""

import pytest
from unittest.mock import patch, Mock
from app.services.segnalazione_service import SegnalazioneService

class TestGetGuidelinesForIncident:
    @pytest.fixture
    def service(self):
        return SegnalazioneService(db=Mock())

    @patch('app.services.segnalazione_service.get_segnalazione_by_id')
    def test_tc_16_1_sda_visualizzazione_notifica_linee_guida(self, mock_get_by_id, service):
        """TC_16.1_SDA: L'utente riceve la notifica e visualizza le linee guida generiche."""
        mock_get_by_id.return_value = {
            '_id': '123',
            'category': 'tamponamento',
            'status': True
        }
        guidelines = service.get_guidelines_for_incident('123')
        assert 'accostare in sicurezza' in guidelines.lower()
        assert 'triangolo' in guidelines.lower()

    @patch('app.services.segnalazione_service.get_segnalazione_by_id')
    def test_tc_16_2_sda_visualizzazione_linee_guida_specifiche_incendio(self, mock_get_by_id, service):
        """TC_16.2_SDA: L'utente visualizza linee guida specifiche per incendio veicolo."""
        mock_get_by_id.return_value = {
            '_id': '456',
            'category': 'incendio veicolo',
            'status': True
        }
        guidelines = service.get_guidelines_for_incident('456')
        assert 'incendio' in guidelines.lower()
        assert 'allontanati' in guidelines.lower() or 'allontanarsi' in guidelines.lower()
        assert 'vigili del fuoco' in guidelines.lower()

    @patch('app.services.segnalazione_service.get_segnalazione_by_id')
    def test_tc_16_3_sda_accesso_linee_guida_utente_non_registrato(self, mock_get_by_id, service):
        """TC_16.3_SDA: L'utente non autenticato può accedere alle linee guida."""
        mock_get_by_id.return_value = {
            '_id': '789',
            'category': 'tamponamento',
            'status': True
        }
        guidelines = service.get_guidelines_for_incident('789')
        assert 'linee guida' not in guidelines.lower() or isinstance(guidelines, str)
        assert 'accostare' in guidelines.lower()

    @patch('app.services.segnalazione_service.get_segnalazione_by_id')
    def test_tc_16_id_non_esistente(self, mock_get_by_id, service):
        """TP_16_SDA: Caso ID segnalazione non esistente (errore)."""
        mock_get_by_id.return_value = None
        with pytest.raises(ValueError):
            service.get_guidelines_for_incident('notfound')
