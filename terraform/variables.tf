locals {
  data_lake_bucket = "louisville_data_lake"
}

variable "project" {
  description = "Your GCP Project ID"
  type = string
  validation {
    condition = var.project != ""
    error_message = "The 'project' variable cannot be an empty string (ensure GCP_PROJECT_ID environment variable is set)."
  }
}

variable "region" {
  description = "Region for GCP resources. Choose as per your location: https://cloud.google.com/about/locations"
  default = "europe-west6"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket. Check official docs for more info."
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQuery Dataset that raw data (from GCS) will be written to"
  type = string
  default = "louisville_data_all"
}

variable "TABLE_NAME_FMT1_2008" {
  description= "BigQuery Table for Data in FMT1_2008 format"
  type = string
  default = "FMT1_2008_expenditure_data"
}

variable "TABLE_NAME_FMT2_2018" {
  description= "BigQuery Table for Data in FMT2_2018 format"
  type = string
  default = "FMT2_2018_expenditure_data"
}
