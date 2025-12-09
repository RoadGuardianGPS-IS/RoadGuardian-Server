from typing import List
from schemas.mappa_schema import SegnalazioneMapDTO
from db.segnalazione_repository import get_segnalazione_by_status, get_segnalazione_by_category

class MappaService:
    def __init__(self, db):
        self.db = db
    def get_active_incidents(self) -> List[SegnalazioneMapDTO]:
        """Recupera tutte le segnalazioni attive.
        Returns:
            List[SegnalazioneMapDTO]: Lista di segnalazioni attive, formattate per la mappa
        """
        # Recupera tutte le segnalazioni attive dal repository
        all_segnalazioni = get_segnalazione_by_status(True)
        
        result = []
        for segnalazione in all_segnalazioni:
            # Converte ObjectId di MongoDB in stringa per Pydantic
            segnalazione["_id"] = str(segnalazione.get("_id", ""))
            segnalazione_dto = SegnalazioneMapDTO(**segnalazione)
            result.append(segnalazione_dto)
        return result
    
    def get_filtered_incidents(self, tipi_incidente: List[str]) -> List[SegnalazioneMapDTO]:
        """Recupera segnalazioni attive filtrate per tipo di incidente.
        Args:
            tipi_incidente (List[str]): Tipi di incidente da filtrare
        Returns:
            List[SegnalazioneMapDTO]: Lista di segnalazioni filtrate
        """
        result = []
        # Per ogni tipo di incidente richiesto, recupera le segnalazioni corrispondenti
        if( tipi_incidente is None or len(tipi_incidente) == 0):
            return self.get_active_incidents()
        for tipo in tipi_incidente:
            segnalazioni_by_category = get_segnalazione_by_category(tipo)
            # Aggiungi le segnalazioni trovate alla lista dei risultati e li trasforma in SegnalazioneMapDTO
            for segnalazione in segnalazioni_by_category:
                    # Converte ObjectId di MongoDB in stringa per Pydantic
                    segnalazione["_id"] = str(segnalazione.get("_id", ""))
                    segnalazione_dto = SegnalazioneMapDTO(**segnalazione)
                    result.append(segnalazione_dto)
        return result