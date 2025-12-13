from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date, time, datetime
from typing import Optional, Dict, Literal


class SegnalazioneInput(BaseModel):
    """Input per creazione segnalazione: dati client validati e normalizzati."""
    user_id: Optional[str] = Field(
        None,
        description="Identificativo univoco dell'utente.",
        min_length=1,
        max_length=24
    )
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
    seriousness: Literal['high'] = Field(
        'high', 
        description="Livello di gravità dell'incidente. Valore ammesso: 'high'."
    )
    category: str = Field(
        'incidente stradale', 
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

    @field_validator('incident_date')
    @classmethod
    def validate_incident_date(cls, v):
        """
        Scopo: Verifica che l'anno di `incident_date` sia ≥ 2025.

        Parametri:
        - v (date|None): Valore della data incidente.

        Valore di ritorno:
        - date|None: La data valida o None.

        Eccezioni:
        - ValueError: Se l'anno è inferiore a 2025.
        """
        if v is not None and v.year < 2025:
            raise ValueError('incident_date year must be >= 2025')
        return v

    @field_validator('incident_time')
    @classmethod
    def validate_incident_time(cls, v):
        """
        Scopo: Valida che `incident_time` sia un oggetto `time` corretto.

        Parametri:
        - v (time|None): Orario dell'incidente.

        Valore di ritorno:
        - time|None: L'orario valido o None.

        Eccezioni:
        - ValueError: Se non è un oggetto `time`.
        """
        if v is not None and not isinstance(v, time):
            raise ValueError('incident_time must be a valid time object in format HH:MM:SS')
        return v

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
    """DTO risposta: dati completi segnalazione per il client, senza trasformazioni lato client."""
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
        'high', 
        description="Livello di gravità dell'incidente. Valori ammessi: 'low', 'medium', 'high'."
    )
    status: bool = Field(
        default=True, 
        description="Stato della segnalazione: True se creata/attiva, False se risolta/inattiva."
    )
    category: Optional[str] = Field(
        None, 
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
        Scopo: Restituisce coordinate GPS della segnalazione in formato strutturato.

        Parametri:
        - Nessuno.

        Valore di ritorno:
        - Dict[str, float]: Chiavi 'latitudine' e 'longitudine'.

        Eccezioni:
        - Nessuna.
        """
        return {
            "latitudine": self.incident_latitude,
            "longitudine": self.incident_longitude
        }


# class SegnalazioneStatoUpdate(BaseModel): #da eliminare facendo cambiare l'update dell'api con una chiamata a deletesegnalazione nel service
#     """
#     Schema per l'aggiornamento dello stato di una segnalazione.
#     """
#     status: bool = Field(
#         ..., 
#         description="Nuovo stato della segnalazione: True (attiva) o False (risolta/inattiva)."
#     )

