import pandas as pd
import asyncio
from bs4 import BeautifulSoup
import re
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()



  
class EventParser:
    is_tfg_logged_in = None # Used to check if log in is successful

    def __init__(self, website):
        self.website = website
        if __name__ != '__main__':
            site_info_path = os.path.join(os.path.dirname(__file__), './site_info.json')
        else:
            site_info_path = "src/parse_events/site_info.json"
        with open(site_info_path, "r") as file:
            info_all_sites = json.load(file)
        self.site_info = info_all_sites[self.website]


    async def fetch_html(self):
        card_html = None # Think there was a gotcha without... not sure but it stays
        async with aiohttp.ClientSession() as session: 
            if self.website == 'ticketsforgood':
                await self.login(session)
            page_url =  self.site_info['URL_BASE'] + self.site_info['FIRST_PAGE_REL_PATH']
            async with session.get(page_url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
            if self.website == 'ticketsforgood':
                EventParser.is_tfg_logged_in = self.is_logged_in(soup)
            
            # Find number of pages to search
            if not re.search('concertsforcarers', self.site_info['URL_BASE']): # This can be made simpler now
            # if self.website != 'concertsforcarers':
                last_page_num_el = soup.select(self.site_info['LAST_PAGE_ELEMENT_SEL'])[-1]['href']
                last_page_num = int(re.search(self.site_info['LAST_PAGE_TEXT_PAT'], last_page_num_el).group(1))
            else:
                last_page_num = 1
            # Iterate through pages and collect event_card_html. Pages are scraped concurrently (set to two to reduce traffic)
            tasks = []
            sem = asyncio.Semaphore(2) # Restricts concurrent tasks to 2. i.e. only allows two iterations of loop to happen simultaneously.
            # for i in range(last_page_num):
            for i in range(last_page_num): 
                page_ext = self.site_info['PAGE_QUERY_REL_PATH']
                if self.website != 'concertsforcarers':
                    page_ext += str(i+1)
                url = self.site_info['URL_BASE'] + page_ext
                task = asyncio.create_task(self.parse_event_cards(session, sem, url)) ### semaphore must be within async func or wont work
                tasks.append(task)
            completed_tasks = await asyncio.gather(*tasks)
            card_html = [card for sublist in completed_tasks for card in sublist]
    
            return card_html

        
        
    def html_to_dataframe(self, cards_html):  
        events_list = [self.parse_card_info(event) for event in cards_html]
        df = pd.DataFrame(events_list)
        df.date = df.date.str.replace('\n', '') 
        df['website'] = self.site_info['URL_BASE']
        if self.website == 'ticketsforgood':
            df.event_type =  df.event_type.str.replace("^\W+$", 'Not Listed', regex=True)
        return df


    async def parse_event_cards(self, session, sem, url):
        async with session.get(url) as response:
            async with sem:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                event_cards = soup.select(self.site_info['EVENT_CARD_SEL'])
                await asyncio.sleep(2) # Avoid overloading server
                return event_cards
            

    def parse_card_info(self, event_card):
        if self.website == 'ticketsforgood':
            event_name = event_card.select_one("h5[class*='card-title']").string.strip('\n')
            info = [element.string.strip('\n') for element in event_card.select('div.col')]
            [location, date, event_type] = info
            url_ext = event_card.select_one("a[class*='btn']")['href']
            event_dic = {'event_name': event_name, 'event_type': event_type, 'location': location, 'date': date, 'url': url_ext}
            return event_dic
        
        elif self.website == 'concertsforcarers':
            details = event_card.select('span')[:5]
            details_text = [element.text for element in details]
            event_name1, event_name2, location, _, date  = details_text
            if event_name1 != event_name2:
                event_name = f"{event_name1} - {event_name2}" # Event name is arranged awkwardly so needs combined
            else:
                event_name = event_name1
            url_ext = event_card.select_one("a.button")['href']
            event_dic = {'event_name':event_name, 'location': location, 'date': date, 'url': url_ext}
            return event_dic
        
        elif self.website == 'bluelighttickets':
            event_element_text = event_card.select_one("span").text
            event_name = event_element_text #.split('-')[0].strip() removes useful info
            event_info = event_card.select_one("p").contents
            date, location = [info.strip() for info in event_info if isinstance(info, str)]
            url_ext = event_card.select_one("a.btn-primary")['href']
            event_dic = {'event_name':event_name, 'location': location, 'date': date, 'url': url_ext}
            return event_dic



    
    async def login(self, session):
            # Get the authenticity token from the login page
            email = os.getenv("TFG_EMAIL")
            pw = os.getenv("TFG_PW")
            login_url = 'https://nhs.ticketsforgood.co.uk/users/sign_in'
            async with session.get(login_url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
            form = soup.select_one("form.simple_form[action='/users/sign_in']")
            authenticity_token = form.select_one("input[name*='auth']")['value']
            login_data = {
                'authenticity_token': authenticity_token, # can't log in without token
                'user[email]': email,
                'user[password]': pw,
                'commit': 'Log in' # this posts the log in
            }
            headers = {
                'Referer': login_url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }

            # Login to the webpage
            await session.post(login_url, data=login_data, headers=headers)

    def is_logged_in(self, soup):
        """Check if ticketsforgood log in was successful."""
        login_btn = soup.select_one("nav a.btn")
        if login_btn:
            return False
        return True



    async def main(self):
        cards_html = await self.fetch_html()
        event_df = self.html_to_dataframe(cards_html)
        return event_df
    
    @staticmethod
    def new_events():
        loop = asyncio.get_event_loop()
        return  loop.run_until_complete(EventParser._fetch_all())
 
    @staticmethod
    async def _fetch_all():
        parser1 = EventParser('bluelighttickets')
        parser2 = EventParser('ticketsforgood')
        parser3 = EventParser('concertsforcarers')
        tasks = []
        for p in [parser1, parser2, parser3]:
            task = asyncio.create_task(p.main())
            tasks.append(task)
        df_array = await asyncio.gather(*tasks)
        event_df = pd.concat(df_array)
        event_df = event_df.reset_index()
        event_df['website_name'] = event_df.website.str.replace(r'https://(www\.)?(nhs.)?', '', regex=True)
        event_df.website_name = event_df.website_name.str.replace(r"\.\w+(\.w+)?", '', regex=True)
        return {'events': event_df, 'tfg_status': EventParser.is_tfg_logged_in}



if __name__ == "__main__":

    
    def run_event_loop(method): 
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(method())
    
    # df = run_event_loop(EventParser._fetch_all)
    df = EventParser.new_events()
    print(df)
    print(EventParser.is_tfg_logged_in)
  
