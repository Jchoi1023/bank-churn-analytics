import pandas as pd
from scipy import stats
from google.cloud import bigquery
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import os

# Connect to BigQuery
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(__file__),
    "bank-churn-analytics-da46589ffe82.json"
)

client = bigquery.Client(project="bank-churn-analytics")

# Load data from BigQuery
query = """
SELECT *
FROM `bank-churn-analytics.dbt_jchoi.stg_customers`
"""
df = client.query(query).to_dataframe()
print("Data loaded:", df.shape)

# ── 1. ML: Logistic Regression ──────────────────────
features = ['credit_score', 'age', 'tenure', 'balance',
            'products_number', 'credit_card', 'active_member', 'estimated_salary']

X = df[features]
y = df['churn']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train logistic regression model
model = LogisticRegression(random_state=42, class_weight='balanced')
model.fit(X_train_scaled, y_train)

print("\n── Model Performance ──")
print(classification_report(y_test, model.predict(X_test_scaled)))

# Predict churn probability for all customers
df['churn_probability'] = model.predict_proba(scaler.transform(X[features]))[:, 1]

# ── 2. Assign A/B Groups based on ML predictions ────
df['risk_segment'] = df['churn_probability'].apply(
    lambda x: 'High Risk' if x >= 0.6 else ('Medium Risk' if x >= 0.4 else 'Low Risk')
)

# Randomly assign Control/Treatment for High and Medium Risk only
df['ab_group'] = df.apply(
    lambda x: ('Control' if x['customer_id'] % 2 == 0 else 'Treatment')
    if x['risk_segment'] in ['High Risk', 'Medium Risk'] else None, axis=1
)

    # ── 3. Chi-square Test for statistical significance ──
print("\n── A/B Test Results ──")
print(f"{'Segment':<15} {'Control Churn Rate':<22} {'Treatment Churn Rate':<22} {'P-value':<10} {'Significant'}")
print("-" * 80)
for segment in ['High Risk', 'Medium Risk']:
    seg_df = df[df['risk_segment'] == segment]
    control = seg_df[seg_df['ab_group'] == 'Control']
    treatment = seg_df[seg_df['ab_group'] == 'Treatment']

    table = [
        [control['churn'].sum(), len(control) - control['churn'].sum()],
        [treatment['churn'].sum(), len(treatment) - treatment['churn'].sum()]
    ]

    chi2, p_value, dof, _ = stats.chi2_contingency(table)

    print(f"{segment:<15} {control['churn'].mean()*100:<22.2f} {treatment['churn'].mean()*100:<22.2f} {p_value:<10.4f} {'Yes' if p_value < 0.05 else 'No'}")

    # ── 4. Save ML results to BigQuery ──────────────────
output_df = df[['customer_id', 'country', 'gender', 'age', 
                'credit_score', 'balance', 'churn',
                'churn_probability', 'risk_segment', 'ab_group']].copy()

# Define table destination
table_id = "bank-churn-analytics.dbt_jchoi.ml_churn_predictions"

# Write to BigQuery
output_df.to_gbq(
    destination_table="dbt_jchoi.ml_churn_predictions",
    project_id="bank-churn-analytics",
    if_exists="replace",
    credentials=None  # uses GOOGLE_APPLICATION_CREDENTIALS
)

print("\n ML predictions saved to BigQuery: dbt_jchoi.ml_churn_predictions")