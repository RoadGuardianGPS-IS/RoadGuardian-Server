"""
Preprocess OSM PBF into a parquet cache of highway-related POI for fast local lookup.
Usage:
  python app/AI/build_osm_poi_cache.py
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_DIR = os.path.join(BASE_DIR, "app")
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
if APP_DIR not in sys.path:
    sys.path.append(APP_DIR)

PBF_PATH = os.path.join(BASE_DIR, "dati_osm", "italy-latest.osm.pbf")
OUTPUT_DIR = os.path.join(BASE_DIR, "cache")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "pois_highway.parquet")

HIGHWAY_TAGS = ["traffic_signals", "stop", "crossing", "bump"]


def main():
    import pandas as pd
    import pyrosm

    if not os.path.exists(PBF_PATH):
        print(f"[BUILD] PBF non trovato: {PBF_PATH}")
        return 1

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"[BUILD] Carico PBF: {PBF_PATH}")
    osm = pyrosm.OSM(PBF_PATH)
    print("[BUILD] Estraggo POI highway rilevanti...")
    pois = osm.get_pois(custom_filter={"highway": HIGHWAY_TAGS})

    if pois is None or pois.empty:
        print("[BUILD] Nessun POI trovato con i tag richiesti")
        return 1

    if "lon" not in pois.columns or "lat" not in pois.columns:
        if "geometry" in pois.columns:
            pois["lon"] = pois.geometry.x
            pois["lat"] = pois.geometry.y
        else:
            print("[BUILD] Colonne lon/lat non presenti e nessuna geometry disponibile")
            return 1

    cols = ["lon", "lat", "highway"]
    pois = pois[cols].dropna(subset=["lon", "lat", "highway"])

    print(f"[BUILD] Salvo parquet: {OUTPUT_PATH}")
    pois.to_parquet(OUTPUT_PATH, index=False)
    print(f"[BUILD] Salvato. Righe: {len(pois)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
