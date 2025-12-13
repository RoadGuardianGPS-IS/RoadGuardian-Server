from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import date, time

class PosizioneGPS(BaseModel):
    """Rappresenta una posizione GPS per filtri e centering mappa."""
    latitudine: float = Field(
        ..., 
        description="Latitudine della posizione (valore decimale).", 
        ge=-90.0, 
        le=90.0
    )
    longitudine: float = Field(
        ..., 
        description="Longitudine della posizione (valore decimale).", 
        ge=-180.0, 
        le=180.0
    )

class UserPositionUpdate(BaseModel):
    """Aggiornamento periodico posizione utente e token per notifiche."""
    latitudine: float = Field(..., ge=-90.0, le=90.0)
    longitudine: float = Field(..., ge=-180.0, le=180.0)
    fcm_token: Optional[str] = Field(None, description="Token FCM per le notifiche push.")

class SegnalazioneMapDTO(BaseModel):
    """DTO essenziale per marker mappa con categoria, gravità e coordinate."""
    id: str = Field(
        ..., 
        alias="_id", 
        description="Identificativo univoco della segnalazione (MongoDB ObjectId)."
    )
    category: str = Field(
        ..., 
        description="Categoria dell'incidente (es. 'incidente', 'lavori', 'traffico')."
    )
    seriousness: Literal['low', 'medium', 'high'] = Field(
        ..., 
        description="Livello di gravità dell'incidente. Valori ammessi: 'low', 'medium', 'high'."
    )
    incident_latitude: float = Field(
        ..., 
        description="Latitudine della posizione dell'incidente.", 
        ge=-90.0, 
        le=90.0
    )
    incident_longitude: float = Field(
        ..., 
        description="Longitudine della posizione dell'incidente.", 
        ge=-180.0, 
        le=180.0
    )
    # Opzionale: potresti voler includere anche la data/ora per mostrare "quanto tempo fa"
    # incident_time: Optional[time] = ...

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "60d5ecb8b5c9c62b3c1d4e5f",
                "category": "incidente",
                "seriousness": "high",
                "incident_latitude": 41.902782,
                "incident_longitude": 12.496366
            }
        }
    )


