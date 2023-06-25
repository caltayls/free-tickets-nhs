import pandas as pd
import asyncio
from bs4 import BeautifulSoup
import re
import aiohttp
import json


with open(r"C:\Users\callu\OneDrive\Desktop\ticketsforgood.txt", 'r') as f:
    email = f.readline().strip('\n')
    pw = f.readline().strip('\n')

  
class EventParser:

    def __init__(self, website):
        self.website = website

        with open("./src/app/site_info.json", "r") as file:
            info_all_sites = json.load(file)
        self.site_info = info_all_sites[self.website]

    async def fetch_html(self):
        html_obj = {
            'html': None,
            'logged_in': False
        }

        async with aiohttp.ClientSession() as session: # create a session so login is cached and cookies are stored
            await self.login(session)
            page_url =  self.site_info['URL_BASE'] + self.site_info['FIRST_PAGE_REL_PATH']
            async with session.get(page_url) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
            
            login_success = self.is_logged_in(soup)
            
            # Find number of pages to search
            if not re.search('concertsforcarers', self.site_info['URL_BASE']):
                last_page_num_el = soup.select(self.site_info['LAST_PAGE_ELEMENT_SEL'])[-1]['href']
                last_page_num = int(re.search(self.site_info['LAST_PAGE_TEXT_PAT'], last_page_num_el).group(1))
            else:
                last_page_num = 1
            # Iterate through pages and collect event_card_html. Pages are scraped concurrently (set to two to reduce traffic)
            tasks = []
            sem = asyncio.Semaphore(2) # Restricts concurrent tasks to 2. i.e. only allows two iterations of loop to happen simultaneously.
            # for i in range(last_page_num):
            for i in range(1): ##############change
                page_ext = self.site_info['PAGE_QUERY_REL_PATH']
                if self.website != 'concertsforcarers':
                    page_ext += str(i+1)
                url = self.site_info['URL_BASE'] + page_ext
                task = asyncio.create_task(self.parse_event_cards(session, sem, url)) ### semaphore must be within async func or wont work
                tasks.append(task)
            completed_tasks, _ = await asyncio.wait(tasks)  # returns tasks completed and awaiting. ignore latter
            html_obj.update({'html': completed_tasks, 'logged_on': login_success})
            
            return html_obj

        
        
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
            event_name = f"{event_name1} - {event_name2}" # Event name is arranged awkwardly so needs combined
            url_ext = event_card.select_one("a.button")['href']
            event_dic = {'event_name':event_name, 'location': location, 'date': date, 'url': url_ext}
            return event_dic
        
        elif self.website == 'bluelighttickets':
            event_element_text = event_card.select_one("span").text
            event_name = event_element_text.split('-')[0].strip()
            event_info = event_card.select_one("p").contents
            date, location = [info.strip() for info in event_info if isinstance(info, str)]
            url_ext = event_card.select_one("a.btn-primary")['href']
            event_dic = {'event_name':event_name, 'location': location, 'date': date, 'url': url_ext}
            return event_dic



    
    async def login(self, session, email=email, pw=pw):
            # Get the authenticity token from the login page
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
        html_dict = await self.fetch_html()
        finished_tasks = html_dict['html']
        results = [await result for result in finished_tasks]
        cards_html = [card for sublist in results for card in sublist]
        event_df = self.html_to_dataframe(cards_html)
        if self.website == 'ticketsforgood':
            is_logged_in = html_dict['logged_on']
            print(f"Logged in? {is_logged_in}")
        return event_df


if __name__ == "__main__":


    loop = asyncio.get_event_loop()
    card_df = loop.run_until_complete(EventParser('concertsforcarers').main())

    print(card_df)
