from datetime import date
import os
from dataclasses import dataclass
from pathlib import Path


BASE_URL = "https://data.cityofnewyork.us"
RESOURCE_ID = "erm2-nwe9"
RESOURCE_URL = f"{BASE_URL}/resource/{RESOURCE_ID}.json"

MIN_DATE = date(2020, 1, 1)

DATE_FIELD = "created_date"

ORDER_FIELD = "unique_key"

PAGE_SIZE = 50_000


CONNECT_TIMEOUT = 10.0
READ_TIMEOUT = 60.0

MAX_RETRIES = 5
BACKOFF_BASE = 1.0
BACKOFF_CAP = 30.0

RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    log_level: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            data_dir=Path(os.environ.get("DATA_DIR", "data")),
            log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        )


COLUMNS: tuple[str, ...] = (
    "address_type",
    "agency",
    "agency_name",
    "bbl",
    "borough",
    "bridge_highway_direction",
    "bridge_highway_name",
    "bridge_highway_segment",
    "city",
    "closed_date",
    "community_board",
    "complaint_type",
    "council_district",
    "created_date",
    "cross_street_1",
    "cross_street_2",
    "descriptor",
    "descriptor_2",
    "due_date",
    "facility_type",
    "incident_address",
    "incident_zip",
    "intersection_street_1",
    "intersection_street_2",
    "landmark",
    "latitude",
    "location",
    "location_type",
    "longitude",
    "open_data_channel_type",
    "park_borough",
    "park_facility_name",
    "police_precinct",
    "resolution_action_updated_date",
    "resolution_description",
    "road_ramp",
    "status",
    "street_name",
    "taxi_company_borough",
    "taxi_pick_up_location",
    "unique_key",
    "vehicle_type",
    "x_coordinate_state_plane",
    "y_coordinate_state_plane",
)

COLUMNS_SET: set[str] = frozenset(COLUMNS)

METADATA_COLUMNS = ("_ingested_at", "_source_url", "_partition_date")
