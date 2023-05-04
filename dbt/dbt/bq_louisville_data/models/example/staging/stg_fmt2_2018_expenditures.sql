{{ config(materialized='table') }}

select
    ObjectId as object_id,
    fiscal_year as fiscal_year,
    invoice_date as invoice_date,
    invoice_number as invoice_id,
    invoice_amount as invoice_amount,
    payee as payee,
    expenditure_type as budget_type,
    agency as agency,
    cost_center as sub_agency,
    agency as department,
    expenditure_category as expenditure_category,
    spend_category as expenditure_sub_category,
    fund as funding_source,
    payment_number as payment_id,
    payment_date as payment_date,
    extended_amount as payment_amount
from {{ source('staging', 'FMT2_2018_expenditure_data') }}
