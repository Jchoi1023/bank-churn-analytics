import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import bigquery
import os

# Connect to BigQuery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "bank-churn-analytics-da46589ffe82.json"
)

client = bigquery.Client(project="bank-churn-analytics")

# Load data
churn_df = client.query("""
    SELECT * FROM `bank-churn-analytics.dbt_jchoi.mart_churn_analysis`
""").to_dataframe()

ml_df = client.query("""
    SELECT * FROM `bank-churn-analytics.dbt_jchoi.ml_churn_predictions`
""").to_dataframe()

os.makedirs("images", exist_ok=True)

def clean_axes(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# 1. Churn Rate by Age Group
fig, ax = plt.subplots(figsize=(8, 5))
age_df = churn_df.groupby('age_group')['churn_rate'].mean().sort_values(ascending=False)
bars = ax.bar(age_df.index, age_df.values, color='steelblue')
ax.set_title('Churn Rate by Age Group', fontweight='bold', fontsize=14)
ax.set_ylabel('Churn Rate (%)')
for bar, val in zip(bars, age_df.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', fontsize=10)
clean_axes(ax)
plt.tight_layout()
plt.savefig('images/churn_by_age_group.png', dpi=150)
plt.close()

# 2. Churn Rate by Country
fig, ax = plt.subplots(figsize=(8, 5))
country_df = churn_df.groupby('country')['churn_rate'].mean().sort_values(ascending=False)
bars = ax.bar(country_df.index, country_df.values, color='steelblue')
ax.set_title('Churn Rate by Country', fontweight='bold', fontsize=14)
ax.set_ylabel('Churn Rate (%)')
for bar, val in zip(bars, country_df.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', fontsize=10)
clean_axes(ax)
plt.tight_layout()
plt.savefig('images/churn_by_country.png', dpi=150)
plt.close()

# 3. Churn Rate by Credit Score Tier
fig, ax = plt.subplots(figsize=(8, 5))
credit_df = churn_df.groupby('credit_score_tier')['churn_rate'].mean().sort_values(ascending=False)
bars = ax.bar(credit_df.index, credit_df.values, color='steelblue')
ax.set_title('Churn Rate by Credit Score Tier', fontweight='bold', fontsize=14)
ax.set_ylabel('Churn Rate (%)')
for bar, val in zip(bars, credit_df.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', fontsize=10)
clean_axes(ax)
plt.tight_layout()
plt.savefig('images/churn_by_credit_score.png', dpi=150)
plt.close()

# 4. Churn Rate by Balance Tier
fig, ax = plt.subplots(figsize=(8, 5))
balance_df = churn_df.groupby('balance_tier')['churn_rate'].mean().sort_values(ascending=False)
bars = ax.bar(balance_df.index, balance_df.values, color='steelblue')
ax.set_title('Churn Rate by Balance Tier', fontweight='bold', fontsize=14)
ax.set_ylabel('Churn Rate (%)')
for bar, val in zip(bars, balance_df.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val:.1f}%', ha='center', fontsize=10)
clean_axes(ax)
plt.tight_layout()
plt.savefig('images/churn_by_balance_tier.png', dpi=150)
plt.close()

# 5. Churn Probability by Risk Segment
fig, ax = plt.subplots(figsize=(8, 5))
risk_df = ml_df.groupby('risk_segment')['churn_probability'].mean().sort_values(ascending=False)
bars = ax.bar(risk_df.index, risk_df.values * 100, color='steelblue')
ax.set_title('Avg Churn Probability by Risk Segment', fontweight='bold', fontsize=14)
ax.set_ylabel('Avg Churn Probability (%)')
for bar, val in zip(bars, risk_df.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{val*100:.1f}%', ha='center', fontsize=10)
clean_axes(ax)
plt.tight_layout()
plt.savefig('images/ml_churn_probability.png', dpi=150)
plt.close()