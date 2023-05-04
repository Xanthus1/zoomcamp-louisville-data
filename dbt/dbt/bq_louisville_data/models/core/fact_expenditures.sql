{{ config(materialized='table') }}
-- Use the `ref` function to select from other models

with fmt1_data as (
    select *
        from {{ ref('stg_fmt1_2008_expenditures') }}
),

fmt2_data as (
    select *
        from {{ ref('stg_fmt2_2018_expenditures')}}
),

data_unioned as (
    select * from fmt1_data
    union all
    select * from fmt2_data
)

select
    data_unioned.object_id,
    data_unioned.fiscal_year,
    data_unioned.agency,
    data_unioned.payment_amount,
    data_unioned.payee,
    data_unioned.payment_date,
    data_unioned.expenditure_category,
    data_unioned.expenditure_sub_category
from data_unioned
