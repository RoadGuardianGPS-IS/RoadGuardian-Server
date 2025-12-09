from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time, datetime
from typing import Optional, Dict, Literal


class SegnalazioneManualeInput(BaseModel):
    """
    Schema per la creazione di una nuova segnalazione.
    Contiene solo i dati forniti dal client.
    Viene utilizzata dall'API per validare i dati in ingresso.
    """
    incident_date: Optional[date] = Field(
        default_factory=date.today, 
        description="Data in cui è avvenuto l'incidente (formato YYYY-MM-DD). Se non fornita, viene usata la data corrente del Server."
    )
    incident_time: Optional[time] = Field(
        default_factory=lambda: datetime.now().time().replace(microsecond=0), 
        description="Orario in cui è avvenuto l'incidente (formato HH:MM:SS). Se non fornito, viene usato l'orario corrente del Server."
    )
    incident_longitude: float = Field(
        ..., 
        description="Longitudine della posizione dell'incidente (valore decimale).", 
        ge=-180.0, 
        le=180.0
    )
    incident_latitude: float = Field(
        ..., 
        description="Latitudine della posizione dell'incidente (valore decimale).", 
        ge=-90.0, 
        le=90.0
    )
    seriousness: Literal['low', 'medium', 'high'] = Field(
        ..., 
        description="Livello di gravità dell'incidente. Valori ammessi: 'low', 'medium', 'high'."
    )
    category: str = Field(
        ..., 
        description="Categoria dell'incidente (es. 'incidente stradale', 'tamponamento', 'collisione laterale').",
        min_length=1,
        max_length=50
    )
    description: Optional[str] = Field(
        None, 
        description="Descrizione testuale opzionale dell'incidente.", 
        max_length=500
    )
    img_url: Optional[str] = Field(
        None, 
        description="URL opzionale di un'immagine allegata alla segnalazione."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "incident_date": "2025-12-09",
                "incident_time": "10:30:00",
                "incident_longitude": 12.496366,
                "incident_latitude": 41.902782,
                "seriousness": "high",
                "category": "incidente",
                "description": "Tamponamento a catena.",
                "img_url": "https://example.com/images/incident.jpg"
            }
        }
    )

class SegnalazioneOutputDTO(BaseModel):
    """
    Schema che definisce la struttura dati di una segnalazione di incidente in risposta al Client.
    Utilizzato per la validazione e la serializzazione dei dati.
    Viene utilizzata dall'API per restituire i dati al client.
    """
    id: Optional[str] = Field(
        default=None, 
        alias="_id", 
        description="Identificativo univoco della segnalazione (MongoDB ObjectId)."
    )
    user_id: str = Field(
        ..., 
        description="Identificativo univoco dell'utente."
    )
    incident_date: date = Field(
        ..., 
        description="Data in cui è avvenuto l'incidente (formato YYYY-MM-DD)."
    )
    incident_time: time = Field(
        ..., 
        description="Orario in cui è avvenuto l'incidente (formato HH:MM:SS)."
    )
    incident_longitude: float = Field(
        ..., 
        description="Longitudine della posizione dell'incidente (valore decimale).", 
        ge=-180.0, 
        le=180.0
    )
    incident_latitude: float = Field(
        ..., 
        description="Latitudine della posizione dell'incidente (valore decimale).", 
        ge=-90.0, 
        le=90.0
    )
    seriousness: Literal['low', 'medium', 'high'] = Field(
        ..., 
        description="Livello di gravità dell'incidente. Valori ammessi: 'low', 'medium', 'high'."
    )
    status: bool = Field(
        default=True, 
        description="Stato della segnalazione: True se creata/attiva, False se risolta/inattiva."
    )
    category: str = Field(
        ..., 
        description="Categoria dell'incidente (es. 'incidente stradale', 'tamponamento', 'collisione laterale').",
        min_length=1,
        max_length=50
    )
    description: Optional[str] = Field(
        None, 
        description="Descrizione testuale opzionale dell'incidente.", 
        max_length=500
    )
    img_url: Optional[str] = Field(
        None, 
        description="URL opzionale di un'immagine allegata alla segnalazione."
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "user_id": "60d5ecb8b5c9c62b3c1d4e5f",
                "incident_date": "2025-12-09",
                "incident_time": "10:30:00",
                "incident_longitude": 12.496366,
                "incident_latitude": 41.902782,
                "seriousness": "alta",
                "status": True,
                "category": "incidente",
                "description": "Tamponamento a catena.",
                "img_url": "https://example.com/images/incident.jpg"
            }
        }
    )

    def get_posizione_GPS(self) -> Dict[str, float]:
        """
        Scopo: Restituisce le coordinate GPS della segnalazione in un formato strutturato.
        Parametri: Nessuno.
        Valore di ritorno: Dizionario con chiavi 'latitudine' e 'longitudine' contenente i valori float del campo correlato al campo chiave.
        Eccezioni: Nessuna eccezione prevista.
        """
        return {
            "latitudine": self.incident_latitude,
            "longitudine": self.incident_longitude
        }

class SegnalazioneStatoUpdate(BaseModel): #da eliminare facendo cambiare l'update dell'api con una chiamata a deletesegnalazione nel service
    """
    Schema per l'aggiornamento dello stato di una segnalazione.
    """
    status: bool = Field(
        ..., 
        description="Nuovo stato della segnalazione: True (attiva) o False (risolta/inattiva)."
    )


