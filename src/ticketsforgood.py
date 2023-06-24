import pandas as pd
import asyncio
from bs4 import BeautifulSoup
import re
import aiohttp

with open(r"C:\Users\callu\OneDrive\Desktop\ticketsforgood.txt", 'r') as f:
    email = f.readline().strip('\n')
    pw = f.readline().strip('\n')

     
async def login(session, email=email, pw=pw):

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


async def fetch_html():
    async with aiohttp.ClientSession() as session: # create a session so login is cached and cookies are stored
        await login(session)
        page_url = 'https://nhs.ticketsforgood.co.uk'
        async with session.get(page_url) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')

        # Confirm if logged in successfully:
        login_btn = soup.select_one("nav a.btn")
        if login_btn:
            is_logged_in = False
        else:
            is_logged_in = True

        # Find number of pages to search
        last_page_num_el = soup.select("li.page-item a")[-1]['href']
        last_page_num = int(re.search('\d+', last_page_num_el).group())

        # Iterate through pages and collect event_card_html. Pages are scraped concurrently (set to two to reduce traffic)
        tasks = []
        sem = asyncio.Semaphore(2) # Restricts concurrent tasks to 2. i.e. only allows two iterations of loop to happen simultaneously.
        for i in range(last_page_num):
            url = rf'https://nhs.ticketsforgood.co.uk/?page={i+1}'
            task = asyncio.create_task(fetch_event_cards(session, sem, url)) ### semaphore must be within async func or wont work
            tasks.append(task)
        completed_tasks, _ = await asyncio.wait(tasks)  # returns tasks completed and awaiting. ignore latter
        return completed_tasks, is_logged_in


    
async def fetch_event_cards(session, sem, url):
    async with session.get(url) as response:
        async with sem:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            event_cards = soup.select("div[class*='col-xl']")
            await asyncio.sleep(2) # Avoid overloading server
            print(len(event_cards))
            return event_cards
        
    
def html_to_dataframe(cards_html):  
    events_list = []
    url_base = r"https://nhs.ticketsforgood.co.uk/"
    for event in cards_html:
        name = event.select_one("h5[class*='card-title']").string.strip('\n')
        info = [element.string.strip('\n') for element in event.select('div.col')]
        [location, dates, event_type] = info
        url_ext = event.select_one("a[class*='btn']")['href']
        event_dic = {'name': name, 'event_type': event_type, 'location': location, 'dates': dates, 'url': url_ext}
        events_list.append(event_dic)
    df = pd.DataFrame(events_list)
    df.dates = df.dates.str.replace('\n', '')
    df.event_type =  df.event_type.str.replace("^\W+$", 'Not Listed', regex=True)
    df['url'] = url_base + df.url 
    df['website'] = 'tickets_for_good'
    return df






async def main():
    finished_tasks, is_logged_in = await fetch_html()
    results = [await result for result in finished_tasks]
    cards_html = [card for sublist in results for card in sublist]
    event_df = html_to_dataframe(cards_html)
    print(f"Logged in? {is_logged_in}")
    return event_df


loop = asyncio.get_event_loop()
card_df = loop.run_until_complete(main())

print(card_df)