with source as (
    select * from {{ source('bank_churn_raw', 'raw_customer') }}
),

renamed as (
    select
        customer_id,
        credit_score,
        country,
        gender,
        age,
        tenure,
        balance,
        products_number,
        credit_card,
        active_member,
        estimated_salary,
        churn
    from source
)

select * from renamed