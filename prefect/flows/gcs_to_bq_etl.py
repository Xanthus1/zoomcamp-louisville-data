import argparse
import os
from pathlib import Path

import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

from blocks.const import BLOCK_BUCKET_NAME, BLOCK_CREDS_NAME, BQ_DATASET, PROJECT_ID
from .web_to_gcs_etl import DataFormat, get_format, get_data_folder, filename_from_year

@task()
def extract_from_gcs(year: int) -> Path:
    """Download trip data from GCS"""
    data_folder = get_data_folder()
    filename = filename_from_year(year)
    gcs_path = f"{data_folder}/{filename}.parquet"
    gcs_block = GcsBucket.load(BLOCK_BUCKET_NAME)
    gcs_block.get_directory(from_path=gcs_path, local_path=f"./")
    return Path(f"./{gcs_path}")

@task()
def transform(path: Path) -> pd.DataFrame:
    """ Transforming data to consolidate Agency names across years.
    Each data format has a different Agency column name. It might be better
    to allow dbt to make these transformations and keep the original
    data in the BigQuery table."""
    df = pd.read_parquet(path)

    agency_column:str
    df_format = get_format(df)
    if df_format == DataFormat.FMT1_2008:
        agency_column='Agency_Name'
    if df_format == DataFormat.FMT2_2018:
        agency_column='agency'

    def map_agency(agency: str):
        POLICE_DEPT = 'Louisville Metro Police Department'
        PUBLIC_WORKS = 'Public Works & Assets Department'

        agency_lc = agency.lower()
        if 'police' in agency_lc:
            return POLICE_DEPT
        if 'public works' in agency_lc:
            return PUBLIC_WORKS
        return agency

    df[agency_column] = df[agency_column].map(map_agency)

    return df

@task()
def write_bq(df: pd.DataFrame) -> None:
    """Write DataFrame to BigQuery"""
    gcp_credentials_block:GcpCredentials = GcpCredentials.load(BLOCK_CREDS_NAME)

    data_format: DataFormat = get_format(df)
    format_name = data_format.name

    df.to_gbq(
        destination_table=f'{BQ_DATASET}.{format_name}_expenditure_data',
        project_id=PROJECT_ID,
        credentials= gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )

@flow()
def etl_gcs_to_bq(year):
    """Main ETL flow to load data into BigQuery"""
    path = extract_from_gcs(year)
    df = transform(path)
    write_bq(df)

# Parent flow to do 3 flows for 3 months
@flow()
def etl_parent_flow_bq(
    start_year: int=2017,
    end_year: int=2018
):
    print(os.getcwd())
    for year in range(start_year, end_year+1):
        etl_gcs_to_bq(year)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start ETL flow to extract CSV data to GCS in parquet format.')

    # These defaults will download 1 CSV for each data format, providing a good base test.
    parser.add_argument('--start_year', default=2017, help='First year in range to process. (Min: 2008)')
    parser.add_argument('--end_year', default=2018, help='Last year in range to process.')

    args = parser.parse_args()
    start_year = args.start_year
    end_year = args.end_year
    etl_parent_flow_bq(start_year, end_year)
