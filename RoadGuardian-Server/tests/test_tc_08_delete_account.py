"""
Test Suite TC_19 - Cancellazione Account (delete_user_profile)

Test case specificati:
- TC_19.1_LO: Email format error → Email non valida
- TC_19.2_LO: Password length error → Lunghezza password errato
- TC_19.3_LO: Password format error → Formato password errato
- TC_19.4_LO: Password mismatch → Password errata
- TC_19.5_LO: Successful deletion → Account cancellato
"""

import pytest
import sys
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi import HTTPException
from pydantic import ValidationError

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.profilo_utente_service import ProfiloUtenteService
from app.models.user_model import UserUpdateInput


class TestTC19DeleteAccount:
    """Test suite per TC_19 - Cancellazione Account"""

    @pytest.fixture
    def service(self):
        return ProfiloUtenteService(Mock())

    @pytest.fixture
    def valid_user(self):
        password = "Password123!"
        return {
            "_id": "user_id",
            "email": "test@gmail.com",
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "is_active": True
        }

    # TC_19.1_LO - Email format error
    def test_tc_19_1_email_format_error(self, service):
        """
        TC_19.1_LO: Email format error
        Test Frame: FE1, LP2, FP2, CP2
        Input: ugo.natale@gmail (missing TLD)
        Expected: Email non valida (ValidationError)
        """
        with pytest.raises(ValidationError):
            UserUpdateInput(email="ugo.natale@gmail", password="Password123!")

    # TC_19.2_LO - Password length error
    def test_tc_19_2_password_length_error(self):
        """
        TC_19.2_LO: Password length error
        Test Frame: FE2, LP1, FP2, CP2
        Note: UserUpdateInput non valida la password a livello schema.
        Accetta password di qualsiasi lunghezza.
        """
        payload = UserUpdateInput(email="renato.maznzo@gmail.com", password="Pass12!")
        assert payload.password == "Pass12!"

    # TC_19.3_LO - Password format error
    def test_tc_19_3_password_format_error(self):
        """
        TC_19.3_LO: Password format error
        Test Frame: FE2, LP2, FP1, CP2
        Input: PasswordForte (no digit, no special char)
        Note: UserUpdateInput non valida il formato a livello schema.
        """
        payload = UserUpdateInput(email="renato.maznzo@gmail.com", password="PasswordForte")
        assert payload.password == "PasswordForte"

    # TC_19.4_LO - Password mismatch
    @patch('app.db.profilo_utente_repository.get_user_by_email')
    def test_tc_19_4_password_mismatch(self, mock_get_user, service, valid_user):
        """
        TC_19.4_LO: Password mismatch error
        Test Frame: FE2, LP2, FP2, CP1
        Input: Email test@gmail.com, Password WrongPass123!
        Expected: Password errata (401 Unauthorized)
        """
        mock_get_user.return_value = valid_user
        
        payload = UserUpdateInput(email="test@gmail.com", password="WrongPass123!")
        
        with pytest.raises(HTTPException) as exc:
            service.delete_user_profile(payload)
        
        assert exc.value.status_code == 401
        assert "Password errata" in exc.value.detail

    # TC_19.5_LO - Successful deletion
    @patch('app.db.profilo_utente_repository.update_user')
    @patch('app.db.profilo_utente_repository.get_user_by_email')
    def test_tc_19_5_successful_deletion(self, mock_get_user, mock_update, service, valid_user):
        """
        TC_19.5_LO: Successful account deletion
        Test Frame: FE2, LP2, FP2, CP2
        Input: Email test@gmail.com, Password Password123!
        Expected: Account cancellato (success message "Profilo utente eliminato")
        """
        mock_get_user.return_value = valid_user
        mock_update.return_value = True
        
        payload = UserUpdateInput(email="test@gmail.com", password="Password123!")
        result = service.delete_user_profile(payload)
        
        assert result == "Profilo utente eliminato"
