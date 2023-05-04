# Louisville Metro Expenditure Data Pipeline

## Project Goal

This project creates a data pipeline to load Louisville Metro (KY) expenditure data (via data.louisvilleky.gov) for comparison across fiscal years.  The comparisons include expenditures by department and type per year. Reports for each fiscal year can have different column names, so this project helps consolidate data and map related columns as well as resolve slight name differences in the agencies.

## Project Architecture

Necessary cloud infrastructure is created via Terraform. The data pipeline is orchestrated by a Prefect docker container, which creates tasks to download data and load it to a Google Cloud Storage (GCS) bucket.

The next stage will extract data from the GCS bucket, perform cleanup and transformations, and load it to Google Big Query. The final stage will be transformations using dbt to create a fact table for efficient data aggregation to the dashboard.

Although the entire data set is less than 1 GB, I've partitioned the data by fiscal year to fulfill the project requirements. 

## Install/Initialization

### Pre-requisites
* Docker Installed
* Terraform installed
* Google Cloud account
    * New project created
    * Google Cloud service account for this project with Storage and BigQuery roles. JSON Access key downloaded.
* Linux or WSL and ability to run `make`.

### Setup / Commands
1. Setup: Cloud Credentials / env variables / Docker install / WSL
    1.a Export environment variable for GCP_PROJECT_ID
    ```
    > export GCP_PROJECT_ID=<Project ID>
    ```
    1.b Download a service account JSON key for a service account with Storage and BigQuery roles. Place JSON file into the `credentials` directory with the name `gcp_service_account_key.json`
2. `make init` in the project directory. This will use terraform to create the necessary infrastructure, and build the docker containers
3. `make start`. This will start prefect containers to run the ETL task flows.
4. `make transform`. This will start the dbt container and run transformations.
5. `make stop` to stop containers
6. `make clean` to stop containers, remove volumes, and use terraform to take down resources created by this project.

## Dashboard
Google Data Studio dashboard can be viewed here: https://lookerstudio.google.com/reporting/dcd5e9e7-bf72-4a5b-addd-f1e0349159b9

## Future Improvmements

Include a script or optional parameter to download directly from the original data source instead of my repo with a snapshot. It should download their latest previously generated CSV, rather than requesting new report, to avoid excessive report generation on their end.

## Thanks

Thank you to everyone involved in DataTalksClub Data Engineering Zoomcamp 2023 for helping me improve my knowledge of data engineering concepts and tools involved in this project. https://github.com/DataTalksClub/data-engineering-zoomcamp

Also thanks to the Louisville Open Data portal for compiling and giving public access to this data.

Data license: PPDL (https://louisville-metro-opendata-lojic.hub.arcgis.com/pages/terms-of-use-and-license)
