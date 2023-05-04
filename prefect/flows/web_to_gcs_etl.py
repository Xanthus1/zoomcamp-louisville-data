import os
import argparse
from pathlib import Path
from datetime import timedelta
from enum import Enum

import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

from blocks.const import BLOCK_BUCKET_NAME


class DataFormat(Enum):
    """Formats are defined by the first year they were used"""
    FMT_UNKNOWN = -1
    FMT1_2008 = 1  # Used from 2008-2017
    FMT2_2018 = 2  # Used from 2018-2022

def get_format(df: pd.DataFrame) -> DataFormat:
    """ Returns which DataFormat the frame is in- different years have different 
    columns. """
    COLUMNS_2008 = ['ObjectId', 'Fiscal_Year', 'Budget_Type', 'Agency_Name',
       'Sub_Agency_Name', 'DepartmentName', 'Sub_DepartmentName', 'Category',
       'Sub_Category', 'Stimulus_Type', 'Funding_Source', 'Vendor_Name',
       'InvoiceID', 'InvoiceDt', 'InvoiceAmt', 'DistributionAmt', 'CheckID',
       'CheckDt', 'CheckAmt', 'CheckVoidDt']
    COLUMNS_2018 = ['ObjectId', 'fiscal_year', 'invoice_date', 'invoice_number',
       'invoice_amount', 'payee', 'payment_date', 'payment_number', 'agency',
       'expenditure_type', 'expenditure_category', 'spend_category',
       'cost_center', 'project', 'program', 'grant_', 'fund',
       'financing_source', 'region', 'extended_amount']
    if set(COLUMNS_2008) == set(df.columns):
        return DataFormat.FMT1_2008
    if set(COLUMNS_2018) == set(df.columns):
        return DataFormat.FMT2_2018
    return DataFormat.FMT_UNKNOWN

def filename_from_year(year: int) -> str:
    dataset_file = f'Louisville_Metro_KY_-_Expenditures_Data_For_Fiscal_Year_{year}'
    return dataset_file

def get_data_folder() -> str:
    """ Helper function to return data folder path, for consistency
    and easier refactoring separate folders are needed in
    the future based on parameters. For local file paths and 
    paths in a GCS bucket."""
    return 'data'

@task(retries=3, cache_expiration=timedelta(days=1))
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read csv data from web into pandas DataFrame"""
    df = pd.read_csv(dataset_url)
    return df

@task()
def fetch_local(file_path: Path) -> pd.DataFrame:
    """Read csv data from local file path into pandas DataFrame"""
    df = pd.read_csv(file_path)
    return df

@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Resolve any data type issues. Based on formatting"""

    data_format: DataFormat = get_format(df)
    if data_format == DataFormat.FMT1_2008:
        df = clean_format_2008(df)
    elif data_format == DataFormat.FMT2_2018:
        df = clean_format_2018(df)    
    else:
        exc_msg = f"Unknown DataFormat on cleaning Dataframe: {data_format}. "\
            f"Columns: {df.columns}"
        raise Exception(exc_msg)
    return df

def clean_format_2008(df: pd.DataFrame) -> pd.DataFrame:
    """ Cleans the data for the 2008 DataFormat. Corcering bad date data
    to be 'NaT' (Not a Time). Ran into this issue for 2012's data.
    
    I found non-integer InvoiceIDs as well. I may need to change this column
    to a string in BigQuery"""
    df['InvoiceDt'] = pd.to_datetime(df['InvoiceDt'], errors='coerce')
    df['InvoiceID'] = pd.to_numeric(df['InvoiceID'], errors='coerce')
    df['CheckDt'] = pd.to_datetime(df['CheckDt'], errors='coerce')
    df['CheckVoidDt'] = pd.to_datetime(df['CheckVoidDt'], errors='coerce')
    return df

def clean_format_2018(df: pd.DataFrame) -> pd.DataFrame:
    """ Cleans the data for the 2018 DataFormat"""
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], errors='coerce')
    df['payment_date'] = pd.to_datetime(df['payment_date'], errors='coerce')
    return df

@task()
def write_local(df: pd.DataFrame, dataset_file: str) -> Path:
    """Write DataFrame out as a local parquet file.
    Organized into directories using the data format
    """
    if not os.path.exists(f"data"):
        print("Creating target directory")
        os.makedirs(f"data")

    data_folder = get_data_folder()
    path = Path(f"{data_folder}/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task()
def write_gcs(file_path: Path) -> None:
    """Uploading local parquet file to GCS (Google Cloud Storage)"""
    gcs_block: GcsBucket = GcsBucket.load(BLOCK_BUCKET_NAME)
    gcs_block.upload_from_path(
        from_path=file_path,
        to_path=file_path
    )
    return

@flow()
def etl_to_gcs(year: int) -> None:
    """The main ETL function"""
    dataset_file = filename_from_year(year)
    df: pd.DataFrame
    
    # TODO: setting or option to download from original source
    # E.g.: download button on https://data.louisvilleky.gov/datasets/louisville-metro-ky-expenditures-data-for-fiscal-year-<YEAR>/about
    dataset_url = f"https://github.com/Xanthus1/louisville-expenditure-data/releases/download/v1.0/{dataset_file}.csv.gz"
    df = fetch(dataset_url)
    df_clean = clean(df)

    # write locally first as parquet
    file_path = write_local(df_clean, dataset_file)
    write_gcs(file_path)

# Parent flow to do 1 subflow for each year
@flow()
def etl_parent_flow(start_year: int = 2017, end_year: int = 2018):
    for year in range(start_year, end_year+1):
        etl_to_gcs(year)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start ETL flow to extract CSV data to GCS in parquet format.')

    # These defaults will download 1 CSV for each data format, providing a good base test.
    parser.add_argument('--start_year', default=2017, help='First year in range to process. (Min: 2008)')
    parser.add_argument('--end_year', default=2018, help='Last year in range to process.')
    
    args = parser.parse_args()
    start_year = args.start_year
    end_year = args.end_year

    etl_parent_flow(start_year, end_year)
