from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

import os

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
    """ Placeholder for necessary data cleaning / transformations"""
    df = pd.read_parquet(path)
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
    start_year = 2017
    end_year = 2018
    etl_parent_flow_bq(2017, 2018)
 