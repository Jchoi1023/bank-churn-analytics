from google.cloud import storage
import pandas as pd

project_id = "bank-churn-analytics"
bucket_name = "bank-churn-analytics-project"
file_name = "Bank Customer Churn Prediction.csv"

client = storage.Client(project=project_id)

bucket = client.bucket(bucket_name)
blob = bucket.blob(file_name)

df = pd.read_csv(blob.open("r"))

print(df.head())
print(df.shape)
print(df.columns.tolist())