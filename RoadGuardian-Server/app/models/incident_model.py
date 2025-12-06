from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class IncidentModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str #sarebbe l'username 
    #date: datetime.date
    #time: datetime.time
    incident_date: date
    incident_time: time
    incident_longitude: float
    incident_latitude: float
    seriousness: str #in base ai nomi delle gravitá decidere quali opzioni mettere nel form lato client 
    # False = segnalazione non attiva, True = segnalazione attiva
    status: bool = True
    category: str #in base ai nomi delle categorie scelte
    description: Optional[str] = None
    img_url: Optional[str] = None 

    def to_mongo(self) -> dict: # metodo per rendere la data memorizzabile da mongoDB senza salvarla come stringa
        data = self.model_dump(exclude={"id"})
        print(f"Prova{type(data)}")
        if self.incident_date and self.incident_time:
            dt = datetime.combine(self.incident_date, self.incident_time)
            data['incident_date'] = dt
            if 'incident_time' in data:
                del data['incident_time']
        return data

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "RenatoPunta69",
                "date": "2023-06-01",
                "time": "14:30:00",
                "incident_longitude": 12.4924,
                "incident_latitude": 41.8902,
                "seriousness": "high",
                "status": True,
                "category": "accident",
                "description": "Car accident on Main St.",
                "img_url": "http://example.com/image.jpg" #non so come vogliamo salvare le immagini
            }
        }

class IncidentCreateInput(BaseModel): #creato per backend ma da cambiare in base alle funzionalitá
    """Modello per la creazione (Input dal client)"""
    user_id: str
    seriousness: str
    category: str
    description: Optional[str] = None
    img_url: Optional[str] = None

class IncidentDeleteInput(BaseModel): #creato per backend ma da cambiare in base alle funzionalitá
    """Modello per l'aggiornamento (Input dal client)"""
    status: bool

#Lasciamo da creare la classe per l'update generale alla backend per gestirsi come meglio vogliono i dati opzionali per le API etc.... oppure dite a lorenzo di scrivermi e vengo in call :D

#class IncidentUpdateInput(BaseModel):