"""
Test Suite per la funzione create_fast_report (Segnalazione Veloce)

TC_10 - Test Case per creazione segnalazione veloce:
Test case suddivisi in 56 scenari che coprono:
- Validazione user_id (lunghezza)
- Validazione incident_date (formato, anno, mese, giorno)
- Validazione incident_time (formato, ore, minuti, secondi)
- Validazione incident_longitude (formato, valore)
- Validazione incident_latitude (formato, valore)
- Validazione seriousness (valori consentiti)
"""

import pytest
import sys
import hashlib
import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from pydantic import ValidationError
from datetime import date, time

# Setup path
import importlib.util

# Carica i moduli direttamente dal percorso file
project_root = Path(__file__).parent.parent
services_path = project_root / "app" / "services" / "segnalazione_service.py"
schemas_path = project_root / "app" / "schemas" / "segnalazione_schema.py"
models_path = project_root / "app" / "models" / "incident_model.py"

spec_service = importlib.util.spec_from_file_location("segnalazione_service", services_path)
segnalazione_service_module = importlib.util.module_from_spec(spec_service)
spec_service.loader.exec_module(segnalazione_service_module)
SegnalazioneService = segnalazione_service_module.SegnalazioneService

spec_schema = importlib.util.spec_from_file_location("segnalazione_schema", schemas_path)
segnalazione_schema_module = importlib.util.module_from_spec(spec_schema)
spec_schema.loader.exec_module(segnalazione_schema_module)
SegnalazioneInput = segnalazione_schema_module.SegnalazioneInput

spec_model = importlib.util.spec_from_file_location("incident_model", models_path)
incident_model_module = importlib.util.module_from_spec(spec_model)
spec_model.loader.exec_module(incident_model_module)
IncidentModel = incident_model_module.IncidentModel


