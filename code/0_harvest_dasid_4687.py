import pandas as pd
import pyarrow.dataset as ds
import pyarrow.compute as pc
from pathlib import Path
from urllib.parse import urlparse
import pyarrow.fs
import pystac_client


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


def extract_data_in_batches(dataset, dasid: int, output_dir: Path,
                            chunk_size=25_000):
    """
    Extract all rows for a given datasetid (dasid) and write all columns to separate CSVs in batches.

    Parameters:
    - dataset: PyArrow dataset
    - dasid: dataset ID to filter
    - output_dir: folder to save CSV files
    - chunk_size: maximum number of rows per CSV
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create scanner filtered by datasetid
    scanner = dataset.scanner(filter=pc.field("datasetid") == dasid)

    buffer = []
    total_rows = 0
    part = 1

    for i, batch in enumerate(scanner.to_batches()):
        df = batch.to_pandas()
        buffer.append(df)

        # Check if buffer reached chunk_size
        if sum(len(b) for b in buffer) >= chunk_size:
            combined = pd.concat(buffer, ignore_index=True)
            output_file = output_dir / f"dasid_{dasid}_part{part}.csv"
            combined.to_csv(output_file, index=False)
            total_rows += len(combined)
            print(
                f"✅ Wrote {output_file} ({len(combined)} rows, total so far: {total_rows})")
            buffer = []
            part += 1

    # Write any remaining rows
    if buffer:
        combined = pd.concat(buffer, ignore_index=True)
        output_file = output_dir / f"dasid_{dasid}_part{part}.csv"
        combined.to_csv(output_file, index=False)
        total_rows += len(combined)
        print(
            f"✅ Wrote final batch {output_file} ({len(combined)} rows, total rows: {total_rows})")

    print(
        f"🎉 Finished extraction for dasid {dasid}, total rows saved: {total_rows}")


if __name__ == "__main__":
    occ_url = "https://catalog.dive.edito.eu"  # your STAC URL
    client = pystac_client.Client.open(occ_url)
    variable = "emodnet-occurrence_data"
    # Get first parquet asset URL
    data_file = next(
        value.href
        for collection in client.get_collections() if variable in collection.id
        for item in collection.get_items()
        for key, value in item.assets.items() if key == "parquet"
    )
    print(f"Using dataset: {data_file}")

    dataset = setup_s3_dataset(data_file)

    output_csv = Path("../data/output_dasid_4687/")
    extract_data_in_batches(dataset, dasid=4687, output_dir=output_csv)

