import sys
import types
import pytest


# Create a minimal fake firebase_admin package so importing the adapter works
firebase_admin_mod = types.ModuleType("firebase_admin")
firebase_admin_mod._apps = {}
def _init_app(*args, **kwargs):
    firebase_admin_mod._apps.setdefault('app', True)
firebase_admin_mod.initialize_app = _init_app

credentials_mod = types.ModuleType("firebase_admin.credentials")
class Certificate:
    def __init__(self, *args, **kwargs):
        pass
credentials_mod.Certificate = Certificate

messaging_mod = types.ModuleType("firebase_admin.messaging")
class Notification:
    def __init__(self, title=None, body=None):
        self.title = title
        self.body = body

class Message:
    def __init__(self, notification=None, data=None, token=None):
        self.notification = notification
        self.data = data
        self.token = token

class MulticastMessage:
    def __init__(self, notification=None, data=None, tokens=None):
        self.notification = notification
        self.data = data
        self.tokens = tokens

def _dummy_send(message):
    raise NotImplementedError("send should be monkeypatched in tests")

def _dummy_send_multicast(message):
    raise NotImplementedError("send_multicast should be monkeypatched in tests")

messaging_mod.Notification = Notification
messaging_mod.Message = Message
messaging_mod.MulticastMessage = MulticastMessage
messaging_mod.send = _dummy_send
messaging_mod.send_multicast = _dummy_send_multicast

sys.modules['firebase_admin'] = firebase_admin_mod
sys.modules['firebase_admin.credentials'] = credentials_mod
sys.modules['firebase_admin.messaging'] = messaging_mod


from app.notifications.notify_fcm_adapter import NotifyFCMAdapter


def _run_case(token, title, body, expected_message, should_succeed, monkeypatch, capsys):
    import firebase_admin
    firebase_admin._apps = {'app': True}

    messaging = sys.modules['firebase_admin.messaging']

    if should_succeed:
        def fake_send(msg):
            return "mock_message_id_123"
        monkeypatch.setattr(messaging, 'send', fake_send)
    else:
        def fake_send(msg):
            raise Exception(expected_message)
        monkeypatch.setattr(messaging, 'send', fake_send)

    adapter = NotifyFCMAdapter()
    result = adapter.send_notification(token, title, body)
    captured = capsys.readouterr()

    if should_succeed:
        assert result is True
        assert "NotifyFCMAdapter: Fine fcm" in captured.out
        assert expected_message == "L'invio è riuscito."
    else:
        assert result is False
        assert expected_message in captured.out


def test_case_1_token_none(monkeypatch, capsys):
    """TC_04.1_CM: Token assente
    Test Frame: TOK_P1
    Oracolo: Il token è assente.
    """
    _run_case(None, "Allerta", "Incidente in corso", "Il token è assente.", False, monkeypatch, capsys)


def test_case_2_token_invalid_chars(monkeypatch, capsys):
    """TC_04.2_CM: Formato token non valido
    Test Frame: TOK_C1
    Oracolo: Il token contiene caratteri non ammessi.
    """
    _run_case("@@@###", "Allerta", "Incidente in corso", "Il token contiene caratteri non ammessi.", False, monkeypatch, capsys)


def test_case_3_token_short(monkeypatch, capsys):
    """TC_04.3_CM: Token troppo corto o troppo lungo
    Test Frame: TOK_L1
    Oracolo: Il token è troppo corto o troppo lungo.
    """
    _run_case("SHORT_TOKEN_EXAMPLE_50CHARS_ABC123xyz456DEF789ghi", "Allerta", "Incidente in corso", "Il token è troppo corto o troppo lungo.", False, monkeypatch, capsys)


def test_case_4_title_none(monkeypatch, capsys):
    """TC_04.4_CM: Titolo vuoto o con solo spazi
    Test Frame: TIT_P1, TIT_C1
    Oracolo: Il titolo è vuoto o contiene solo spazi.
    """
    _run_case("VALID_TOKEN_EXAMPLE_150CHARS_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuv", None, "Incidente in corso", "Il titolo è vuoto o contiene solo spazi.", False, monkeypatch, capsys)


def test_case_5_title_too_long(monkeypatch, capsys):
    """TC_04.5_CM: Titolo troppo lungo
    Test Frame: TIT_L1
    Oracolo: Il titolo è troppo lungo.
    """
    _run_case("VALID_TOKEN_EXAMPLE_150CHARS_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuv", "Titolo_esempio_che_supera_il_limite_consentito_di_sessantaquattro_caratteri_80XYZ", "Incidente in corso", "Il titolo è troppo lungo.", False, monkeypatch, capsys)


def test_case_6_body_none(monkeypatch, capsys):
    """TC_04.6_CM: Corpo assente
    Test Frame: BOD_P1
    Oracolo: Il corpo è assente.
    """
    _run_case("VALID_TOKEN_EXAMPLE_150CHARS_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuv", "Allerta", None, "Il corpo è assente.", False, monkeypatch, capsys)


def test_case_7_body_too_long(monkeypatch, capsys):
    """TC_04.7_CM: Corpo troppo corto o troppo lungo
    Test Frame: BOD_L1
    Oracolo: Il corpo è troppo corto o troppo lungo.
    """
    _run_case("VALID_TOKEN_EXAMPLE_150CHARS_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuv", "Allerta", "A" * 1200, "Il corpo è troppo corto o troppo lungo.", False, monkeypatch, capsys)


def test_case_8_success(monkeypatch, capsys):
    """TC_04.8_CM: Invio riuscito
    Test Frame: TOK_P2, TOK_L2, TOK_C2, TIT_P2, TIT_L2, TIT_C2, BOD_P2, BOD_L2, BOD_C2
    Oracolo: L'invio è riuscito
    """
    _run_case("VALID_TOKEN_EXAMPLE_150CHARS_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuv", "Allerta", "Incidente in corso", "L'invio è riuscito.", True, monkeypatch, capsys)
