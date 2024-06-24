import pandas as pd
import os
import datetime
from dotenv import load_dotenv
from src.html_generator.html_generator import render_html
from src.aws_utils.utils import AWS_tools

load_dotenv()


def send_emails(events, aws_instance, tfg_status):
  aws_bucket = os.getenv("AWS_BUCKET")
  source_email = os.getenv("SOURCE_EMAIL_ADDRESS")

  active_events = AWS_tools().bucket_to_df("active_events.csv", aws_bucket)
  active_events.time_added = pd.to_datetime(active_events.time_added, format='%d/%m/%y-%H:%M')
  active_events = active_events.dropna().sort_values("time_added")

  dt_now = datetime.datetime.now()
  day_of_week_now = dt_now.strftime("%A")

  users_df = aws_instance.bucket_to_df("users.csv", aws_bucket)
  users_df = pd.read_csv("users.csv")

  # collective email to users subscribed to all times
  users_all_times = users_df[(users_df.frequency == "hourly") & (users_df.locations == "All")]
  html_hourly_all_locs = render_html(events, tfg_status)
  aws_instance.send_email(
      address_list=users_all_times.email.unique(),
      source_email_address= source_email, 
      html=html_hourly_all_locs
  )

  # send personalised emails to rest
  users_remaining = users_df[(users_df.frequency != "hourly") & (users_df.locations != "All")]
  for user in users_remaining.itertuples():
    # hourly
    events_refined = active_events[active_events.location.str.contains(user.locations)]
    if user.frequency == "hourly":
      if len(events_refined) == 0: continue
      html = render_html(events_refined, tfg_status)
      aws_instance.send_email(address_list= user.email,source_email_address= source_email, html=html)
    # daily
    elif user.frequency == "daily" & dt_now.hour == 17:
      daily_events = events_refined[events_refined.time_added.dt.strftime("%d%m") == dt_now.strftime("%d%m")]
      if len(daily_events) == 0: continue
      html = render_html(daily_events, tfg_status)
      aws_instance.send_email(address_list= user.email, source_email_address= source_email, html=html)
    # weekly at 1700 on Fridays
    elif user.frequency == "weekly" & dt_now.hour == 17 & day_of_week_now == "Friday":
      weekly_events = events_refined[events_refined.time_added.dt.isocalendar().week == dt_now.isocalendar()[1]]
      if len(weekly_events) == 0: continue
      aws_instance.send_email(address_list= user.email, source_email_address= source_email, html=html)



    


  # Email new events 
  aws_instance.send_email(
      address_list=['callumtaylor955@gmail.com'], # , 'tomebbatson@live.co.uk', 'jennykent94@googlemail.com', 'emilypatrick01@hotmail.com', 'colindavid92@gmail.com']
      source_email_address='callumtaylor955@gmail.com', 
      html=html
  )
