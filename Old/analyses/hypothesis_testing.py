import os
import pandas as pd
from google.cloud import bigquery
from scipy.stats import chi2_contingency

# Connect to BigQuery using Application Default Credentials
client = bigquery.Client(project="bank-churn-analytics")

# Load dbt mart table
query = """
SELECT
    age,
    churn
FROM `bank-churn-analytics.dbt_jchoi.stg_customers`
WHERE age IS NOT NULL
AND churn IS NOT NULL
"""

df = client.query(query).to_dataframe()

# Create high-risk age segment
df["age_46_60"] = df["age"].between(46, 60)

# Build contingency table
table = pd.crosstab(df["age_46_60"], df["churn"])

print("Contingency Table:")
print(table)

# Chi-square test
chi2, p_value, dof, expected = chi2_contingency(table)

print("\nChi-square statistic:", round(chi2, 4))
print("P-value:", p_value)

# Interpretation
alpha = 0.05

if p_value < alpha:
    print("\nReject H0")
    print("Customers aged 46–60 churn at significantly higher rates.")
else:
    print("\nFail to reject H0")
    print("No statistically significant churn difference found.")