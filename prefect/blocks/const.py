import os

PROJECT_ID = os.environ['GCP_PROJECT_ID']
# Concatenate with project ID for unique name
GCS_BUCKET_NAME = f'louisville_data_lake_{PROJECT_ID}'
BQ_DATASET = 'louisville_data_all'
GCS_CREDENTIALS_PATH = '/root/credentials/gcp_service_account_key.json'
BLOCK_CREDS_NAME = 'louisville-data-gcp-creds'
BLOCK_BUCKET_NAME = 'louisville-data-lake-bucket'
