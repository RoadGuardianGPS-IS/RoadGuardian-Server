
"""
Schema per l'interfacciamento con l'API RG-Linee_Guida_Comportamentali_AI.

Definisce i modelli di input/output e le enumerazioni per la comunicazione
con il servizio ML di generazione linee guida comportamentali.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum

class LineeGuidaAIOutputDTO(BaseModel):
    """DTO per output delle linee guida AI (compatibilità test legacy)."""
    guidelines: List[str]
    model_version: Optional[str] = None
    incident_id: Optional[str] = None
    road_features: Optional[dict] = None
    fallback: Optional[bool] = False

class SeverityLevel(str, Enum):
    """Livelli di gravità supportati dall'API ML."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    UNKNOWN = "Unknown"


class IncidentType(str, Enum):
    """Tipologie di incidente riconosciute dall'API ML."""
    INCENDIO_VEICOLO = "Incendio Veicolo"
    INVESTIMENTO = "Investimento"
    VEICOLO_FUORI_STRADA = "Veicolo Fuori Strada"
    TAMPONAMENTO = "Tamponamento"
    COLLISIONE_OSTACOLO = "Collisione con ostacolo"


class RoadType(str, Enum):
    """Tipologie di strada riconosciute dall'API ML."""
    MOTORWAY_TRUNK = "motorway_trunk"
    PRIMARY_SECONDARY = "primary_secondary"
    RESIDENTIAL = "residential"
    SERVICE = "service"
    TERTIARY = "tertiary"
    LIVING_STREET = "living_street"
    UNCLASSIFIED = "unclassified"


class AIGuidelinesInput(BaseModel):
    """
    Input per la richiesta di linee guida comportamentali all'API ML.
    
    Contiene tutti i dati necessari per classificare lo scenario stradale
    e generare le linee guida di sicurezza appropriate.
    """
    Severity: SeverityLevel = Field(
        default=SeverityLevel.UNKNOWN,
        description="Livello di gravità dell'incidente."
    )
    Incident_Type: Optional[IncidentType] = Field(
        default=None,
        description="Tipologia di incidente. Può essere null se sconosciuto."
    )
    Road_Type: RoadType = Field(
        default=RoadType.UNCLASSIFIED,
        description="Tipologia di strada in cui è avvenuto l'incidente."
    )
    Daylight: bool = Field(
        default=True,
        description="True se l'incidente è avvenuto in condizioni di luce diurna."
    )
    Bump: bool = Field(
        default=False,
        description="Presenza di dosso artificiale nelle vicinanze."
    )
    Crossing: bool = Field(
        default=False,
        description="Presenza di attraversamento pedonale nelle vicinanze."
    )
    Give_Way: bool = Field(
        default=False,
        description="Presenza di segnale di precedenza nelle vicinanze."
    )
    Junction: bool = Field(
        default=False,
        description="Incidente avvenuto in prossimità di un incrocio."
    )
    Railway: bool = Field(
        default=False,
        description="Presenza di passaggio a livello nelle vicinanze."
    )
    Roundabout: bool = Field(
        default=False,
        description="Incidente avvenuto in prossimità di una rotatoria."
    )
    Stop: bool = Field(
        default=False,
        description="Presenza di segnale di stop nelle vicinanze."
    )
    Traffic_Signal: bool = Field(
        default=False,
        description="Presenza di semaforo nelle vicinanze."
    )
    Turning_Loop: bool = Field(
        default=False,
        description="Presenza di inversione a U nelle vicinanze."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "Severity": "High",
                "Incident_Type": "Tamponamento",
                "Road_Type": "primary_secondary",
                "Daylight": True,
                "Bump": False,
                "Crossing": False,
                "Give_Way": False,
                "Junction": True,
                "Railway": False,
                "Roundabout": False,
                "Stop": False,
                "Traffic_Signal": True,
                "Turning_Loop": False
            }
        }
    )


class AIGuidelinesResponse(BaseModel):
    """
    Risposta dell'API ML contenente le linee guida comportamentali.
    """
    guidelines: List[str] = Field(
        default_factory=list,
        description="Lista di linee guida comportamentali generate dal modello ML."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "guidelines": [
                    "Mantieni la calma e accosta in sicurezza se possibile.",
                    "Accendi le luci di emergenza per segnalare la tua posizione.",
                    "Posiziona il triangolo di segnalazione a distanza adeguata."
                ]
            }
        }
    )


