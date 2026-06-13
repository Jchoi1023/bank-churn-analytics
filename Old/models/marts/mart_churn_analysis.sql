with customers as (
    select * from {{ ref('stg_customers') }}
),

churn_summary as (
    select
        country,
        gender,
        case
            when age < 30 then 'Under 30'
            when age between 30 and 45 then '30-45'
            when age between 46 and 60 then '46-60'
            else 'Over 60'
        end as age_group,
        case
            when credit_score < 580 then 'Poor'
            when credit_score between 580 and 669 then 'Fair'
            when credit_score between 670 and 739 then 'Good'
            else 'Excellent'
        end as credit_score_tier,
        case
            when balance = 0 then 'Zero Balance'
            when balance < 50000 then 'Low'
            when balance between 50000 and 100000 then 'Medium'
            else 'High'
        end as balance_tier,
        count(*) as total_customers,
        sum(churn) as churned_customers,
        round(safe_divide(sum(churn), count(*)) * 100, 2) as churn_rate,
        round(avg(balance), 2) as avg_balance,
        round(avg(credit_score), 2) as avg_credit_score,
        round(avg(tenure), 2) as avg_tenure
    from customers
    group by 1, 2, 3, 4, 5
)

select * from churn_summary