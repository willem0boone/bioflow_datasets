import pandas as pd
import requests
from pathlib import Path
from collections import Counter
import ast
import json
import threading
import time

# ------------------------
# Cache setup
# ------------------------
cache_dir = Path("../cache")
cache_dir.mkdir(parents=True, exist_ok=True)
cache_file = cache_dir / "aphia_cache.json"

# Load existing cache if present
aphia_cache = {}
if cache_file.exists():
    try:
        with open(cache_file, "r") as f:
            aphia_cache = json.load(f)
    except Exception:
        aphia_cache = {}

# Lock for thread-safe cache writing (optional if multithreading is used)
cache_lock = threading.Lock()

# ------------------------
# WoRMS API function
# ------------------------
def get_aphia_record(aphia_id: int):
    """
    Retrieve WoRMS Aphia record, using cache if available.
    Added print statements to validate cache behavior.
    """
    aphia_id_str = str(aphia_id)

    # Check cache first
    if aphia_id_str in aphia_cache:
        # print(f"🔹 Cache hit for AphiaID {aphia_id}")
        return aphia_cache[aphia_id_str]

    # print(f"🔸 Cache miss for AphiaID {aphia_id}, requesting from WoRMS API...")
    url = f"https://www.marinespecies.org/rest/AphiaRecordByAphiaID/{aphia_id}"

    try:
        response = requests.get(url, headers={"accept": "application/json"}, timeout=10)
        response.raise_for_status()
        record = response.json()
        # print(f"✅ Successfully retrieved AphiaID {aphia_id}")
    except Exception as e:
        # print(f"⚠️ Failed to fetch AphiaID {aphia_id}: {e}")
        record = None

    # Save to cache immediately
    with cache_lock:
        aphia_cache[aphia_id_str] = record
        try:
            with open(cache_file, "w") as f:
                json.dump(aphia_cache, f, indent=2)
            # print(f"💾 Cache updated for AphiaID {aphia_id}, cache size: {cache_file.stat().st_size / 1024:.2f} KB")
        except Exception as e:
            print(f"⚠️ Failed to write cache to disk: {e}")

    return record

# ------------------------
# Process a single CSV
# ------------------------
def process_csv(csv_file: Path):
    """
    Process one CSV:
      1. Count occurrences of each AphiaID
      2. Get taxonomy info (from cache or REST API)
      3. Return list of dicts {"taxonomy": [...], "count": n}
    """
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"⚠️ Failed to read {csv_file}: {e}")
        return None

    aphia_counter = Counter()

    # Count occurrences of each AphiaID
    for row in df.itertuples():
        try:
            aphia_list = ast.literal_eval(row.aphiaid)
            if isinstance(aphia_list, int):
                aphia_list = [aphia_list]
            aphia_counter.update(aphia_list)
        except Exception:
            continue

    results = []

    for aphia_id, count in aphia_counter.items():
        record = get_aphia_record(aphia_id)
        if not record:
            continue
        taxonomy = [
            record.get("kingdom"),
            record.get("phylum"),
            record.get("class"),
            record.get("order"),
            record.get("family"),
            record.get("genus"),
            record.get("scientificname")
        ]
        results.append({"taxonomy": taxonomy, "count": count})

    return results

# ------------------------
# Main
# ------------------------
if __name__ == "__main__":
    output_dir = Path("../data/worms")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_dirs = {
        "call1": Path("../data/output_call1"),
        "sensor_data": Path("../data/output_sensor_data")
    }

    for source_name, csv_dir in csv_dirs.items():
        # Create subdirectory for this source
        sub_output_dir = output_dir / f"worms_{source_name}_data"
        sub_output_dir.mkdir(parents=True, exist_ok=True)

        csv_files = sorted(csv_dir.glob("*.csv"))

        for file in csv_files:
            dasid = file.stem.split("_")[-1]
            print(f"Processing DASID {dasid} from {source_name}...")

            data = process_csv(file)
            if data is None:
                continue

            out_file = sub_output_dir / f"worms_info_dasid_{dasid}.json"
            with open(out_file, "w") as f:
                json.dump(data, f, indent=2)

            print(f"✅ Saved taxonomy counts for DASID {dasid} to {out_file}")

    print(f"✅ All done. Aphia cache stored at {cache_file}")