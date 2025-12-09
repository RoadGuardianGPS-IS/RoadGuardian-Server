import unittest
import sys
import os
import pprint
from datetime import date, time, datetime
from pydantic import ValidationError

# Configurazione path per importare i moduli
current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
app_dir = os.path.join(parent_dir, 'app')

# Aggiungiamo sia la root del progetto che la cartella app per supportare diversi stili di import
sys.path.insert(0, parent_dir)
sys.path.insert(0, app_dir)

# Import dei moduli da testare
# Nota: Assicurati che il path sia configurato correttamente per eseguire i test
from app.schemas.segnalazione_schema import SegnalazioneManualeInput, SegnalazioneOutputDTO, SegnalazioneStatoUpdate
from app.schemas.mappa_schema import PosizioneGPS, SegnalazioneMapDTO, SegnalazioneDettaglioDTO
from app.models.incident_model import IncidentModel

class TestCategoryPartition(unittest.TestCase):

    def setUp(self):
        print(f"\n--- Esecuzione Test: {self._testMethodName} ---")
        if self._testMethodDoc:
            print(f"Descrizione: {self._testMethodDoc.strip()}")

    def tearDown(self):
        failed = False
        if hasattr(self, '_outcome'):
            # Controllo errori (compatibilità varie versioni Python)
            if hasattr(self._outcome, 'errors') and self._outcome.errors:
                failed = True
            elif hasattr(self._outcome, 'result'):
                result = self._outcome.result
                if any(t == self for t, _ in result.failures + result.errors):
                    failed = True
        
        if failed:
            print(f"[FAIL] Test {self._testMethodName} FALLITO.")
        else:
            print(f"[OK] Test {self._testMethodName} completato con successo.")

    # ==========================================================================
    # PARTIZIONE 1: VALIDAZIONE COORDINATE (IncidentSchema & MappaSchema)
    # Categorie:
    # - Valide: -90 <= lat <= 90, -180 <= lon <= 180
    # - Invalid Lat: < -90 o > 90
    # - Invalid Lon: < -180 o > 180
    # ==========================================================================

    def test_coordinate_valide(self):
        """Test input con coordinate valide (Equivalenza Valida)"""
        input_data = {
            "incident_longitude": 12.4924,
            "incident_latitude": 41.8902,
            "seriousness": "low",
            "category": "test",
            "description": "test"
        }
        print(f"Input Data:\n{pprint.pformat(input_data, indent=4)}")
        schema = SegnalazioneManualeInput(**input_data)
        print(f"Output Schema:\n{pprint.pformat(schema.model_dump(mode='json'), indent=4)}")
        self.assertEqual(schema.incident_latitude, 41.8902)

    def test_latitudine_fuori_limite_inferiore(self):
        """Test Boundary: Latitudine < -90 (Non Valido)"""
        input_data = {
            "incident_longitude": 12.0,
            "incident_latitude": -90.1, # Invalid
            "seriousness": "low",
            "category": "test"
        }
        print(f"Input Data:\n{pprint.pformat(input_data, indent=4)}")
        with self.assertRaises(ValidationError) as context:
            SegnalazioneManualeInput(**input_data)
        print(f"Errore Pydantic Rilevato:\n{context.exception}")
        self.assertIn("Input should be greater than or equal to -90", str(context.exception))

    def test_latitudine_fuori_limite_superiore(self):
        """Test Boundary: Latitudine > 90 (Non Valido)"""
        input_data = {
            "incident_longitude": 12.0,
            "incident_latitude": 90.1, # Invalid
            "seriousness": "low",
            "category": "test"
        }
        print(f"Input Data:\n{pprint.pformat(input_data, indent=4)}")
        with self.assertRaises(ValidationError) as context:
            SegnalazioneManualeInput(**input_data)
        print(f"Errore Pydantic Rilevato:\n{context.exception}")

    def test_longitudine_fuori_limite(self):
        """Test Boundary: Longitudine > 180 (Non Valido)"""
        input_data = {
            "incident_longitude": 180.1, # Invalid
            "incident_latitude": 45.0,
            "seriousness": "low",
            "category": "test"
        }
        print(f"Input Data:\n{pprint.pformat(input_data, indent=4)}")
        with self.assertRaises(ValidationError) as context:
            SegnalazioneManualeInput(**input_data)
        print(f"Errore Pydantic Rilevato:\n{context.exception}")

    # ==========================================================================
    # PARTIZIONE 2: ENUM SERIOUSNESS (IncidentSchema)
    # Categorie:
    # - Valide: 'low', 'medium', 'high'
    # - Invalide: Qualsiasi altra stringa
    # ==========================================================================

    def test_seriousness_valida(self):
        """Test valori enum validi"""
        for level in ['low', 'medium', 'high']:
            input_data = {
                "incident_longitude": 10.0, 
                "incident_latitude": 10.0, 
                "seriousness": level, 
                "category": "test"
            }
            print(f"Input Data:\n{pprint.pformat(input_data, indent=4)}")
            schema = SegnalazioneManualeInput(**input_data)
            print(f"Output Schema:\n{pprint.pformat(schema.model_dump(mode='json'), indent=4)}")
            self.assertEqual(schema.seriousness, level)

    def test_seriousness_invalida(self):
        """Test valore enum non valido"""
        input_data = {
            "incident_longitude": 10.0, 
            "incident_latitude": 10.0, 
            "seriousness": "critical", # Non esiste
            "category": "test"
        }
        print(f"Input Data:\n{pprint.pformat(input_data, indent=4)}")
        with self.assertRaises(ValidationError) as context:
            SegnalazioneManualeInput(**input_data)
        print(f"Errore Pydantic Rilevato:\n{context.exception}")
        self.assertIn("Input should be 'low', 'medium' or 'high'", str(context.exception))

    # ==========================================================================
    # PARTIZIONE 3: DEFAULT VALUES (IncidentSchema - Logica Server)
    # Categorie:
    # - Data/Ora Fornite: Usa quelle fornite
    # - Data/Ora Mancanti: Usa default (Today/Now)
    # ==========================================================================

    def test_default_date_time(self):
        """Test che data e ora vengano generate se mancanti"""
        input_data = {
            "incident_longitude": 12.0,
            "incident_latitude": 41.0,
            "seriousness": "medium",
            "category": "generic"
        }
        print(f"Input Data:\n{pprint.pformat(input_data, indent=4)}")
        schema = SegnalazioneManualeInput(**input_data)
        print(f"Output Schema (con defaults):\n{pprint.pformat(schema.model_dump(mode='json'), indent=4)}")
        
        # Verifica che siano stati assegnati valori di default
        self.assertIsNotNone(schema.incident_date)
        self.assertIsNotNone(schema.incident_time)
        self.assertEqual(schema.incident_date, date.today())
        # Nota: time è dinamico, difficile testare l'uguaglianza esatta, basta che esista

    # ==========================================================================
    # PARTIZIONE 4: LOGICA MODELLO E DB (IncidentModel)
    # Categorie:
    # - Input da DB (Raw): Datetime unito -> Deve splittare
    # - Output verso DB: Date + Time separati -> Deve unire
    # ==========================================================================

    def test_model_from_mongo_logic(self):
        """
        Testa il validatore 'split_datetime' di IncidentModel.
        Simula il recupero di un documento da MongoDB che ha data e ora unite.
        """
        # Simuliamo un documento grezzo da MongoDB
        mongo_raw_data = {
            "_id": "60d5ecb8b5c9c62b3c1d4e5f",
            "user_id": "507f1f77bcf86cd799439011",
            "incident_date": datetime(2025, 12, 25, 15, 30, 0), # Datetime unico
            "incident_longitude": 10.0,
            "incident_latitude": 20.0,
            "seriousness": "high",
            "category": "accident",
            "status": True
        }
        print(f"Input Data (from Mongo):\n{pprint.pformat(mongo_raw_data, indent=4)}")

        # Creiamo il modello (Pydantic deve attivare il validatore before)
        model = IncidentModel(**mongo_raw_data)
        print(f"Output Model:\n{pprint.pformat(model.model_dump(mode='json'), indent=4)}")

        # Verifiche
        self.assertEqual(model.id, "60d5ecb8b5c9c62b3c1d4e5f") # Alias _id -> id
        self.assertEqual(model.incident_date, date(2025, 12, 25)) # Estratto data
        self.assertEqual(model.incident_time, time(15, 30, 0))    # Estratto ora

    def test_model_to_mongo_logic(self):
        """
        Testa il metodo 'to_mongo' di IncidentModel.
        Verifica che data e ora vengano unite per il salvataggio.
        """
        input_data = {
            "user_id": "507f1f77bcf86cd799439011",
            "incident_date": date(2025, 12, 25),
            "incident_time": time(15, 30, 0),
            "incident_longitude": 10.0,
            "incident_latitude": 20.0,
            "seriousness": "high",
            "category": "accident"
        }
        print(f"Input Data (Model):\n{pprint.pformat(input_data, indent=4)}")
        model = IncidentModel(**input_data)

        mongo_dict = model.to_mongo()
        print(f"Output Data (to Mongo):\n{pprint.pformat(mongo_dict, indent=4)}")

        # Verifiche
        self.assertNotIn("id", mongo_dict) # L'id deve essere escluso se None
        self.assertIsInstance(mongo_dict["incident_date"], datetime) # Deve essere datetime
        self.assertEqual(mongo_dict["incident_date"], datetime(2025, 12, 25, 15, 30, 0))
        self.assertNotIn("incident_time", mongo_dict) # Il campo time deve sparire

    # ==========================================================================
    # PARTIZIONE 5: MAPPA SCHEMA (DTOs)
    # Categorie:
    # - DTO Leggero (MapDTO): Solo campi essenziali
    # - DTO Dettaglio (DettaglioDTO): Campi estesi
    # ==========================================================================

    def test_mappa_dto_inheritance(self):
        """Testa che il DTO di dettaglio erediti correttamente e validi i campi extra"""
        data = {
            "_id": "123",
            "category": "lavori",
            "seriousness": "low",
            "incident_latitude": 45.0,
            "incident_longitude": 12.0,
            "incident_date": "2025-01-01",
            "incident_time": "10:00:00",
            "status": True,
            "description": "Lavori in corso"
        }
        print(f"Input Data:\n{pprint.pformat(data, indent=4)}")
        
        dettaglio = SegnalazioneDettaglioDTO(**data)
        print(f"Output DTO:\n{pprint.pformat(dettaglio.model_dump(mode='json'), indent=4)}")
        
        self.assertEqual(dettaglio.description, "Lavori in corso")
        self.assertEqual(dettaglio.id, "123")
        self.assertTrue(dettaglio.status)

    # ==========================================================================
    # PARTIZIONE 6: SCENARI REALI (da metodi_repo_segnalazione.py)
    # Categorie:
    # - Combinazione Data/Ora per query Repository
    # - Gestione Status (Attivo/Inattivo)
    # ==========================================================================

    def test_scenario_repo_data_consistency(self):
        """
        Replica gli scenari di dati usati in 'metodi_repo_segnalazione.py'
        per garantire che il Modello supporti le query del Repository.
        """
        # Dati di test presi da metodi_repo_segnalazione.py
        scenarios = [
            {
                "user_id": "507f1f77bcf86cd799439012",
                "incident_date": date(2023, 10, 25),
                "incident_time": time(14, 30),
                "incident_longitude": 12.0, "incident_latitude": 41.0,
                "seriousness": "high", "category": "accident", "status": True
            },
            {
                "user_id": "507f1f77bcf86cd799439013", # Caso status False
                "incident_date": date(2023, 10, 25),
                "incident_time": time(9, 00),
                "incident_longitude": 12.0, "incident_latitude": 41.0,
                "seriousness": "low", "category": "other", "status": False
            }
        ]

        for i, data in enumerate(scenarios):
            print(f"Scenario {i+1} Input:\n{pprint.pformat(data, indent=4)}")
            # 1. Verifica creazione Modello
            model = IncidentModel(**data)
            print(f"Model Created:\n{pprint.pformat(model.model_dump(mode='json'), indent=4)}")
            self.assertEqual(model.status, data["status"])

            # 2. Verifica trasformazione per DB (to_mongo)
            # Il repository fa query su 'incident_date' come datetime, quindi è CRUCIALE
            # che to_mongo unisca correttamente data e ora.
            mongo_data = model.to_mongo()
            print(f"Mongo Data:\n{pprint.pformat(mongo_data, indent=4)}")
            
            expected_dt = datetime.combine(data["incident_date"], data["incident_time"])
            self.assertEqual(mongo_data["incident_date"], expected_dt)
            self.assertNotIn("incident_time", mongo_data)

            # 3. Verifica ricostruzione da DB (simulazione lettura)
            # Il repository legge questo dizionario (con datetime unito)
            # e il modello deve saperlo separare.
            reconstructed_model = IncidentModel(**mongo_data)
            print(f"Reconstructed Model:\n{pprint.pformat(reconstructed_model.model_dump(mode='json'), indent=4)}")
            self.assertEqual(reconstructed_model.incident_date, data["incident_date"])
            self.assertEqual(reconstructed_model.incident_time, data["incident_time"])

class Tee:
    """Classe helper per scrivere l'output sia su console che su file"""
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            try:
                f.write(obj)
                f.flush()
            except Exception:
                pass
    def flush(self):
        for f in self.files:
            try:
                f.flush()
            except Exception:
                pass

if __name__ == '__main__':
    
    # Ottiene il nome del file corrente (es. 'test_schemas_models.py')
    filename = os.path.basename(__file__)
    # Ottiene il prefisso (es. 'test_schemas_models')
    prefix = os.path.splitext(filename)[0]

    # Configurazione cartella di output
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Redirezione output su file e console
    output_filename = os.path.join(output_dir, f"{prefix}_output.txt")
    print(f"--- L'output verrà salvato anche in: {output_filename} ---")
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Redirigiamo stdout e stderr
        sys.stdout = Tee(sys.stdout, f)
        sys.stderr = Tee(sys.stderr, f)
        
        try:
            # exit=False impedisce a unittest di chiudere lo script bruscamente
            unittest.main(exit=False)
        finally:
            # Ripristino (buona pratica)
            sys.stdout = original_stdout
            sys.stderr = original_stderr
