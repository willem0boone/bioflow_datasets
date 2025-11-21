import pyarrow.fs
import pyarrow.dataset as ds
import pyarrow.fs
import pystac_client
from urllib.parse import urlparse
from datetime import datetime, timezone
import pandas as pd
from pathlib import Path
import pyarrow.compute as pc


def read_dataset_ids(file_path: str):
    """Read dataset IDs (integers) from a text file, one per line."""
    with open(file_path, "r") as f:
        ids = [int(line.strip()) for line in f if line.strip().isdigit()]
    print(f"Loaded {len(ids)} dataset IDs from {file_path}")
    return ids


def find_occurrence_data():
    """Find EMODnet occurrence parquet URLs from the STAC catalog."""
    url = 'https://catalog.dive.edito.eu'
    client = pystac_client.Client.open(url)
    variable = "emodnet-occurrence_data"

    for collection in client.get_collections():
        if variable in collection.id:
            for item in collection.get_items():
                for key, value in item.assets.items():
                    if key == "parquet":
                        yield value.href


def setup_s3_dataset(url: str):
    """Set up S3 connection and return dataset object."""
    parsed = urlparse(url)

    if parsed.scheme in ("http", "https") and "cloudferro.com" in parsed.netloc:
        endpoint = parsed.netloc
        s3_path = parsed.path.lstrip("/")
        s3 = pyarrow.fs.S3FileSystem(endpoint_override=endpoint, anonymous=True)
    elif parsed.scheme == "s3":
        endpoint = "s3.waw3-1.cloudferro.com"
        s3_path = f"{parsed.netloc}/{parsed.path.lstrip('/')}"
        s3 = pyarrow.fs.S3FileSystem(endpoint_override=endpoint, anonymous=True)
    else:
        raise ValueError(f"Unsupported URL scheme: {url}")

    print(f"Connected to endpoint: {endpoint}")
    print(f"Dataset path: {s3_path}")

    dataset = ds.dataset(s3_path, filesystem=s3, format="parquet")
    return dataset


def extract_call1_data(dataset, dataset_id: int, output_dir: Path):
    """
    Extract data for one dataset ID, keep unique latitude, longitude, observationdate combinations,
    and store all unique aphiaids at that location and time in a list. Save to its own CSV.
    """

    # Only keep needed columns
    columns_needed = ["datasetid", "latitude", "longitude", "observationdate", "aphiaid"]

    # Filter for the current dataset_id
    dataset_filter = pc.field("datasetid") == dataset_id

    try:
        table = dataset.to_table(columns=columns_needed, filter=dataset_filter)
        df = table.to_pandas()
    except Exception as e:
        print(f"⚠️ Error extracting datasetid {dataset_id}: {e}")
        return

    if df.empty:
        print(f"No records found for datasetid {dataset_id}")
        return

    # ✅ Drop duplicates across all grouping keys + aphiaid (safety check)
    df = df.drop_duplicates(subset=["latitude", "longitude", "observationdate", "aphiaid"])

    # ✅ Group by lat, lon, datetime and aggregate unique aphiaids
    df_grouped = (
        df.groupby(["latitude", "longitude", "observationdate"], as_index=False)
          .agg({"aphiaid": lambda x: sorted(set(x))})  # ensures unique aphiaids per space-time
    )

    # Prepare output_call1 file
    csv_name = output_dir / f"dasid_{dataset_id}.csv"
    df_grouped.to_csv(csv_name, index=False)
    print(f"✅ Saved {len(df_grouped)} aggregated records for datasetid {dataset_id} to {csv_name}")
    print(f"   ↳ Each (lat, lon, time) has {df_grouped['aphiaid'].apply(len).max()} max unique aphiaids")


