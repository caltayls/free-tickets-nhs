import boto3
import pandas as pd
from dotenv import load_dotenv
import os

from src.utils.utils import get_areas_from_county
load_dotenv()

def load_dynamodb() -> pd.DataFrame:
  dynamodb = boto3.resource('dynamodb', endpoint_url=os.getenv("DYNAMODB_ENDPOINT"))
  table = dynamodb.Table("users")
  response = table.scan()
  df = pd.DataFrame(response["Items"])
  df["weeklyUpdate"] = df["weeklyUpdate"].astype(bool)
  return df