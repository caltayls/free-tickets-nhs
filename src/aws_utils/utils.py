import pandas as pd
import boto3
from io import BytesIO, StringIO
import datetime

with open(r"C:\Users\callu\OneDrive\Desktop\aws-key.txt", 'r') as f:
    key = f.readline().strip('\n')
    sec = f.readline().strip('\n')

class AWS_tools:

    def __init__(self,):

        with open(r"C:\Users\callu\OneDrive\Desktop\aws-key.txt", 'r') as f:
            key = f.readline().strip('\n')
            sec = f.readline().strip('\n')
        
        self._key_secret = {
            'aws_access_key_id': key,
            'aws_secret_access_key': sec, 
            'region_name': 'eu-west-2',
        }       
        self.s3 = boto3.client('s3', **self._key_secret) # to access files
        self.ses = boto3.client('ses', **self._key_secret) # to email data
    
    def df_to_bucket(self, df, file_name, bucket_name):
        "Convert Pandas df to csv and upload to aws bucket."
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        self.s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_content)

    def bucket_to_df(self, file_name, bucket_name):
        "Get csv from bucket and convert to df"
        response = self.s3.get_object(Bucket=bucket_name, Key=file_name)
        content = response['Body'].read()
        df = pd.read_csv(BytesIO(content))
        return df
    
    def send_email(self, address_list, source_email_address, html):
        # html = events_df.to_html(index=False, )

        CHARSET = "UTF-8"
        message = {
                "Body": {"Html": {"Charset": CHARSET, "Data": html}},
                "Subject": {"Charset": CHARSET, "Data": 'New Events'},
        }

        response = self.ses.send_email(
            Destination={"ToAddresses": address_list},
            Message=message,
            Source=source_email_address,
        )





def compare_previous_search(df, aws_tools_instance, bucket_name='nhs-free-events', file_name='active_events.csv'):
        """Compare newest event dataframe with previous and compare to find new events."""

        df_prev = aws_tools_instance.bucket_to_df(file_name, bucket_name)
        # Create url sets for both dataframes. Returns a list of urls that are in newer df and not the other.
        urls_prev = set(df_prev.url)
        urls_new = set(df.url)

        # create logic to check if event is sold out.
        # event will be added back if more tickets added.

        diff_list = [*urls_new.difference(urls_prev)]
        new_events_df = df.loc[df.url.isin(diff_list)]
        return new_events_df

def update_event_history(new_events, aws_tools_instance):
    timestamp = datetime.datetime.now().strftime("%d/%m/%y-%H:%M")
    new_events['timestamp'] = timestamp
    new_events = new_events.drop(['url', 'website'], axis=1)
    try:
        event_history_df = aws_tools_instance.bucket_to_df('event_history.csv', 'nhs-free-events')
        event_history_df = pd.concat((event_history_df, new_events))
        aws_tools_instance.df_to_bucket(event_history_df, 'event_history.csv', 'nhs-free-events')
    
    # If file is empty:
    except:
        aws_tools_instance.df_to_bucket(new_events, 'event_history.csv', 'nhs-free-events')

if __name__ == '__main__':
    with open(r'C:\Users\callu\OneDrive\Documents\coding\webscrape\ticket_checker_app\ticket_checker_app\src\html_templates\new_events_email_template\new_events_email.html', 'r') as f:
        html = f.read()


    AWS_tools(key, sec).send_email(address_list=['callumtaylor955@gmail.com'], source_email_address='callumtaylor955@gmail.com', html=html)



