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
    os.path.dirname(os.path.abspath(__file__)),
    "bank-churn-analytics-5ccec03d41f1.json"
)

client = bigquery.Client(project="bank-churn-analytics")

# Load data from BigQuery
query = """
SELECT *
FROM `bank-churn-analytics.dbt_jchoi.stg_customers`
"""
df = client.query(query).to_dataframe()
print("Data loaded:", df.shape)

# ── 1. Logistic Regression Model ────────────────────
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

# Train logistic regression model with class balancing
model = LogisticRegression(random_state=42, class_weight='balanced')
model.fit(X_train_scaled, y_train)

print("\n── Model Performance ──")
print(classification_report(y_test, model.predict(X_test_scaled)))

# ── 2. Predict churn probability ─────────────────────
df['churn_probability'] = model.predict_proba(scaler.transform(X[features]))[:, 1]

# Classify into risk segments
df['risk_segment'] = df['churn_probability'].apply(
    lambda x: 'High Risk' if x >= 0.6 else ('Medium Risk' if x >= 0.4 else 'Low Risk')
)

print("\n── Risk Segment Distribution ──")
print(df['risk_segment'].value_counts())

# ── 3. Save results to BigQuery ───────────────────────
output_df = df[['customer_id', 'country', 'gender', 'age',
                'credit_score', 'balance', 'churn',
                'churn_probability', 'risk_segment']].copy()

output_df.to_gbq(
    destination_table="dbt_jchoi.ml_churn_predictions",
    project_id="bank-churn-analytics",
    if_exists="replace"
)

print("\n ML predictions saved to BigQuery: dbt_jchoi.ml_churn_predictions")

coef_df = pd.DataFrame({
    'feature': features,
    'coefficient': model.coef_[0]
}).sort_values(by='coefficient', ascending=False)

print("\n── Logistic Regression Coefficients ──")
print(coef_df)