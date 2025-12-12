"""
Test Suite per la funzione get_segnalazione_details

TC_06_DPL - Test Case per visualizzazione dettagli segnalazione:
- TC_06.1_DPL: ID non esiste
- TC_06.2_DPL: ID esiste

Tabella Parametri TP_06_DPL:

ID:
- Formato: "^(true|false)$"
- Esistenza [ID]: 
  1. Non esistente = false [error]
  2. Esistente = true [PROPERTY_ID_OK]
"""

import pytest
import sys
import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, date, time
from bson import ObjectId

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Aggiungi anche la directory app per gli import relativi
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app"))

# Carica i moduli direttamente dal percorso file
services_path = project_root / "app" / "services" / "segnalazione_service.py"

spec_service = importlib.util.spec_from_file_location("segnalazione_service", services_path)
segnalazione_service_module = importlib.util.module_from_spec(spec_service)
sys.modules['segnalazione_service'] = segnalazione_service_module  # Registra in sys.modules
spec_service.loader.exec_module(segnalazione_service_module)
SegnalazioneService = segnalazione_service_module.SegnalazioneService

# Importa SegnalazioneOutputDTO dal modulo app.schemas
from app.schemas.segnalazione_schema import SegnalazioneOutputDTO


class TestGetSegnalazioneDetails:
    """Test suite per get_segnalazione_details"""

    @pytest.fixture
    def service(self):
        return SegnalazioneService(Mock())

    @pytest.fixture
    def valid_segnalazione(self):
        """Fixture per una segnalazione valida"""
        example_oid = ObjectId()
        return {
            "_id": example_oid,
            "user_id": "user123",
            "category": "tamponamento",
            "seriousness": "high",
            "description": "Incidente grave sulla A1",
            "incident_latitude": 41.9028,
            "incident_longitude": 12.4964,
            "incident_date": datetime(2025, 12, 10, 14, 30, 0),
            "status": True
        }

    # ============================================================================
    # TC_06.1_DPL - ID non esiste
    # Test Frame: ID1 (Non esistente)
    # ============================================================================

    @patch('segnalazione_service.get_segnalazione_by_id')
    def test_tc_06_1_dpl_id_non_esiste(self, mock_get_by_id, service):
        """
        TC_06.1_DPL: ID non esiste
        Test Frame: ID1
        
        Pre-condizione: 
        - L'utente è connesso ad internet
        - L'utente è coperto da segnale GPS
        
        Flusso Eventi:
        1. L'utente apre l'app
        2. L'utente clicca su un'incidente per visualizzarne i dettagli
        3. Il server riceve l'ID dell'incidente
        
        Input: ID non esistente
        Oracolo: Incidente non trovato o non attivo (ValueError)
        """
        # Mock: simula che la segnalazione non esista
        mock_get_by_id.return_value = None
        
        with pytest.raises(ValueError) as exc:
            service.get_segnalazione_details("id_non_esistente")
        
        assert "Segnalazione non trovata o non attiva" in str(exc.value)

    # ============================================================================
    # TC_06.2_DPL - ID esiste
    # Test Frame: ID2 (Esistente)
    # ============================================================================

    @patch('segnalazione_service.get_segnalazione_by_id')
    def test_tc_06_2_dpl_id_esiste(self, mock_get_by_id, service, valid_segnalazione):
        """
        TC_06.2_DPL: ID esiste
        Test Frame: ID2
        
        Pre-condizione: 
        - L'utente è connesso ad internet
        - L'utente è coperto da segnale GPS
        
        Flusso Eventi:
        1. L'utente apre l'app
        2. L'utente clicca su un'incidente per visualizzarne i dettagli
        3. Il server riceve l'ID dell'incidente
        
        Input: ID esistente
        Oracolo: Mostra i dettagli dell'incidente selezionato, quali:
        - descrizione
        - gravità
        - coordinate GPS
        - distanza dalle coordinate GPS correnti
        - data e ora
        - sotto-sezione per visualizzare le linee guida comportamentali della segnalazione
        """
        mock_get_by_id.return_value = valid_segnalazione.copy()
        
        result = service.get_segnalazione_details(str(valid_segnalazione["_id"]))
        
        # Verifica che il risultato sia un SegnalazioneOutputDTO
        assert result.__class__.__name__ == 'SegnalazioneOutputDTO'
        
        # Verifica i campi principali
        assert result.id == str(valid_segnalazione["_id"])
        assert result.user_id == valid_segnalazione["user_id"]
        assert result.category == valid_segnalazione["category"]
        assert result.seriousness == valid_segnalazione["seriousness"]
        assert result.description == valid_segnalazione["description"]
        assert result.incident_latitude == valid_segnalazione["incident_latitude"]
        assert result.incident_longitude == valid_segnalazione["incident_longitude"]
        
        # Verifica separazione data e ora
        assert result.incident_date == date(2025, 12, 10)
        assert result.incident_time == time(14, 30, 0)
        
        # Verifica lo status
        assert result.status == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
