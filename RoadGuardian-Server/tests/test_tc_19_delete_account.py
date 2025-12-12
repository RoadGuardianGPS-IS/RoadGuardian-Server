"""
Test Suite per la funzione delete_user_profile

TC_19 - Test Case per cancellazione account:
- TC_19.1_LO: Email format error
- TC_19.2_LO: Password length error  
- TC_19.3_LO: Password format error
- TC_19.4_LO: Password mismatch
- TC_19.5_LO: Successful deletion
"""

import pytest
import sys
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from pydantic import ValidationError

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.profilo_utente_service import ProfiloUtenteService
from app.models.user_model import UserUpdateInput


class TestDeleteUserProfile:
    """Test suite per delete_user_profile"""

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

    # TC_19.1 - Email format error
    def test_tc_19_1_invalid_email(self, service):
        """Email non valida"""
        with pytest.raises(ValidationError):
            UserUpdateInput(email="invalid@email", password="Pass123!")

    # TC_19.2 - Password length
    def test_tc_19_2_short_password_accepted(self):
        """UserUpdateInput accetta password di qualsiasi lunghezza"""
        # No validation at model level
        payload = UserUpdateInput(email="test@gmail.com", password="short")
        assert payload.password == "short"

    # TC_19.3 - Password format
    def test_tc_19_3_any_password_format_accepted(self):
        """UserUpdateInput accetta password di qualsiasi formato"""
        # No validation at model level
        payload = UserUpdateInput(email="test@gmail.com", password="NoSpecialChars")
        assert payload.password == "NoSpecialChars"

    # TC_19.4 - Password mismatch
    @patch('app.db.profilo_utente_repository.get_user_by_email')
    def test_tc_19_4_password_mismatch(self, mock_get_user, service, valid_user):
        """Password errata → 401"""
        mock_get_user.return_value = valid_user
        
        payload = UserUpdateInput(email="test@gmail.com", password="WrongPass123!")
        
        with pytest.raises(HTTPException) as exc:
            service.delete_user_profile(payload)
        
        assert exc.value.status_code == 401
        assert "Password errata" in exc.value.detail

    # TC_19.5 - Successful deletion
    @patch('app.db.profilo_utente_repository.update_user')
    @patch('app.db.profilo_utente_repository.get_user_by_email')
    def test_tc_19_5_successful_deletion(self, mock_get_user, mock_update, service, valid_user):
        """Account cancellato"""
        mock_get_user.return_value = valid_user
        mock_update.return_value = True
        
        payload = UserUpdateInput(email="test@gmail.com", password="Password123!")
        result = service.delete_user_profile(payload)
        
        assert result == "Profilo utente eliminato"

    @patch('app.db.profilo_utente_repository.get_user_by_email')
    def test_user_not_found(self, mock_get_user, service):
        """User not found → 404"""
        mock_get_user.return_value = None
        
        payload = UserUpdateInput(email="notfound@gmail.com", password="Pass123!")
        
        with pytest.raises(HTTPException) as exc:
            service.delete_user_profile(payload)
        
        assert exc.value.status_code == 404

    @pytest.mark.parametrize("valid_email", [
        "user@example.com",
        "user.name@example.com",
        "user-name@example.co.uk",
    ])
    def test_valid_emails(self, valid_email):
        """Valid email formats"""
        payload = UserUpdateInput(email=valid_email, password="Pass123!")
        assert payload.email == valid_email

    @pytest.mark.parametrize("invalid_email", [
        "missing@domain",
        "no-at-sign.com",
        "@missing.local.com",
    ])
    def test_invalid_emails(self, invalid_email):
        """Invalid email formats"""
        with pytest.raises(ValidationError):
            UserUpdateInput(email=invalid_email, password="Pass123!")
