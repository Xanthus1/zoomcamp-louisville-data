{{ config(materialized='table') }}

select
    ObjectId as object_id,
    Fiscal_Year as fiscal_year,
    InvoiceDt as invoice_date,
    InvoiceID as invoice_id,
    InvoiceAmt as invoice_amount,
    Vendor_Name as payee,
    Budget_Type as budget_type,
    Agency_Name as agency,
    Sub_Agency_Name as sub_agency,
    DepartmentName as department,
    Category as expenditure_category,
    Sub_Category as expenditure_sub_category,
    Funding_Source as funding_source,
    CheckID as payment_id,
    CheckDt as payment_date,
    CheckAmt as payment_amount,
from {{ source('staging', 'FMT1_2008_expenditure_data') }}
