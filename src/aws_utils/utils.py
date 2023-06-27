import pandas as pd
import boto3
from io import BytesIO, StringIO

with open(r"C:\Users\callu\OneDrive\Desktop\aws-key.txt", 'r') as f:
    key = f.readline().strip('\n')
    sec = f.readline().strip('\n')

class AWS_tools:

    def __init__(self, AWS_key, AWS_secret,):
        self._key_secret = {
            'aws_access_key_id': AWS_key,
            'aws_secret_access_key': AWS_secret, 
            'region_name': 'eu-west-2',
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
    
    def send_email(self, address_list, source_email_address, html):
        # html = events_df.to_html(index=False, )

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


if __name__ == '__main__':
    with open(r'C:\Users\callu\OneDrive\Documents\coding\webscrape\ticket_checker_app\ticket_checker_app\src\html_templates\new_events_email_template\new_events_email.html', 'r') as f:
        html = f.read()


    AWS_tools(key, sec).send_email(address_list=['callumtaylor955@gmail.com'], source_email_address='callumtaylor955@gmail.com', html=html)



