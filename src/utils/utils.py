import pandas as pd
import boto3
from io import BytesIO, StringIO

class AWS_tools:

    def __init__(self):
        self._key_secret = {
            'aws_access_key_id': AWS_key,
            'aws_secret_access_key': AWS_secret, 
            'region_name': AWS_region,
        }       
        self.s3 = boto3.client('s3', **self._key_secret) # to access files
        self.ses = boto3.client('ses', **self._key_secret) # to email data
    
    def df_to_bucket(self, df, file_name, bucket_name):
        "Convert Pandas df to csv and upload to aws bucket."
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=index)
        csv_content = csv_buffer.getvalue()
        self.s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_content)

    def bucket_to_df(self, file_name, bucket_name):
        "Get csv from bucket and convert to df"
        response = self.s3.get_object(Bucket=bucket_name, Key=file_name)
        content = response['Body'].read()
        df = pd.read_csv(BytesIO(content))
        return df
    
    def email_new_events(self, address_list, source_email_address, events_df):
        html = events_df.to_html(index=False, )

        CHARSET = "UTF-8"
        message = {
                "Body": {"Html": {"Charset": CHARSET, "Data": html}},
                "Subject": {"Charset": CHARSET, "Data": 'Tickets for Good: New Events'},
        }

        response = self.ses.send_email(
            Destination={"ToAddresses": address_list},
            Message=message,
            Source=source_email_address,
        )

    def update_AWS():
        # Upload newest scrape data to s3 bucket.
        bucket_name = 'ticketsforgood'
        file_name = 'last-search.csv'
        self.df_to_bucket(self._all_events_df, file_name, bucket_name)

