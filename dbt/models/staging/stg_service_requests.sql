SELECT
    cast(unique_key as bigint) as service_request_id,
    cast(created_date as timestamp) as created_at,
    cast(closed_date as timestamp) as closed_at,
    cast(resolution_action_updated_date as timestamp) as resolution_updated_at,
    cast(_ingested_at as timestamp) as ingested_at,
    cast(_partition_date  as date) as  partition_date,
    cast(latitude as double) as latitude,
    cast(longitude as double) as longitude,
    address_type,
    agency,
    agency_name,
    bbl,
    complaint_type, 
    descriptor, 
    status, 
    borough, 
    city, 
    incident_zip, 
    incident_address, 
    street_name, 
    location_type, 
    resolution_description, 
    community_board, 
    council_district, 
    police_precinct, 
    open_data_channel_type as channel,
    _source_url as source_url

    
    
from {{ source('nyc311', 'service_requests') }}