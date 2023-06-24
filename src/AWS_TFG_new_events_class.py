import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import boto3
from io import BytesIO, StringIO


class FindNewEventsTFG:
    """
    TODO:
            - Add documentation
            - Generalise bucket/key use. Only works for my bucket/files.
            - Add property decorators for all_events_df
    """
    
    def __init__(self, AWS_key, AWS_secret, tfg_username, tfg_password, AWS_region='eu-west-2'):
        self._key_secret = {'aws_access_key_id': AWS_key,
                           'aws_secret_access_key': AWS_secret,
                            'region_name': AWS_region
                           }       
        self.s3 = boto3.client('s3', **self._key_secret) # to access files
        self.ses = boto3.client('ses', **self._key_secret) # to email data
        
        # Tickets For Good credentials
        self.tfg_username = tfg_username
        self.tfg_password = tfg_password
              
        self._all_events_df = None
        self._new_events_df = None
    
    def _get_html(self):
        with requests.Session() as session: # create a session so login is cached and cookies are stored
            # Get the authenticity token from the login page
            login_url = 'https://nhs.ticketsforgood.co.uk/users/sign_in'
            response = session.get(login_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            form = soup.select_one("form.simple_form[action='/users/sign_in']")
            authenticity_token = form.select_one("input[name*='auth']")['value']

            login_data = {
                'authenticity_token': authenticity_token, # can't log in without token
                'user[email]': self.tfg_username,
                'user[password]': self.tfg_password,
                'commit': 'Log in' # this posts the log in
            }
            headers = {
                'Referer': login_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }

            # Login to the webpage
            session.post(login_url, data=login_data, headers=headers)

            # Access the webpage after logging in
            page_url = 'https://nhs.ticketsforgood.co.uk'
            response = session.get(page_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find number of pages to search
            last_page_num_el = soup.select("li.page-item a")[-1]['href']
            last_page_num = int(re.search('\d+', last_page_num_el).group())

            events_html_lst = []
            for i in range(last_page_num):
                url = rf'https://nhs.ticketsforgood.co.uk/?page={i+1}'
                response = session.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                event_cards = soup.select("div[class*='col-xl']")
                events_html_lst += event_cards
                time.sleep(1) # to avoid overloading server

            return events_html_lst

    def get_all_events(self):  
        html_list = self._get_html()
        events_list = []
        for event in html_list:
            name = event.select_one("h5[class*='card-title']").string.strip('\n')
            info = [element.string.strip('\n') for element in event.select('div.col')]
            [location, dates, event_type] = info
            url_ext = event.select_one("a[class*='btn']")['href']

            event_dic = {'name': name, 'event_type': event_type, 'location': location, 'dates': dates, 'url': url_ext}
            events_list.append(event_dic)

        df = pd.DataFrame(events_list)
        df.dates = df.dates.str.replace('\n', '')
        df.event_type =  df.event_type.str.replace("^\W+$", 'Not Listed', regex=True)
        url_base = r"https://nhs.ticketsforgood.co.uk/"
        df['url'] = url_base + df.url 
       
        return df


    def _compare_previous_search(self, df):
        """compare full search dfs NOT new events df"""
        # df_prev = get_last_search()
        bucket_name = 'ticketsforgood'
        file_name = 'last-search.csv'
        df_prev = self.bucket_to_df(file_name, bucket_name)
        # Create url sets for both dataframes. Returns a list of urls that are in newer df and not the other.
        urls_prev_search = set(df_prev.url)
        urls_new_search = set(df.url)
        new_urls = [*urls_new_search.difference(urls_prev_search)]
        new_events = df.loc[df.url.isin(new_urls)]

        return changes
    
    def get_new_events(self, auto_update=False):
        self._all_events_df = self.get_all_events() ### upload to bucket
        self._new_events_df = self._compare_previous_search(self._all_events_df) ### for email only
        # if auto_update:
        #     self.update_AWS()
        
        return self._new_events_df




            