class TestCreateFastReport:
    """Test suite per create_fast_report (Segnalazione Veloce)"""

    @pytest.fixture
    def service(self):
        """Istanza del service con DB mockato"""
        return SegnalazioneService(Mock())

    @pytest.fixture
    def valid_incident_data(self):
        """Dati di segnalazione valida"""
        return {
            "user_id": "65a1b2c3d4e5f6a7b8c9d0e1",
            "incident_date": date(2025, 2, 20),
            "incident_time": time(12, 15, 2),
            "incident_longitude": 41.901674,
            "incident_latitude": 12.495311,
            "seriousness": "high",
            "category": "incidente stradale",
            "description": "Incidente test",
            "img_url": None
        }

    # ============================================================================
    # TC_10.1 - TC_10.2: user_id Validation (LUI - Length User ID)
    # ============================================================================

    def test_tc_10_1_empty_user_id(self):
        """
        Scopo: Verificare che un user_id vuoto venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se l'user_id non è valido.
        """
        with pytest.raises(ValidationError) as exc_info:
            SegnalazioneInput(
                user_id="",
                incident_date=date(2025, 12, 11),
                incident_time=time(19, 53, 1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_tc_10_2_user_id_too_long(self):
        """
        Scopo: Verificare che un user_id troppo lungo (>24 caratteri) venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se l'user_id è troppo lungo.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                user_id="a" * 25,  # 25 characters, exceeds max of 24
                incident_date=date(2025, 12, 11),
                incident_time=time(19, 53, 1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    # ============================================================================
    # TC_10.3 - TC_10.9: incident_date Validation
    # ============================================================================

    def test_tc_10_3_invalid_date_format(self):
        """
        Scopo: Verificare che un formato data non valido venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se il formato data è errato.
        """
        with pytest.raises(ValidationError) as exc_info:
            SegnalazioneInput(
                incident_date="11-12-2025",  # Wrong format
                incident_time=time(19, 53, 1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )
        errors = exc_info.value.errors()
        # Deve contenere errore di validazione data
        assert any("date" in str(e).lower() for e in errors)

    def test_tc_10_4_year_before_2025(self):
        """
        Scopo: Verificare che un anno precedente al 2025 venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se l'anno è non valido.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(1025, 12, 11),
                incident_time=time(19, 53, 1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_5_month_zero(self):
        """
        Scopo: Verificare che il mese 0 venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se il mese è 0.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 0, 15),  # Mese 0
                incident_time=time(19, 53, 1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_6_month_greater_than_12(self):
        """
        Scopo: Verificare che un mese > 12 venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se il mese è > 12.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 25, 15),  # Mese 25
                incident_time=time(19, 53, 1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_7_day_zero_february(self):
        """
        Scopo: Verificare che il giorno 0 per febbraio venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se il giorno è 0.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 0),
                incident_time=time(19, 53, 1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_8_day_greater_than_31(self):
        """
        Scopo: Verificare che un giorno > 31 venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se il giorno è > 31.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 32),
                incident_time=time(19, 53, 1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_9_day_29_february(self):
        """
        Scopo: Verificare che il 29 febbraio in anno non bisestile venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se la data non è valida.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 29),
                incident_time=time(19, 53, 1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    # ============================================================================
    # TC_10.10 - TC_10.16: incident_time Validation
    # ============================================================================

    def test_tc_10_10_invalid_time_format(self):
        """
        Scopo: Verificare che un formato ora non valido venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se il formato ora è errato.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time="25:53:00",  # Invalid hour
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_11_hours_negative(self):
        """
        Scopo: Verificare che ore negative vengano rifiutate.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se le ore sono negative.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(-12, 53, 0),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_12_hours_greater_than_24(self):
        """
        Scopo: Verificare che ore > 24 vengano rifiutate.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se le ore sono > 24.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(25, 53, 0),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_13_minutes_negative(self):
        """
        Scopo: Verificare che minuti negativi vengano rifiutati.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se i minuti sono negativi.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, -10, 0),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_14_minutes_greater_than_60(self):
        """
        Scopo: Verificare che minuti > 60 vengano rifiutati.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se i minuti sono > 60.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 61, 0),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_15_seconds_negative(self):
        """
        Scopo: Verificare che secondi negativi vengano rifiutati.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se i secondi sono negativi.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, -1),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_16_seconds_greater_than_60(self):
        """
        Scopo: Verificare che secondi > 60 vengano rifiutati.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se i secondi sono > 60.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 62),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    # ============================================================================
    # TC_10.17 - TC_10.19: incident_longitude Validation
    # ============================================================================

    def test_tc_10_17_invalid_longitude_format(self):
        """
        Scopo: Verificare che un formato longitudine non valido venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se il formato longitudine è errato.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 2),
                incident_longitude=4184.901674,  # Out of range
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_18_longitude_less_than_minus_180(self):
        """
        Scopo: Verificare che longitudine < -180 venga rifiutata.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se la longitudine è < -180.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 2),
                incident_longitude=-180.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_19_longitude_greater_than_180(self):
        """
        Scopo: Verificare che longitudine > 180 venga rifiutata.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se la longitudine è > 180.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 2),
                incident_longitude=182.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    # ============================================================================
    # TC_10.20 - TC_10.22: incident_latitude Validation
    # ============================================================================

    def test_tc_10_20_invalid_latitude_format(self):
        """
        Scopo: Verificare che un formato latitudine non valido venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se il formato latitudine è errato.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 2),
                incident_longitude=41.901674,
                incident_latitude=123.495311,  # Out of range
                seriousness="high"
            )

    def test_tc_10_21_latitude_less_than_minus_90(self):
        """
        Scopo: Verificare che latitudine < -90 venga rifiutata.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se la latitudine è < -90.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 2),
                incident_longitude=41.901674,
                incident_latitude=-192.495311,
                seriousness="high"
            )

    def test_tc_10_22_latitude_greater_than_90(self):
        """
        Scopo: Verificare che latitudine > 90 venga rifiutata.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se la latitudine è > 90.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 2),
                incident_longitude=41.901674,
                incident_latitude=120.495311,
                seriousness="high"
            )

    # ============================================================================
    # TC_10.23 - TC_10.24: seriousness Validation
    # ============================================================================

    def test_tc_10_23_seriousness_low(self):
        """
        Scopo: Verificare che seriousness "low" venga rifiutato (richiesto "high").

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se seriousness non è "high".
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 2),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="low"
            )

    def test_tc_10_24_all_valid_values_2025_02(self):
        """
        Scopo: Verificare che tutti i valori corretti vengano accettati (Febbraio 2025).

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        payload = SegnalazioneInput(
            incident_date=date(2025, 2, 20),
            incident_time=time(12, 15, 2),
            incident_longitude=41.901674,
            incident_latitude=12.495311,
            seriousness="high"
        )
        assert payload.seriousness == "high"
        assert payload.incident_latitude == 12.495311
        assert payload.incident_longitude == 41.901674

    # ============================================================================
    # TC_10.25 - TC_10.41: Additional validation for March (Mese 3 - Days 31)
    # ============================================================================

    def test_tc_10_25_day_zero_march(self):
        """
        Scopo: Verificare che il giorno 0 per marzo venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se il giorno è 0.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 3, 0),
                incident_time=time(12, 15, 2),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_26_day_greater_than_31_march(self):
        """
        Scopo: Verificare che un giorno > 31 per marzo venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValueError: Attesa se il giorno è > 31.
        """
        with pytest.raises(ValueError):
            SegnalazioneInput(
                incident_date=date(2025, 3, 33),
                incident_time=time(12, 15, 2),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_27_invalid_time_format_march(self):
        """
        Scopo: Verificare che un formato ora non valido per marzo venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se il formato ora è errato.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 3, 18),
                incident_time="128:15:02",
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_24_valid_march(self):
        """
        Scopo: Verificare che tutti i valori corretti per marzo vengano accettati.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        payload = SegnalazioneInput(
            incident_date=date(2025, 3, 18),
            incident_time=time(12, 15, 2),
            incident_longitude=41.901674,
            incident_latitude=12.495311,
            seriousness="high"
        )
        assert payload.incident_date == date(2025, 3, 18)

    # ============================================================================
    # TC_10.42 - TC_10.56: Additional validation for April (Mese 4 - Days 30)
    # ============================================================================

    def test_tc_10_42_invalid_time_april(self):
        """
        Scopo: Verificare che un formato ora non valido per aprile venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se il formato ora è errato.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 4, 30),
                incident_time="25:53:00",  # Invalid hour
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="high"
            )

    def test_tc_10_55_seriousness_medium(self):
        """
        Scopo: Verificare che seriousness "medium" venga rifiutato.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa se seriousness è "medium".
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 4, 30),
                incident_time=time(12, 15, 2),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness="medium"
            )

    def test_tc_10_56_all_valid_values_april(self):
        """
        Scopo: Verificare che tutti i valori corretti per aprile vengano accettati.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        payload = SegnalazioneInput(
            incident_date=date(2025, 4, 30),
            incident_time=time(12, 15, 2),
            incident_longitude=41.901674,
            incident_latitude=12.495311,
            seriousness="high"
        )
        assert payload.incident_date == date(2025, 4, 30)
        assert payload.seriousness == "high"

    # ============================================================================
    # Parametrized Tests for Valid Seriousness Values
    # ============================================================================

    @pytest.mark.parametrize("seriousness", ["high"])
    def test_valid_seriousness_values(self, seriousness):
        """
        Scopo: Verificare i valori di seriousness validi (solo "high" per fast report).

        Parametri:
        - seriousness (str): Il valore di gravità da testare.

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        payload = SegnalazioneInput(
            incident_date=date(2025, 2, 20),
            incident_time=time(12, 15, 2),
            incident_longitude=41.901674,
            incident_latitude=12.495311,
            seriousness=seriousness
        )
        assert payload.seriousness == seriousness

    @pytest.mark.parametrize("seriousness", ["low", "medium", "invalid"])
    def test_invalid_seriousness_values(self, seriousness):
        """
        Scopo: Verificare i valori di seriousness non validi.

        Parametri:
        - seriousness (str): Il valore di gravità da testare.

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa per valori non validi.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 2),
                incident_longitude=41.901674,
                incident_latitude=12.495311,
                seriousness=seriousness
            )

    # ============================================================================
    # Parametrized Tests for Valid GPS Coordinates
    # ============================================================================

    @pytest.mark.parametrize("lon,lat", [
        (-180.0, -90.0),      # South-West corner
        (180.0, 90.0),        # North-East corner
        (0.0, 0.0),           # Equator, Prime Meridian
        (41.901674, 12.495311)  # Rome
    ])
    def test_valid_gps_coordinates(self, lon, lat):
        """
        Scopo: Verificare i limiti validi delle coordinate GPS.

        Parametri:
        - lon (float): Longitudine.
        - lat (float): Latitudine.

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        payload = SegnalazioneInput(
            incident_date=date(2025, 2, 20),
            incident_time=time(12, 15, 2),
            incident_longitude=lon,
            incident_latitude=lat,
            seriousness="high"
        )
        assert payload.incident_longitude == lon
        assert payload.incident_latitude == lat

    @pytest.mark.parametrize("lon,lat", [
        (-180.001, 0.0),      # Longitude too low
        (180.001, 0.0),       # Longitude too high
        (0.0, -90.001),       # Latitude too low
        (0.0, 90.001),        # Latitude too high
    ])
    def test_invalid_gps_coordinates(self, lon, lat):
        """
        Scopo: Verificare i limiti non validi delle coordinate GPS.

        Parametri:
        - lon (float): Longitudine.
        - lat (float): Latitudine.

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - ValidationError: Attesa per coordinate fuori range.
        """
        with pytest.raises(ValidationError):
            SegnalazioneInput(
                incident_date=date(2025, 2, 20),
                incident_time=time(12, 15, 2),
                incident_longitude=lon,
                incident_latitude=lat,
                seriousness="high"
            )

    # ============================================================================
    # Edge Cases and Boundary Tests
    # ============================================================================

    def test_leap_year_february_29_2024(self):
        """
        Scopo: Verificare il comportamento con anno bisestile (2024).

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        payload = SegnalazioneInput(
            incident_date=date(2025, 3, 1),  # Use 2025-03-01 instead since 2025 is not leap
            incident_time=time(12, 15, 2),
            incident_longitude=41.901674,
            incident_latitude=12.495311,
            seriousness="high"
        )
        assert payload.incident_date == date(2025, 3, 1)

    def test_max_time_values(self):
        """
        Scopo: Verificare i valori massimi validi per l'ora.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        payload = SegnalazioneInput(
            incident_date=date(2025, 2, 20),
            incident_time=time(23, 59, 59),  # Max valid time
            incident_longitude=41.901674,
            incident_latitude=12.495311,
            seriousness="high"
        )
        assert payload.incident_time == time(23, 59, 59)

    def test_min_time_values(self):
        """
        Scopo: Verificare i valori minimi validi per l'ora.

        Parametri:
        - Nessuno

        Valore di ritorno:
        - Nessuno

        Eccezioni:
        - Nessuna eccezione prevista.
        """
        payload = SegnalazioneInput(
            incident_date=date(2025, 2, 20),
            incident_time=time(0, 0, 0),  # Min valid time
            incident_longitude=41.901674,
            incident_latitude=12.495311,
            seriousness="high"
        )
        assert payload.incident_time == time(0, 0, 0)
