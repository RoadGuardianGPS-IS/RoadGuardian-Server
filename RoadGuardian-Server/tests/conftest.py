"""
Pytest configuration file per il progetto RoadGuardian-Server
Configura il path per gli import dei moduli
"""

import sys
from pathlib import Path

# Aggiungi la directory app al path di Python
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))

# Aggiungi anche la directory root
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
