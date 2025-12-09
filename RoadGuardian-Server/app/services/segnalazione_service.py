from schemas.mappa_schema import SegnalazioneMapDTO
from db.segnalazione_repository import get_segnalazione_by_id
class SegnalazioneService: 
    def __init__(self, db):
        self.db = db
    def get_incident_details(self, incident_id: str) -> SegnalazioneMapDTO:
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