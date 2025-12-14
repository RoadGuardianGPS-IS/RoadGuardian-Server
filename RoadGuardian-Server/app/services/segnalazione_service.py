from schemas.mappa_schema import SegnalazioneMapDTO
from db.segnalazione_repository import get_segnalazione_by_id, create_segnalazione, delete_segnalazione
from schemas.segnalazione_schema import SegnalazioneInput, SegnalazioneOutputDTO
from models.incident_model import IncidentModel
from datetime import datetime

class SegnalazioneService: 
    """Gestisce creazione, lettura e cancellazione di segnalazioni d'incidente."""
    def __init__(self, db):
        self.db = db
    def get_segnalazione_details(self, incident_id: str) -> SegnalazioneOutputDTO:
        """
        Scopo: Recupera i dettagli di una segnalazione attiva dato il suo ID.

        Parametri:
        - incident_id (str): Identificativo univoco della segnalazione.

        Valore di ritorno:
        - SegnalazioneOutputDTO: Dati normalizzati della segnalazione (ObjectId→str, data/ora separati).

        Eccezioni:
        - ValueError: Se la segnalazione non esiste o non è attiva.
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
        """
        Scopo: Valida, costruisce il modello e crea una nuova segnalazione manuale.

        Parametri:
        - user_id (str): ID dell'utente che effettua la segnalazione.
        - report_data (SegnalazioneInput): Dati della segnalazione da persistere.

        Valore di ritorno:
        - SegnalazioneOutputDTO: Dati della segnalazione appena creata con campi normalizzati.

        Eccezioni:
        - ValueError: Se la validazione del modello fallisce.
        - Exception: Eventuali eccezioni propagate dallo strato di persistenza.
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
        """
        Scopo: Esegue la cancellazione/disattivazione (soft delete) della segnalazione indicata.

        Parametri:
        - incident_id (str): Identificativo della segnalazione da disattivare.

        Valore di ritorno:
        - None: Nessun valore restituito.

        Eccezioni:
        - Exception: Eventuali errori propagati dal repository durante l'operazione.
        """
        delete_segnalazione(incident_id)

    def get_guidelines_for_incident(self, incident_id: str) -> str:
        """
        Scopo: Restituisce linee guida operative in base alla categoria della segnalazione.

        Parametri:
        - incident_id (str): Identificativo della segnalazione da cui dedurre la categoria.

        Valore di ritorno:
        - str: Testo contenente le indicazioni di comportamento.

        Eccezioni:
        - ValueError: Se la segnalazione non esiste o non è attiva.
        """
        incident = get_segnalazione_by_id(incident_id)
        if not incident or incident["status"] == False:
            raise ValueError("Segnalazione non trovata")
        
        guidelines = {
            "tamponamento" : "In caso di tamponamento, assicurati di accostare in sicurezza, accendi le luci di emergenza e posiziona il triangolo di segnalazione.",
            "collisione con ostacolo" : "In caso di collisione laterale, verifica le condizioni di tutti i coinvolti, chiama i soccorsi se necessario e scambia le informazioni con gli altri conducenti.",
            "veicolo fuori strada" : "Se un veicolo è fuori strada, mantieni la calma, valuta la situazione e chiama i soccorsi se ci sono feriti o pericoli maggiori.",
            "investimeto" : "In caso di investimento, fermati immediatamente, presta assistenza alla vittima e chiama i soccorsi.",
            "incendio veicolo" : "In caso di incendio del veicolo, allontanati in sicurezza, chiama i vigili del fuoco e non tentare di spegnere l'incendio da solo se non sei adeguatamente preparato."
            }
        
        category = incident.get("category", "").lower()
        return guidelines.get(category, "Linee guida non disponibili per questa categoria di incidente.")

    def create_fast_report(self, user_id: str, report_data: SegnalazioneInput):
        """
        Scopo: Crea rapidamente una segnalazione con gli stessi controlli della creazione manuale.

        Parametri:
        - user_id (str): ID dell'utente che effettua la segnalazione veloce.
        - report_data (SegnalazioneInput): Dati minimi della segnalazione.

        Valore di ritorno:
        - SegnalazioneOutputDTO: Dati della segnalazione creata con campi normalizzati.

        Eccezioni:
        - ValueError: Se la validazione del modello fallisce.
        - Exception: Eventuali errori propagati dallo strato di persistenza.
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
