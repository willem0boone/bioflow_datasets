import pystac

catalog_url = "https://lifewatch.be/etn/parquet/catalog.json"

# Load the static catalog
catalog = pystac.Catalog.from_file(catalog_url)

# -----------------------------------------
# 1. List all collections
# -----------------------------------------
# print("Collections:")
# collections = list(catalog.get_collections())
# for col in collections:
#     print(f" - {col.id}: {col.description}")
#
# print("\n----------------------------------")
# print("Items and assets")
# print("----------------------------------\n")
#
# # -----------------------------------------
# # 2. List all items and their assets
# # -----------------------------------------
# items = list(catalog.get_all_items())
# print(f"Found {len(items)} items total.\n")
#
# for item in items:
#     print(f"Item ID: {item.id}")
#     print(f"  Collection: {item.collection_id}")
#     print(f"  Assets:")
#
#     for asset_key, asset in item.assets.items():
#         print(f"    - Key: {asset_key}")
#         print(f"      Href: {asset.href}")
#         print(f"      Media type: {asset.media_type}")
#
#     print()  # blank line between items


# open https://www.lifewatch.be/etn/parquet/animals/part-0.parquet
import pyarrow as pa
import pyarrow.parquet as pq
import urllib.request
import io

# URL of the parquet file
parquet_url = "https://www.lifewatch.be/etn/parquet/animals/part-0.parquet"

# Download the parquet file into memory
with urllib.request.urlopen(parquet_url) as response:
    data = response.read()

# Wrap as a BytesIO so pyarrow can read from it
bio = io.BytesIO(data)

# Read the schema
schema = pq.read_schema(bio)

print("Schema of Parquet file:")
print(schema)