def extract_sensor_data(dataset, dataset_id: int, output_dir: Path):
    """
    Extract data for one dataset ID, keep unique latitude, longitude, observationdate combinations,
    and store all unique aphiaids at that location and time in a list. Save to its own CSV.
    """

    columns_needed = ["datasetid", "latitude", "longitude", "observationdate", "aphiaid"]
    dataset_filter = pc.field("datasetid") == dataset_id

    try:
        table = dataset.to_table(columns=columns_needed, filter=dataset_filter)
        df = table.to_pandas()
    except Exception as e:
        print(f"⚠️ Error extracting datasetid {dataset_id}: {e}")
        return

    if df.empty:
        print(f"No records found for datasetid {dataset_id}")
        return

    # ✅ Clean and standardize observationdate
    df["observationdate"] = pd.to_datetime(df["observationdate"], errors="coerce")

    # ✅ Filter for recent data (only for specific dataset IDs)
    if dataset_id in [3117, 4688, 5531]:
        df["observationdate"] = pd.to_datetime(df["observationdate"], utc=True, errors="coerce")
        cutoff = datetime(2023, 9, 1, tzinfo=timezone.utc)
        df = df[df["observationdate"] >= cutoff]
        if df.empty:
            print(f"No records from September 2023 onwards for datasetid {dataset_id}")
            return

    # ✅ Clean aphiaid column
    before = len(df)

    # Convert all to string, strip whitespace, remove commas
    df["aphiaid"] = (
        df["aphiaid"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    # Replace empty or 'nan'/'None' strings with NaN
    df["aphiaid"] = df["aphiaid"].replace(
        ["nan", "None", "none", "null", "", "[]"], pd.NA
    )

    # Drop rows with missing or invalid aphiaids
    df = df.dropna(subset=["aphiaid"])

    # Convert to integers where possible
    df["aphiaid"] = pd.to_numeric(df["aphiaid"], errors="coerce").dropna().astype(int)

    after = len(df)
    if after < before:
        print(f"⚠️ Dropped {before - after} rows with invalid/missing aphiaid values in datasetid {dataset_id}")

    # ✅ Drop duplicates across grouping keys + aphiaid
    df = df.drop_duplicates(subset=["latitude", "longitude", "observationdate", "aphiaid"])

    # ✅ Group by spatial-temporal coordinates and aggregate unique aphiaids
    df_grouped = (
        df.groupby(["latitude", "longitude", "observationdate"], as_index=False)
          .agg({"aphiaid": lambda x: sorted(set(x))})
    )

    # Save to CSV
    csv_name = output_dir / f"dasid_{dataset_id}.csv"
    df_grouped.to_csv(csv_name, index=False)

    print(f"✅ Saved {len(df_grouped)} aggregated records for datasetid {dataset_id} to {csv_name}")
    print(f"   ↳ Each (lat, lon, time) has {df_grouped['aphiaid'].apply(len).max()} max unique aphiaids")


def extract_tracking_data(dataset, dataset_id: int, output_dir: Path):
    """
    Extract data for one dataset ID, keep unique latitude, longitude, observationdate combinations,
    and store all unique aphiaids at that location and time in a list. Save to its own CSV.
    """

    # Only keep needed columns
    columns_needed = ["datasetid", "latitude", "longitude", "observationdate", "aphiaid"]

    # Filter for the current dataset_id
    dataset_filter = pc.field("datasetid") == dataset_id

    try:
        table = dataset.to_table(columns=columns_needed, filter=dataset_filter)
        df = table.to_pandas()
    except Exception as e:
        print(f"⚠️ Error extracting datasetid {dataset_id}: {e}")
        return

    if df.empty:
        print(f"No records found for datasetid {dataset_id}")
        return

    # ✅ Drop duplicates across all grouping keys + aphiaid (safety check)
    df = df.drop_duplicates(subset=["latitude", "longitude", "observationdate", "aphiaid"])

    # ✅ Group by lat, lon, datetime and aggregate unique aphiaids
    df_grouped = (
        df.groupby(["latitude", "longitude", "observationdate"], as_index=False)
          .agg({"aphiaid": lambda x: sorted(set(x))})  # ensures unique aphiaids per space-time
    )

    # Prepare output_call1 file
    csv_name = output_dir / f"dasid_{dataset_id}.csv"
    df_grouped.to_csv(csv_name, index=False)
    print(f"✅ Saved {len(df_grouped)} aggregated records for datasetid {dataset_id} to {csv_name}")
    print(f"   ↳ Each (lat, lon, time) has {df_grouped['aphiaid'].apply(len).max()} max unique aphiaids")


if __name__ == "__main__":

    # Setup data lake connection
    occ = find_occurrence_data()
    data_file = next(occ)
    print(f"Using dataset: {data_file}")
    dataset = setup_s3_dataset(data_file)

    # -------------------------------------------------------------------------
    # call1 data
    print("-"*50)
    print("working on call1 datasets")
    call1_dasids = read_dataset_ids("../sources/dasid_call1_data.txt")
    output_dir = Path("../data/output_call1")
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, did in enumerate(call1_dasids):
        print(f"dataset {i} out of {len(call1_dasids)}")
        extract_call1_data(dataset, did, output_dir)

    # -------------------------------------------------------------------------
    # sensor datasets
    print("-"*50)
    print("working on sensor datasets")
    sensor_dasids = read_dataset_ids("../sources/dasid_sensor_data.txt")
    output_dir = Path("../data/output_sensor_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, did in enumerate(sensor_dasids):
        print(f"dataset {i} out of {len(sensor_dasids)}")
        extract_sensor_data(dataset, did, output_dir)

    # -------------------------------------------------------------------------
    # sensor datasets
    print("-"*50)
    print("working on tracking datasets")
    tracking_dasids = read_dataset_ids("../sources/dasid_tracking_data.txt")
    output_dir = Path("../data/output_tracking_data")
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, did in enumerate(tracking_dasids):
        print(f"dataset {i} out of {len(tracking_dasids)}")
        extract_tracking_data(dataset, did, output_dir)
