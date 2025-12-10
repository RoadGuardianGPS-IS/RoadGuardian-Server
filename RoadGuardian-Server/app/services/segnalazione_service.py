from schemas.mappa_schema import SegnalazioneMapDTO
from db.segnalazione_repository import get_segnalazione_by_id, create_segnalazione, delete_segnalazione
from schemas.segnalazione_schema import SegnalazioneInput, SegnalazioneOutputDTO
class SegnalazioneService: 
    def __init__(self, db):
        self.db = db
    def get_segnalazione_details(self, incident_id: str) -> SegnalazioneMapDTO:
        """Recupera i dettagli di una segnalazione specifica.
        Args:
            incident_id (str): ID della segnalazione
        Returns:
            SegnalazioneMapDTO: Dettagli della segnalazione
        """
        segnalazione = get_segnalazione_by_id(incident_id)
        if not segnalazione or not segnalazione.get("status", False):
            raise ValueError("Segnalazione non trovata o non attiva")
        return SegnalazioneMapDTO(**segnalazione)

    def create_report(user_id: str, report_data: SegnalazioneInput):
        """Crea una nuova segnalazione.
        Args:
            user_id (str): ID dell'utente che crea la segnalazione
            report_data (SegnalazioneInput): Dati della segnalazione
        Returns:
            SegnalazioneOutputDTO: Dettagli della segnalazione creata
        """
        segnalazione_dict = report_data.model_dump()
        segnalazione_dict["user_id"] = user_id
        segnalazione_data = create_segnalazione(segnalazione_dict) 

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
            incident_type (str): Tipo di segnalazione
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

        return guidelines.get(incident["category"])

    def create_fast_report(user_id: str, report_data: SegnalazioneInput):
        """Crea una nuova segnalazione.
        Args:
            user_id (str): ID dell'utente che crea la segnalazione
            report_data (SegnalazioneInput): Dati della segnalazione
        Returns:
            SegnalazioneOutputDTO: Dettagli della segnalazione creata
        """
        segnalazione_dict = report_data.model_dump()
        segnalazione_dict["user_id"] = user_id
        segnalazione_data = create_segnalazione(segnalazione_dict) 

        return SegnalazioneOutputDTO(**segnalazione_data)
