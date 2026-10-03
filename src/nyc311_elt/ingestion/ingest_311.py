from nyc311_elt.config import (
    RESOURCE_URL,
    ORDER_FIELD,
    PAGE_SIZE,
    DATE_FIELD,
    COLUMNS,
    COLUMNS_SET,
    METADATA_COLUMNS,
    Settings,
    READ_TIMEOUT,
    CONNECT_TIMEOUT,
)
from nyc311_elt.http_client import get_with_retries
from datetime import date, timedelta, datetime, timezone
import logging
import httpx
import pyarrow as pa
import json
import os, shutil
import pyarrow.parquet as pq
import argparse

SCHEMA = pa.schema([(name, pa.string()) for name in COLUMNS + METADATA_COLUMNS])
logger = logging.getLogger(__name__)


def _to_str(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


def normalize_rows(rows: list[dict]) -> tuple[list[dict], set[str]]:
    unknown_columns = set()
    normalized_rows = []
    for row in rows:
        unknown_columns.update(set(row.keys()) - COLUMNS_SET)
        normalized_row = {column: _to_str(row.get(column)) for column in COLUMNS}
        normalized_rows.append(normalized_row)
    return normalized_rows, unknown_columns


def build_params(target_date: date, offset: int) -> dict[str, str | int]:
    end_date = target_date + timedelta(days=1)
    return {
        "$where": f"{DATE_FIELD} >= '{target_date.isoformat()}T00:00:00' AND {DATE_FIELD} < '{end_date.isoformat()}T00:00:00'",
        "$limit": PAGE_SIZE,
        "$offset": offset,
        "$order": ORDER_FIELD,
    }


def fetch_data(client: httpx.Client, target_date: date) -> list[dict]:
    rows = []
    offset = 0

    while True:
        params = build_params(target_date, offset)
        response = get_with_retries(client, RESOURCE_URL, params=params)
        logger.info(
            f"Fetched {len(response)} records for date {target_date} with offset {offset}"
        )
        rows.extend(response)
        if len(response) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows


def add_metadata(rows: list[dict], target_date: date) -> list[dict]:

    ingested_at = datetime.now(timezone.utc).isoformat()
    partition_date = target_date.isoformat()
    for row in rows:
        row["_ingested_at"] = ingested_at
        row["_source_url"] = RESOURCE_URL
        row["_partition_date"] = partition_date
    return rows


def write_partition(rows, target_date, settings: Settings):
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    destiny = (
        settings.data_dir / "raw" / "nyc311" / f"created_date={target_date.isoformat()}"
    )
    temp = destiny.with_name(destiny.name + "__tmp")

    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True)

    pq.write_table(table, temp / "part-0.parquet")

    if destiny.exists():
        shutil.rmtree(destiny)
    os.replace(temp, destiny)
    logger.info(f"Wrote {len(rows)} records to {destiny / 'part-0.parquet'}")


def main():
    settings = Settings.from_env()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, type=date.fromisoformat)
    args = parser.parse_args()
    target_date = args.date

    timeout = httpx.Timeout(READ_TIMEOUT, connect=CONNECT_TIMEOUT)
    with httpx.Client(timeout=timeout) as client:
        data = fetch_data(client, target_date)

    normalized_data, unknown_columns = normalize_rows(data)
    rows_with_metadata = add_metadata(normalized_data, target_date)
    write_partition(rows_with_metadata, target_date, settings)


if __name__ == "__main__":
    main()
