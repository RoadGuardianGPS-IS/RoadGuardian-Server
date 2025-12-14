"""
Test Suite per il metodo get_filtered_incidents del MappaService.
Implementa i test case TC_18.1_GM - TC_18.6_GM per il filtraggio dei tipi di incidente.

Test Case:
- TC_18.1_GM: Tipo incidente con formato non valido (FT1)
- TC_18.2_GM: Connessione assente (CN1)
- TC_18.3_GM: Errore nel recupero dati (CN2 DS_ERROR)
- TC_18.4_GM: Nessuna segnalazione corrisponde (FT_OK VT_OK CN_OK DS_EMPTY)
- TC_18.5_GM: Filtro valido con almeno una segnalazione (FT_OK VT_OK CN_OK DS_OK)
- TC_18.6_GM: Filtro valido ma sistema lento (CN_OK DS_DELAY)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId
from fastapi import HTTPException
from app.services.mappa_service import MappaService


class TestGetFilteredIncidents:
    """Suite di test per MappaService.get_filtered_incidents"""

    @pytest.fixture
    def service(self):
        """Crea un'istanza del servizio con un mock del database"""
        return MappaService(Mock())

    # TC 18.1 - Tipo incidente con formato non valido
    @patch('app.services.mappa_service.get_segnalazione_by_category')
    def test_tc_18_1_invalid_format(self, mock_get_category, service):
        """
        TC_18.1_GM: Tipo incidente con formato non valido
        Test Frame: FT1
        
        Verifica che quando il filtro per tipo di incidente ha un formato non valido,
        il sistema restituisca un errore e il filtro non venga applicato.
        """
        # Input non valido: contiene caratteri speciali non permessi
        invalid_incident_type = "123###Tamponamento"
        
        # Simula che il repository sollevi un'eccezione per formato non valido
        mock_get_category.side_effect = ValueError("Formato incident_type non valido: contiene caratteri non permessi")
        
        # Verifica che venga sollevata un'eccezione
        with pytest.raises(ValueError) as excinfo:
            service.get_filtered_incidents([invalid_incident_type])
        
        assert "Formato incident_type non valido" in str(excinfo.value)
        mock_get_category.assert_called_once_with(invalid_incident_type)

    # TC 18.2 - Connessione assente
    @patch('app.services.mappa_service.get_segnalazione_by_category')
    def test_tc_18_2_connection_absent(self, mock_get_category, service):
        """
        TC_18.2_GM: Connessione assente
        Test Frame: CN1
        
        Verifica che quando la connessione al database è assente,
        il sistema restituisca un errore di connessione.
        """
        # Simula connessione assente
        mock_get_category.side_effect = ConnectionError("Impossibile caricare la mappa: connessione assente")
        
        # Verifica che venga sollevata un'eccezione di connessione
        with pytest.raises(ConnectionError) as excinfo:
            service.get_filtered_incidents(["Tamponamento"])
        
        assert "connessione assente" in str(excinfo.value)

    # TC 18.3 - Errore nel recupero dati
    @patch('app.services.mappa_service.get_segnalazione_by_category')
    def test_tc_18_3_internal_error_during_retrieval(self, mock_get_category, service):
        """
        TC_18.3_GM: Errore nel recupero dati
        Test Frame: CN2 DS_ERROR
        
        Verifica che quando il sistema incontra un errore interno durante il recupero dati,
        restituisca un messaggio di errore appropriato.
        """
        # Simula errore interno nel sistema
        mock_get_category.side_effect = Exception("Impossibile recuperare le segnalazioni. Riprova più tardi")
        
        # Verifica che venga sollevata un'eccezione
        with pytest.raises(Exception) as excinfo:
            service.get_filtered_incidents(["Incendio veicolo"])
        
        assert "Impossibile recuperare le segnalazioni" in str(excinfo.value)

    # TC 18.4 - Nessuna segnalazione corrisponde al filtro
    @patch('app.services.mappa_service.get_segnalazione_by_category')
    def test_tc_18_4_no_matching_incidents(self, mock_get_category, service):
        """
        TC_18.4_GM: Nessuna segnalazione corrisponde al filtro
        Test Frame: FT_OK VT_OK CN_OK DS_EMPTY
        
        Verifica che quando il filtro è corretto ma nessuna segnalazione lo soddisfa,
        il sistema restituisca una lista vuota.
        """
        # Filtro valido ma nessuna segnalazione corrispondente
        mock_get_category.return_value = []
        
        result = service.get_filtered_incidents(["Investimento"])
        
        assert isinstance(result, list)
        assert len(result) == 0
        mock_get_category.assert_called_once_with("Investimento")

    # TC 18.5 - Filtro valido con almeno una segnalazione corrispondente
    @patch('app.services.mappa_service.get_segnalazione_by_category')
    def test_tc_18_5_valid_filter_with_results(self, mock_get_category, service):
        """
        TC_18.5_GM: Filtro valido con almeno una segnalazione corrispondente
        Test Frame: FT_OK VT_OK CN_OK DS_OK
        
        Verifica che quando il filtro è corretto e esiste almeno una segnalazione
        corrispondente, il sistema restituisca le segnalazioni filtrate correttamente.
        """
        # Prepara i dati mock
        example_oid = ObjectId()
        fake_segnalazione = {
            "_id": example_oid,
            "category": "Tamponamento",
            "seriousness": "high",
            "incident_latitude": 41.123456,
            "incident_longitude": 12.123456,
        }
        
        mock_get_category.return_value = [fake_segnalazione]
        
        result = service.get_filtered_incidents(["Tamponamento"])
        
        assert isinstance(result, list)
        assert len(result) == 1
        dto = result[0]
        
        # Verifica che la segnalazione sia stata filtrata correttamente
        assert dto.category == "Tamponamento"
        assert dto.seriousness == "high"
        assert dto.incident_latitude == 41.123456
        assert dto.incident_longitude == 12.123456
        mock_get_category.assert_called_once_with("Tamponamento")

    # TC 18.6 - Filtro valido ma sistema lento nel recupero dati
    @patch('app.services.mappa_service.get_segnalazione_by_category')
    def test_tc_18_6_slow_system_response(self, mock_get_category, service):
        """
        TC_18.6_GM: Filtro valido ma sistema lento nel recupero dati
        Test Frame: CN_OK DS_DELAY
        
        Verifica che quando la connessione è attiva ma il server risponde lentamente,
        il metodo comunque restituisca i dati corretti una volta disponibili.
        
        Nota: La simulazione del loader e del delay è responsabilità del client/UI.
        Qui verifichiamo che il servizio restituisca i dati corretti.
        """
        # Prepara i dati mock
        example_oid = ObjectId()
        fake_segnalazione = {
            "_id": example_oid,
            "category": "Collisione ostacolo",
            "seriousness": "medium",
            "incident_latitude": 43.123456,
            "incident_longitude": 11.123456,
        }
        
        # Simula risposta lenta (il mock ritorna comunque i dati)
        mock_get_category.return_value = [fake_segnalazione]
        
        result = service.get_filtered_incidents(["Collisione ostacolo"])
        
        assert isinstance(result, list)
        assert len(result) == 1
        dto = result[0]
        
        # Verifica che i dati siano corretti nonostante il delay
        assert dto.category == "Collisione ostacolo"
        assert dto.seriousness == "medium"
        assert dto.incident_latitude == 43.123456
        assert dto.incident_longitude == 11.123456
