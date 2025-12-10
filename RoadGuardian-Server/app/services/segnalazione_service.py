from schemas.mappa_schema import SegnalazioneMapDTO
from db.segnalazione_repository import get_segnalazione_by_id, create_segnalazione, delete_segnalazione
from schemas.segnalazione_schema import SegnalazioneInput, SegnalazioneOutputDTO
from models.incident_model import IncidentModel
from datetime import datetime

class SegnalazioneService: 
    def __init__(self, db):
        self.db = db
    def get_segnalazione_details(self, incident_id: str) -> SegnalazioneOutputDTO:
        """Recupera i dettagli di una segnalazione specifica.
        Args:
            incident_id (str): ID della segnalazione
        Returns:
            SegnalazioneOutputDTO: Dettagli della segnalazione
        """
        segnalazione = get_segnalazione_by_id(incident_id)
        if not segnalazione or not segnalazione.get("status", False):
            raise ValueError("Segnalazione non trovata o non attiva")
        
        # Converte ObjectId in stringa e separa datetime
        segnalazione["_id"] = str(segnalazione.get("_id", ""))
        if isinstance(segnalazione.get("incident_date"), datetime):
            dt = segnalazione["incident_date"]
            segnalazione["incident_date"] = dt.date()
            segnalazione["incident_time"] = dt.time()
        
        return SegnalazioneOutputDTO(**segnalazione)

    def create_report(self, user_id: str, report_data: SegnalazioneInput):
        """Crea una nuova segnalazione.
        Args:
            user_id (str): ID dell'utente che crea la segnalazione
            report_data (SegnalazioneInput): Dati della segnalazione
        Returns:
            SegnalazioneOutputDTO: Dettagli della segnalazione creata
        """
        segnalazione_dict = report_data.model_dump()
        segnalazione_dict["user_id"] = user_id
        
        # Converte dict in IncidentModel per il repository
        try:
            segnalazione_model = IncidentModel(**segnalazione_dict)
        except Exception as e:
            raise ValueError(f"Errore validazione segnalazione: {e}")
        
        segnalazione_data = create_segnalazione(segnalazione_model)
        
        # Converte ObjectId in stringa e separa datetime
        segnalazione_data["_id"] = str(segnalazione_data.get("_id", ""))
        if isinstance(segnalazione_data.get("incident_date"), datetime):
            dt = segnalazione_data["incident_date"]
            segnalazione_data["incident_date"] = dt.date()
            segnalazione_data["incident_time"] = dt.time()
        
        return SegnalazioneOutputDTO(**segnalazione_data)
    
    def delete_segnalazione(self, incident_id: str):
        """Elimina (disattiva) una segnalazione specifica.
        Args:
            incident_id (str): ID della segnalazione
        """
        delete_segnalazione(incident_id)

    def get_guidelines_for_incident(self, incident_id: str) -> str:
        """Fornisce linee guida basate sul tipo di segnalazione.
        Args:
            incident_id (str): ID della segnalazione
        Returns:
            str: Linee guida per l'utente
        """
        incident = get_segnalazione_by_id(incident_id)
        if not incident or incident["status"] == False:
            raise ValueError("Segnalazione non trovata")
        
        guidelines = {
            "tamponamento" : "In caso di tamponamento, assicurati di accostare in sicurezza, accendi le luci di emergenza e posiziona il triangolo di segnalazione.",
            "collisione laterale" : "In caso di collisione laterale, verifica le condizioni di tutti i coinvolti, chiama i soccorsi se necessario e scambia le informazioni con gli altri conducenti.",
            "deragliamento" : "Se sei uscito fuori strada, rimani calmo, valuta la situazione e chiama i soccorsi se necessario. Non tentare di rientrare sulla strada da solo.",
            "scontro frontale" : "In caso di scontro frontale, verifica le condizioni di tutti i coinvolti, chiama immediatamente i soccorsi e presta assistenza se possibile.",
            "ribaltamento" : "In caso di ribaltamento, rimani calmo, valuta la situazione e chiama i soccorsi se necessario. Non tentare di uscire dal veicolo se non è sicuro farlo.",
            "investimento" : "In caso di investimento, chiama immediatamente i soccorsi, presta assistenza alla vittima se possibile e segnala l'incidente alle autorità competenti.",
            "ostacolo sulla strada" : "Se incontri un ostacolo sulla strada, rallenta, accendi le luci di emergenza e segnala l'ostacolo agli altri conducenti.",
            "urto con animale" : "In caso di urto con un animale, accosta in sicurezza, valuta le condizioni del veicolo e dell'animale, e chiama i soccorsi se necessario."
        }
        
        category = incident.get("category", "").lower()
        return guidelines.get(category, "Linee guida non disponibili per questa categoria di incidente.")

    def create_fast_report(self, user_id: str, report_data: SegnalazioneInput):
        """Crea una nuova segnalazione veloce.
        Args:
            user_id (str): ID dell'utente che crea la segnalazione
            report_data (SegnalazioneInput): Dati della segnalazione
        Returns:
            SegnalazioneOutputDTO: Dettagli della segnalazione creata
        """
        segnalazione_dict = report_data.model_dump()
        segnalazione_dict["user_id"] = user_id
        
        # Converte dict in IncidentModel per il repository
        try:
            segnalazione_model = IncidentModel(**segnalazione_dict)
        except Exception as e:
            raise ValueError(f"Errore validazione segnalazione: {e}")
        
        segnalazione_data = create_segnalazione(segnalazione_model)
        
        # Converte ObjectId in stringa e separa datetime
        segnalazione_data["_id"] = str(segnalazione_data.get("_id", ""))
        if isinstance(segnalazione_data.get("incident_date"), datetime):
            dt = segnalazione_data["incident_date"]
            segnalazione_data["incident_date"] = dt.date()
            segnalazione_data["incident_time"] = dt.time()
        
        return SegnalazioneOutputDTO(**segnalazione_data)
