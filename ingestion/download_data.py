#!/usr/bin/env python3
"""Download NYC TLC data on demand into the shared /data/raw folder.

Provided infrastructure — NOT part of the graded ETL work.

Downloads, for a given year/month:
  * Yellow Taxi trip records (parquet)  -> the heavy FACT source
  * taxi_zone_lookup.csv                -> the zone dimension
and writes three small code-dimension CSVs from the TLC data dictionary:
  * payment_type.csv, rate_code.csv, vendor.csv

Usage:
  python download_data.py <YEAR> <MONTH>        e.g.  python download_data.py 2024 1
"""
import csv
import os
import sys
import urllib.request

CLOUDFRONT = "https://d37ci6vzurychx.cloudfront.net"
RAW_DIR = os.environ.get("RAW_DIR", "/data/raw")

# --- TLC data dictionary code tables (stable reference values) ---------------
PAYMENT_TYPES = [
    (0, "Flex Fare / Unknown"),
    (1, "Credit card"),
    (2, "Cash"),
    (3, "No charge"),
    (4, "Dispute"),
    (5, "Unknown"),
    (6, "Voided trip"),
]
RATE_CODES = [
    (1, "Standard rate"),
    (2, "JFK"),
    (3, "Newark"),
    (4, "Nassau or Westchester"),
    (5, "Negotiated fare"),
    (6, "Group ride"),
    (99, "Unknown"),
]
VENDORS = [
    (1, "Creative Mobile Technologies, LLC"),
    (2, "Curb Mobility, LLC"),
    (6, "Myle Technologies Inc"),
    (7, "Helix"),
]


def download(url: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"  downloading {url}")
    urllib.request.urlretrieve(url, dest)
    print(f"  -> {dest}  ({os.path.getsize(dest):,} bytes)")


def write_csv(path: str, header, rows) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  -> {path}  ({len(rows)} rows)")


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    year, month = int(sys.argv[1]), int(sys.argv[2])
    ym = f"{year:04d}-{month:02d}"

    print(f"[1/3] Yellow Taxi trip records ({ym})")
    download(
        f"{CLOUDFRONT}/trip-data/yellow_tripdata_{ym}.parquet",
        f"{RAW_DIR}/yellow/yellow_tripdata_{ym}.parquet",
    )

    print("[2/3] Taxi zone lookup dimension")
    download(
        f"{CLOUDFRONT}/misc/taxi_zone_lookup.csv",
        f"{RAW_DIR}/dims/taxi_zone_lookup.csv",
    )

    print("[3/3] Code dimensions (from TLC data dictionary)")
    write_csv(f"{RAW_DIR}/dims/payment_type.csv", ["payment_type", "description"], PAYMENT_TYPES)
    write_csv(f"{RAW_DIR}/dims/rate_code.csv", ["ratecode_id", "description"], RATE_CODES)
    write_csv(f"{RAW_DIR}/dims/vendor.csv", ["vendor_id", "name"], VENDORS)

    print(f"\nDone. Raw data available under {RAW_DIR}/")


if __name__ == "__main__":
    main()
