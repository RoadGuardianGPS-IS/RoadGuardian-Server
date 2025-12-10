from datetime import date, time, datetime
from typing import Optional, Literal, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

class IncidentModel(BaseModel):
    """
    Modello che rappresenta la struttura dati interna di una segnalazione nel database.
    Include la logica di conversione per MongoDB.
    """
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str #id dell'utente nel db
    incident_date: date
    incident_time: time
    incident_longitude: float
    incident_latitude: float
    seriousness: Literal['low', 'medium', 'high']
    status: bool = True
    category: str #in base ai nomi delle categorie scelte
    description: Optional[str] = None
    img_url: Optional[str] = None 

    @model_validator(mode='before') #Dice a Pydantic di eseguire questa funzione PRIMA di provare a validare i tipi dei campi in maniera automatica, il metodo non dovrà essere chiamato manualmente.
    @classmethod
    def split_datetime(cls, data: Any) -> Any:
        """
        Validatore che gestisce la lettura da MongoDB.
        Se trova un campo 'incident_date' che è un datetime completo (data+ora),
        lo separa automaticamente in 'incident_date' (solo data) e 'incident_time' (solo ora).
        """
        if isinstance(data, dict):
            # Gestione _id -> id
            if "_id" in data and "id" not in data:
                data["id"] = str(data["_id"])

            # Gestione datetime unito -> date + time separati
            if "incident_date" in data and isinstance(data["incident_date"], datetime):
                dt = data["incident_date"]
                data["incident_date"] = dt.date()
                # Se incident_time manca, lo creiamo dal datetime
                if "incident_time" not in data:
                    data["incident_time"] = dt.time()
        return data

    def to_mongo(self) -> dict:
        """
        Converte il modello in un dizionario compatibile con MongoDB.
        Combina data e ora in un unico oggetto datetime per una migliore gestione delle query temporali.
        """
        data = self.model_dump(exclude={"id"})
        # print(f"Prova{type(data)}") # Debug: Controlla il tipo di 'data'
        if self.incident_date and self.incident_time:
            dt = datetime.combine(self.incident_date, self.incident_time)
            data['incident_date'] = dt
            # Rimuove il campo time separato, mantenendo solo il datetime combinato
            if 'incident_time' in data:
                del data['incident_time']
                
        return data

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "user_id": "60d5ecb8b5c9c62b3c1d4e5f",
                "incident_date": "2023-06-01",
                "incident_time": "14:30:00",
                "incident_longitude": 12.4924,
                "incident_latitude": 41.8902,
                "seriousness": "high",
                "status": True,
                "category": "accident",
                "description": "Car accident on Main St.",
                "img_url": "http://example.com/image.jpg"
            }
        }
    )
