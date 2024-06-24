import boto3
import pandas as pd

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')

table = dynamodb.Table("users")
response = table.scan()
df = pd.DataFrame(response["Items"])

df["weeklyUpdate"] = df["weeklyUpdate"].astype(bool)
df
