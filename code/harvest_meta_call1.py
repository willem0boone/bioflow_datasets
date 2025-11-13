import geopandas as gpd
import pandas as pd
import pyarrow.dataset as ds
import pyarrow.compute as pc
import pyarrow.fs
import pystac_client
from urllib.parse import urlparse
from pathlib import Path


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


def extract_data(dataset, dataset_id: int, output_dir: Path):
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
    # Read dataset IDs from text file
    dataset_ids = read_dataset_ids("dasid_call1.txt")

    # Get first available parquet dataset URL from STAC
    occ = find_occurrence_data()
    data_file = next(occ)
    print(f"Using dataset: {data_file}")

    # Prepare output_call1 directory
    output_dir = Path("../output_call1")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set up S3 dataset once
    dataset = setup_s3_dataset(data_file)

    # Loop over all dataset IDs and save each to its own CSV
    for i, did in enumerate(dataset_ids):
        print(f"dataset {i} out of {len(dataset_ids)}")
        extract_data(dataset, did, output_dir)

    # extract_data(dataset, 4687, output_dir)


    