from schemas.mappa_schema import SegnalazioneMapDTO, SegnalazioneDettaglioDTO
from db.segnalazione_repository import get_segnalazione_by_id, create_segnalazione, delete_segnalazione
from schemas.segnalazione_schema import SegnalazioneInput, SegnalazioneOutputDTO
from schemas.linee_guida_ai_schema import LineeGuidaAIOutputDTO
from models.incident_model import IncidentModel
from services.linee_guida_ai_adapter import get_guidelines_adapter
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

    def get_ai_guidelines_for_incident(self, incident_id: str) -> list:
        """
        Scopo: Ottiene linee guida comportamentali generate dal modello ML per un incidente.
        
        Utilizza il Trasformatore_dati_segnalazione_for_AI_Model per rilevare automaticamente
        le caratteristiche stradali da OpenStreetMap tramite OSMnx.

        Parametri:
        - incident_id (str): Identificativo della segnalazione.

        Valore di ritorno:
        - LineeGuidaAIOutputDTO: DTO con le linee guida AI e metadati.

        Eccezioni:
        - ValueError: Se la segnalazione non esiste o non è attiva.
        """
        # Recupera i dati dell'incidente
        incident = get_segnalazione_by_id(incident_id)
        if not incident or incident.get("status", False) == False:
            raise ValueError("Segnalazione non trovata o non attiva")
        
        # Ottieni l'adapter
        adapter = get_guidelines_adapter()
        
        try:
            # Ricostruisci un oggetto SegnalazioneInput dai dati dell'incidente
            incident_date_val = incident.get("incident_date")
            incident_time_val = incident.get("incident_time")
            
            # Gestisci datetime unificato
            if isinstance(incident_date_val, datetime):
                incident_time_val = incident_date_val.time()
                incident_date_val = incident_date_val.date()
            
            segnalazione_for_transform = SegnalazioneInput(
                incident_latitude=incident.get("incident_latitude"),
                incident_longitude=incident.get("incident_longitude"),
                incident_date=incident_date_val,
                incident_time=incident_time_val,
                seriousness=incident.get("seriousness", "high"),
                category=incident.get("category", "incidente stradale")
            )
            
            # Usa il Trasformatore per rilevare automaticamente le caratteristiche stradali
            ai_input = adapter.build_ai_input_from_segnalazione(
                segnalazione_input=segnalazione_for_transform,
                use_osm_data=True
            )
            
            # DEBUG: Log dell'input inviato al modello ML
            print(f"[SegnalazioneService] AI Input: Severity={ai_input.Severity}, Incident_Type={ai_input.Incident_Type}, Road_Type={ai_input.Road_Type}, Daylight={ai_input.Daylight}")
            print(f"[SegnalazioneService] AI Input Features: Junction={ai_input.Junction}, Stop={ai_input.Stop}, Traffic_Signal={ai_input.Traffic_Signal}, Crossing={ai_input.Crossing}, Railway={ai_input.Railway}, Roundabout={ai_input.Roundabout}")
                
        except Exception as e:
            print(f"[SegnalazioneService] Errore costruzione input da OSM: {e}, uso fallback")
            # Fallback minimo
            ai_input = adapter.build_ai_input_from_incident(
                seriousness=incident.get("seriousness", "high"),
                category=incident.get("category", ""),
                incident_time=None,
                road_type=None,
                road_features=None
            )
        
        try:
            # Tenta di ottenere le linee guida dall'API ML
            ai_response = adapter.get_guidelines_sync(ai_input)
            return ai_response.guidelines
        except Exception as e:
            # Segnala che le linee guida AI non sono disponibili
            print(f"[SegnalazioneService] Errore API ML: {e}")
            raise ValueError(
                "Linee guida AI non disponibili. "
                "Utilizzare l'endpoint /lineeguida/{incident_id} per le linee guida standard."
            )
