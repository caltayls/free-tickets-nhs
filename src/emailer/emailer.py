import pandas as pd
import os
from dotenv import load_dotenv
from src.html_generator.html_generator import render_html
from src.aws_utils.utils import AWS_tools

load_dotenv()
aws_bucket = os.getenv("AWS_BUCKET")
active = AWS_tools().bucket_to_df("active_events.csv", aws_bucket)
active.time_added.unique()

active.time_added = pd.to_datetime(active.time_added, format='%d/%m/%y-%H:%M')
active = active.dropna().sort_values("time_added")
active



users_df = pd.read_csv("users.csv")

events = pd.read_csv("event_history.csv")
events.sort_values("time_added", ascending=False)
events[events.location.str.contains('Newcastle | Brighton | Salford')]


for user in users_df.itertuples():
  if user.frequency == "hourly":


    



  # send_emails(new_events):
  #   iterate through user csv
  #   check requested freq
  #   check requested locations
def send_emails(events, aws_instance, tfg_status):
  users_df = aws_instance.bucket_to_df("users.csv", aws_bucket)
    
  template_path = r"/src/html_templates/new_events_email_template/jinja_template.html"
  html = render_html(events, tfg_status, template_path)

  # Email new events 
  aws_instance.send_email(
      address_list=['callumtaylor955@gmail.com'], # , 'tomebbatson@live.co.uk', 'jennykent94@googlemail.com', 'emilypatrick01@hotmail.com', 'colindavid92@gmail.com']
      source_email_address='callumtaylor955@gmail.com', 
      html=html
  )
