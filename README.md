# Louisville Metro Expenditure Data Pipeline

## Project Goal

This project creates a data pipeline to load Louisville Metro (KY) expenditure data (via data.louisvilleky.gov) for comparison across fiscal years.  The comparisons include expenditures by department and type per year. Reports for each fiscal year can have different column names, so this project helps consolidate data and map related columns.

## Project Architecture

Necessary cloud infrastructure is created via Terraform. The data pipeline is orchestrated by a Prefect docker container, which creates tasks to download data and load it to a Google Cloud Storage (GCS) bucket.

The next stage will extract data from the GCS bucket, perform cleanup and transformations, and load it to Google Big Query. The final stage will be transformations using dbt to create a fact table for efficient data aggregation to the dashboard.

## Install/Initialization

### Pre-requisites
* Docker Installed
* Terraform installed
* Google Cloud account
    * New project created
    * Google Cloud service account for this project with Storage and BigQuery roles. JSON Access key downloaded.
* Linux or WSL

### Setup
1. Setup: Cloud Credentials / env variables / Docker install / WSL
    1.a Export environment variable for GCP_PROJECT_ID
    ```
    > export GCP_PROJECT_ID=<Project ID>
    ```
    1.b Download a service account JSON key for a service account with Storage and BigQuery roles. Place JSON file into the `credentials` directory with the name `gcp_service_account_key.json`
2. Terraform initialization
    ```
    # In the '/terraform' directory
    > terraform init
    > terraform plan -var project=${GCP_PROJECT_ID}
    > terraform apply -var project=${GCP_PROJECT_ID}
    ```
3. Docker containers / Prefect services (Start Orion/ and agents?). Metabase?
4. DBT transformation into fact tables (cloud or local instance?)
5. Dashboard?
6. Running flow / scheduling?

## Improvmements

Include a script or optional parameter to download directly from the original data source instead of my repo with a snapshot. It should download their latest previously generated CSV, rather than requesting new report, to avoid excessive report generation on their end.

## Thanks

Thank you to everyone involved in DataTalksClub Data Engineering Zoomcamp 2023 for helping me improve my knowledge of data engineering concepts and tools involved in this project. https://github.com/DataTalksClub/data-engineering-zoomcamp

Also thanks to the Louisville Open Data portal for compiling and giving public access to this data.

Data license: PPDL (https://louisville-metro-opendata-lojic.hub.arcgis.com/pages/terms-of-use-and-license)
