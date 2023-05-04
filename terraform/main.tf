terraform {
  required_version = ">= 1.0"
  backend "local" {}
  required_providers {
    google = {
      source  = "hashicorp/google"
    }
  }
}

provider "google" {
  project = var.project
  region = var.region
  credentials = file("../credentials/gcp_service_account_key.json")  # Alternate to setting env variable GOOGLE_APPLICATION_CREDENTIALS
}

# Data Lake Bucket
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "data-lake-bucket" {
  # Concatenating DataLake bucket & Project name for unique naming
  name          = "${local.data_lake_bucket}_${var.project}"
  location      = var.region

  # Optional, but recommended settings:
  storage_class = var.storage_class
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 30  // days
    }
  }

  force_destroy = true
}

# Data Warehouse
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.BQ_DATASET
  project    = var.project
  location   = var.region
}

# Two tables: One for each of the formats expenditure data is provided in
# mapping between tables will be performed by dbt.
resource "google_bigquery_table" "table_FMT1_2008" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = var.TABLE_NAME_FMT1_2008
  
  range_partitioning {
    field = "Fiscal_Year"
    range {
      start = 2008
      end = 2099
      interval = 1
    }
  }

  schema = <<EOF
[
    {
        "name": "ObjectId",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "ObjectId"
    },
    {
        "name": "Fiscal_Year",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "Fiscal_Year"
    },
    {
        "name": "Budget_Type",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Budget_Type"
    },
    {
        "name": "Agency_Name",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Agency_Name"
    },
    {
        "name": "Sub_Agency_Name",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Sub_Agency_Name"
    },
    {
        "name": "DepartmentName",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "DepartmentName"
    },
    {
        "name": "Sub_DepartmentName",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Sub_DepartmentName"
    },
    {
        "name": "Category",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Category"
    },
    {
        "name": "Sub_Category",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Sub_Category"
    },
    {
        "name": "Stimulus_Type",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Stimulus_Type"
    },
    {
        "name": "Funding_Source",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Funding_Source"
    },
    {
        "name": "Vendor_Name",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "Vendor_Name"
    },
    {
        "name": "InvoiceID",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "InvoiceID"
    },
    {
        "name": "InvoiceDt",
        "type": "TIMESTAMP",
        "mode": "NULLABLE",
        "description": "InvoiceDt"
    },
    {
        "name": "InvoiceAmt",
        "type": "FLOAT64",
        "mode": "NULLABLE",
        "description": "InvoiceAmt"
    },
    {
        "name": "DistributionAmt",
        "type": "FLOAT64",
        "mode": "NULLABLE",
        "description": "DistributionAmt"
    },
    {
        "name": "CheckID",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "CheckID"
    },
    {
        "name": "CheckDt",
        "type": "TIMESTAMP",
        "mode": "NULLABLE",
        "description": "CheckDt"
    },
    {
        "name": "CheckAmt",
        "type": "FLOAT64",
        "mode": "NULLABLE",
        "description": "CheckAmt"
    },
    {
        "name": "CheckVoidDt",
        "type": "TIMESTAMP",
        "mode": "NULLABLE",
        "description": "CheckVoidDt"
    }
]
EOF
}

resource "google_bigquery_table" "table_FMT2_2018" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id = var.TABLE_NAME_FMT2_2018
  deletion_protection=false

  range_partitioning {
    field = "fiscal_year"
    range {
      start = 2008
      end = 2099
      interval = 1
    }
  }

  schema = <<EOF
[
    {
        "name": "ObjectId",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "ObjectId"
    },
    {
        "name": "fiscal_year",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "fiscal_year"
    },
    {
        "name": "invoice_date",
        "type": "TIMESTAMP",
        "mode": "NULLABLE",
        "description": "invoice_date"
    },
    {
        "name": "invoice_number",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "invoice_number"
    },
    {
        "name": "invoice_amount",
        "type": "FLOAT64",
        "mode": "NULLABLE",
        "description": "invoice_amount"
    },
    {
        "name": "payee",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "payee"
    },
    {
        "name": "payment_date",
        "type": "TIMESTAMP",
        "mode": "NULLABLE",
        "description": "payment_date"
    },
    {
        "name": "payment_number",
        "type": "INT64",
        "mode": "NULLABLE",
        "description": "payment_number"
    },
    {
        "name": "agency",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "agency"
    },
    {
        "name": "expenditure_type",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "expenditure_type"
    },
    {
        "name": "expenditure_category",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "expenditure_category"
    },
    {
        "name": "spend_category",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "spend_category"
    },
    {
        "name": "cost_center",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "cost_center"
    },
    {
        "name": "project",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "project"
    },
    {
        "name": "program",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "program"
    },
    {
        "name": "grant_",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "grant_"
    },
    {
        "name": "fund",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "fund"
    },
    {
        "name": "financing_source",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "financing_source"
    },
    {
        "name": "region",
        "type": "STRING",
        "mode": "NULLABLE",
        "description": "region"
    },
    {
        "name": "extended_amount",
        "type": "FLOAT64",
        "mode": "NULLABLE",
        "description": "extended_amount"
    }
]
EOF
}

