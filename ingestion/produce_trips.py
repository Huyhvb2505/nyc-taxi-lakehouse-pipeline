#!/usr/bin/env python3
"""Replay downloaded Yellow Taxi parquet into a Kafka topic to simulate a stream.

Provided infrastructure — this is the FACT source your Spark Structured
Streaming job will consume. It reads the parquet in batches and publishes one
JSON message per trip, sleeping between batches so the topic fills gradually
like a live stream.

Each message value is the raw trip record as JSON, e.g.:
  {"VendorID": 2, "tpep_pickup_datetime": "2024-01-01T00:57:55", ...,
   "PULocationID": 186, "DOLocationID": 79, "fare_amount": 17.7,
   "total_amount": 22.7, ...}

Usage (inside the compose network):
  docker compose run --rm trip-producer
  docker compose run --rm trip-producer --delay 0.2 --batch-size 5000 --limit 100000
"""
import argparse
import glob
import json
import os
import sys
import time

import pyarrow.parquet as pq
from kafka import KafkaProducer


def json_default(o):
    iso = getattr(o, "isoformat", None)
    return iso() if callable(iso) else str(o)


def find_parquet(path_or_glob: str):
    if os.path.isdir(path_or_glob):
        files = sorted(glob.glob(os.path.join(path_or_glob, "*.parquet")))
    else:
        files = sorted(glob.glob(path_or_glob))
    if not files:
        print(f"No parquet files found at: {path_or_glob}")
        sys.exit(1)
    return files


def parse_args():
    ap = argparse.ArgumentParser(description="Replay TLC parquet into Kafka.")
    ap.add_argument("--path", default=os.environ.get("SOURCE", "/data/raw/yellow"),
                    help="parquet file, directory, or glob")
    ap.add_argument("--broker", default=os.environ.get("BROKER", "redpanda:9092"))
    ap.add_argument("--topic", default=os.environ.get("TOPIC", "yellow_trips"))
    ap.add_argument("--batch-size", type=int, default=int(os.environ.get("BATCH_SIZE", "2000")))
    ap.add_argument("--delay", type=float, default=float(os.environ.get("DELAY", "0.5")),
                    help="seconds to sleep between batches (simulate stream velocity)")
    ap.add_argument("--limit", type=int, default=int(os.environ.get("LIMIT", "0")),
                    help="max messages to send (0 = all rows)")
    return ap.parse_args()


def main():
    args = parse_args()
    producer = KafkaProducer(
        bootstrap_servers=args.broker,
        value_serializer=lambda v: json.dumps(v, default=json_default).encode("utf-8"),
        linger_ms=50,
        acks=1,
    )
    files = find_parquet(args.path)
    print(f"Producing to {args.broker} topic '{args.topic}' from {len(files)} file(s):")
    for f in files:
        print(f"  - {f}")

    sent = 0
    done = False
    for fp in files:
        if done:
            break
        reader = pq.ParquetFile(fp)
        for batch in reader.iter_batches(batch_size=args.batch_size):
            for row in batch.to_pylist():
                producer.send(args.topic, row)
                sent += 1
                if args.limit and sent >= args.limit:
                    done = True
                    break
            producer.flush()
            print(f"  sent {sent:,} messages", flush=True)
            if done:
                break
            time.sleep(args.delay)

    producer.flush()
    producer.close()
    print(f"\nDone. Sent {sent:,} messages to topic '{args.topic}'.")


if __name__ == "__main__":
    main()
