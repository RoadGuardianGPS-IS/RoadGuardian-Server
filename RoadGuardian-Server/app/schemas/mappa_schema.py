from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional
from datetime import date, time

class PosizioneGPS(BaseModel):
    """
    Schema per rappresentare una posizione GPS.
    Utilizzato come input per filtrare le segnalazioni in base alla posizione dell'utente.
    """
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

class SegnalazioneMapDTO(BaseModel):
    """
    Schema ottimizzato per la visualizzazione delle segnalazioni sulla mappa.
    Contiene solo le informazioni essenziali per il rendering dei marker.
    """
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

class SegnalazioneDettaglioDTO(SegnalazioneMapDTO):
    """
    Schema esteso per la visualizzazione dei dettagli completi di una segnalazione.
    Eredita da SegnalazioneMapDTO e aggiunge i campi descrittivi.
    Utilizzato nell'endpoint /dettagli/{incident_id}.
    """
    incident_date: date = Field(
        ..., 
        description="Data in cui è avvenuto l'incidente (formato YYYY-MM-DD)."
    )
    incident_time: time = Field(
        ..., 
        description="Orario in cui è avvenuto l'incidente (formato HH:MM:SS)."
    )
    status: bool = Field(
        ..., 
        description="Stato della segnalazione: True se attiva, False se risolta/inattiva."
    )
    description: Optional[str] = Field(
        None, 
        description="Descrizione testuale dell'incidente."
    )
    img_url: Optional[str] = Field(
        None, 
        description="URL dell'immagine allegata."
    )
