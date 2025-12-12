from typing import List
import math
from schemas.mappa_schema import SegnalazioneMapDTO, UserPositionUpdate
from services.mappa_segnalazione_facade import MappaSegnalazioneFacade
from notifications.notify_fcm_adapter import NotifyFCMAdapter

class MappaService:
    def __init__(self, db):
        self.db = db
        self.notification_adapter = NotifyFCMAdapter()
        # Iniezione del Facade
        self.segnalazione_facade = MappaSegnalazioneFacade()

    def get_active_incidents(self) -> List[SegnalazioneMapDTO]:
        """Recupera tutte le segnalazioni attive.
        Returns:
            List[SegnalazioneMapDTO]: Lista di segnalazioni attive, formattate per la mappa
        """
        # Recupera tutte le segnalazioni attive TRAMITE IL FACADE
        all_segnalazioni = self.segnalazione_facade.get_segnalazioni_attive_per_mappa()
        
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
            # Usa il Facade invece della chiamata diretta al repository
            segnalazioni_by_category = self.segnalazione_facade.get_segnalazioni_per_categoria(tipo)
            # Aggiungi le segnalazioni trovate alla lista dei risultati e li trasforma in SegnalazioneMapDTO
            for segnalazione in segnalazioni_by_category:
                    # Converte ObjectId di MongoDB in stringa per Pydantic
                    segnalazione["_id"] = str(segnalazione.get("_id", ""))
                    segnalazione_dto = SegnalazioneMapDTO(**segnalazione)
                    result.append(segnalazione_dto)
        return result

    def process_user_position(self, position_update: UserPositionUpdate):
        """
        Elabora l'aggiornamento della posizione dell'utente.
        Controlla se ci sono segnalazioni attive entro 3 km e invia notifiche.
        """
        if not position_update.fcm_token:
            return # Nessun token per inviare notifiche

        active_incidents = self.get_active_incidents()
        
        for incident in active_incidents:
            distance = self._calculate_distance(
                position_update.latitudine, 
                position_update.longitudine,
                incident.incident_latitude,
                incident.incident_longitude
            )
            
            if distance <= 3.0: # 3 km
                # Invia notifica
                print("MappaService: Nelle vicinanze della segnalazione")
                title = "Attenzione: Segnalazione vicina!"
                body = f"C'è un {incident.category} a {distance:.1f} km da te."
                data = {"incident_id": incident.id}
                
                if(self.notification_adapter.send_notification(
                    token=position_update.fcm_token,
                    title=title,
                    body=body,
                    data=data)== True):
                    print("MappaService: Notifica Inviata")
                    
            print("MappaService: Posizione Aggiornata")

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcola la distanza in km tra due punti GPS usando la formula di Haversine.
        """
        R = 6371.0 # Raggio della Terra in km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance