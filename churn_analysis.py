import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from scipy.stats import chi2_contingency

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

query = """
SELECT *
FROM public.vw_bank_churn_analytics
"""

df = pd.read_sql(query, engine)

print(df.head())
print(df.shape)

print("\nOverall churn rate:")
print(round(df["churn"].mean() * 100, 2))

print("\nChurn rate by age segment:")
print(
    df.groupby("age_segment")["churn"]
    .mean()
    .mul(100)
    .round(2)
    .sort_values(ascending=False)
)

print("\nChurn rate by balance tier:")
print(
    df.groupby("balance_tier")["churn"]
    .mean()
    .mul(100)
    .round(2)
    .sort_values(ascending=False)
)

print("\nChurn rate by engagement level:")
print(
    df.groupby("engagement_level")["churn"]
    .mean()
    .mul(100)
    .round(2)
)

contingency_table = pd.crosstab(
    df["age_segment"],
    df["churn"]
)

chi2, p, dof, expected = chi2_contingency(contingency_table)

print("\nChi-Square Test Results")
print(f"Chi-square statistic: {chi2:.2f}")
print(f"P-value: {p:.6f}")
print(f"Degrees of freedom: {dof}")