from datetime import date, time, datetime
from typing import Optional, Literal, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

class IncidentModel(BaseModel):
    """Rappresenta una segnalazione e gestisce conversioni per MongoDB.

    Descrizione: Modello interno per segnalazioni con helper per MongoDB.
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
        """Scopo: Normalizza i dati in ingresso letti da MongoDB separando
        un `datetime` unificato in `incident_date` (date) e `incident_time` (time).

        Parametri:
        - data (Any): Dizionario raw proveniente da MongoDB o payload utente.

        Valore di ritorno:
        - Any: Dizionario modificato con campi `incident_date` e `incident_time` separati
            (se applicabile). Mantiene altri campi invariati.

        Eccezioni:
        - None specificate: eventuali eccezioni derivano da input non-dizionari
            e vengono propagate (TypeError se non dict).
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
        """Scopo: Serializzare l'istanza in un dizionario compatibile con MongoDB.

        Parametri:
        - self: Istanza di `IncidentModel` contenente data e ora separate.

        Valore di ritorno:
        - dict: Dizionario pronto per l'inserimento in MongoDB. Combina
            `incident_date` e `incident_time` in un unico `datetime` sotto la chiave
            `incident_date` e rimuove `incident_time` se presente.

        Eccezioni:
        - TypeError: se `incident_date` o `incident_time` non sono tipi compatibili
            per `datetime.combine`.
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
