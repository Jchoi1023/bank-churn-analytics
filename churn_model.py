# ============================================
# 1. Import Required Libraries
# ============================================

import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics import recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ============================================
# 2. Load Environment Variables
#    - Read Cloud SQL credentials from .env
# ============================================

load_dotenv()


# ============================================
# 3. Connect to Cloud SQL PostgreSQL
# ============================================

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


# ============================================
# 4. Load Analytics Dataset
#    - Read SQL View created in PostgreSQL
# ============================================

df = pd.read_sql(
    "SELECT * FROM public.vw_bank_churn_analytics",
    engine
)

print("Dataset Loaded Successfully")
print(df.shape)


# ============================================
# 5. Convert Categorical Variables
#    - One-Hot Encoding
# ============================================

df = pd.get_dummies(
    df,
    columns=[
        "country",
        "gender",
        "age_segment",
        "balance_tier",
        "engagement_level"
    ],
    drop_first=True
)


# ============================================
# 6. Define Features (X) and Target (y)
# ============================================

X = df.drop(
    columns=["customer_id", "churn"]
)

y = df["churn"]


# ============================================
# 7. Train-Test Split
#    - 80% Training
#    - 20% Testing
# ============================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ============================================
# 8. Build Logistic Regression Pipeline
#
# StandardScaler:
#   Standardizes numeric variables
#
# class_weight='balanced':
#   Handles class imbalance problem
#
# max_iter=5000:
#   Prevents convergence issues
# ============================================

model = Pipeline([
    ("scaler", StandardScaler()),
    ("logreg", LogisticRegression(
        max_iter=5000,
        class_weight="balanced"
    ))
])


# ============================================
# 9. Train Model
# ============================================

model.fit(X_train, y_train)


# ============================================
# 10. Generate Predictions
# ============================================

pred = model.predict(X_test)


# ============================================
# 11. Evaluate Model Performance
# ============================================

print(classification_report(y_test, pred))

print(
    "Recall:",
    round(recall_score(y_test, pred), 4)
)


# ============================================
# 12. Generate Churn Probability Scores
#    - Probability customer will churn
# ============================================

churn_probability = model.predict_proba(X_test)[:, 1]

results = X_test.copy()

results["actual_churn"] = y_test.values
results["predicted_churn"] = pred
results["churn_probability"] = churn_probability


# ============================================
# 13. Create Risk Tier Segmentation
#
# Low Risk    : 0 - 30%
# Medium Risk : 30 - 70%
# High Risk   : 70 - 100%
# ============================================

results["risk_tier"] = pd.cut(
    results["churn_probability"],
    bins=[0, 0.3, 0.7, 1.0],
    labels=["Low", "Medium", "High"]
)

print("\nRisk Tier Distribution")
print(results["risk_tier"].value_counts())


# ============================================
# 14. Identify Highest Risk Customers
# ============================================

top_risk = results.sort_values(
    by="churn_probability",
    ascending=False
)

print("\nTop 20 Highest Risk Customers")

print(
    top_risk[
        [
            "churn_probability",
            "risk_tier",
            "actual_churn",
            "predicted_churn"
        ]
    ].head(20)
)


# ============================================
# 15. Create Power BI Dashboard Dataset
#    - Keep original categorical columns
# ============================================

dashboard_dataset = pd.read_sql(
    "SELECT * FROM public.vw_bank_churn_analytics",
    engine
)

dashboard_dataset["churn_probability"] = model.predict_proba(X)[:, 1]

dashboard_dataset["risk_tier"] = pd.cut(
    dashboard_dataset["churn_probability"],
    bins=[0, 0.3, 0.7, 1.0],
    labels=["Low", "Medium", "High"]
)


# ============================================
# 16. Save Results to PostgreSQL
# ============================================

dashboard_dataset.to_sql(
    "churn_dashboard_dataset",
    engine,
    if_exists="replace",
    index=False
)

print("\nSaved to PostgreSQL")
print("public.churn_dashboard_dataset")


# ============================================
# 17. Export Dataset to CSV
# ============================================

dashboard_dataset.to_csv(
    "churn_dashboard_dataset.csv",
    index=False
)

print("\nCSV file saved!")
print(os.getcwd())
print(dashboard_dataset.columns)