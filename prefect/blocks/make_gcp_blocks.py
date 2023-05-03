import os

from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket

from blocks.const import GCS_BUCKET_NAME, GCS_CREDENTIALS_PATH, \
    BLOCK_CREDS_NAME, BLOCK_BUCKET_NAME

# alternative to creating GCP blocks in the UI
# copy your own service_account_info dictionary from the json file you downloaded from google
# IMPORTANT - do not store credentials in a publicly available repository!

credentials_block = GcpCredentials(
    service_account_file=GCS_CREDENTIALS_PATH  # enter your credentials from the json file
)
credentials_block.save(BLOCK_CREDS_NAME, overwrite=True)

bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load(BLOCK_CREDS_NAME),
    bucket=GCS_BUCKET_NAME,  # insert your  GCS bucket name
)

bucket_block.save(BLOCK_BUCKET_NAME, overwrite=True)