from nyc311_elt.config import Settings
import duckdb
import logging

logger = logging.getLogger(__name__)


def load_raw(settings: Settings) -> int:

    path = settings.data_dir / "warehouse" / "nyc311.duckdb"
    parquet_glob = str(settings.data_dir / "raw" / "nyc311" / "*" / "*.parquet")

    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(path))

    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    # hive_partitioning=false a propósito: la columna de partición se llama igual
    # que created_date del Parquet y la sobrescribe, perdiendo la hora
    # (2026-09-15T01:12:16 -> 2026-09-15).
    con.execute(
        f"CREATE OR REPLACE TABLE raw.service_requests AS SELECT * FROM read_parquet('{parquet_glob}', hive_partitioning = false)"
    )
    rows = con.execute("SELECT COUNT(*) FROM raw.service_requests").fetchone()[0]
    logger.info("Cargadas %d filas en raw.service_requests", rows)
    con.close()
    return rows


def main():

    settings = Settings.from_env()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    load_raw(settings)


if __name__ == "__main__":
    main()
