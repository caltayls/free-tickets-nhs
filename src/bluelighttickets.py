
import requests
import pandas as pd
import asyncio
from bs4 import BeautifulSoup
import re
import time
import aiohttp

async def fetch_html():
   
    async with aiohttp.ClientSession() as session:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        page_url = 'https://bluelighttickets.co.uk/event/all'
        
        async with session.get(page_url, headers=headers) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
    
   


        # Find number of pages to search
        last_page_href = soup.select("a.page-link")[-1]['href']
        last_page_num = int(re.search("all/(\d+)", last_page_href).group(1))


        tasks = []
        sem = asyncio.Semaphore(2)
        for i in range(2):  
            url = rf'https://bluelighttickets.co.uk/event/all/{i+1}'
            task = asyncio.create_task(fetch_event_cards(session, sem, url)) ### semaphore must be within async func or wont work
            tasks.append(task)
        completed_tasks, _ = await asyncio.wait(tasks)  # returns tasks completed and awaiting. ignore latter
        return completed_tasks
            
async def fetch_event_cards(session, sem, url):
    async with session.get(url) as response:
        async with sem:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            event_cards = soup.select("#events .col-lg-4")
            await asyncio.sleep(2) # Avoid overloading server
            print(len(event_cards))
            return event_cards


    

async def html_to_dataframe(cards_html):  
    events_list = []

    for event_card in cards_html:

        event_element_text = event_card.select_one("span").text
        event_name = event_element_text.split('-')[0].strip()
        event_info = event_card.select_one("p").contents
        date, location = [info.strip() for info in event_info if isinstance(info, str)]
        url_ext = event_card.select_one("a.btn-primary")['href']
        
        event_dic = {'name':event_name, 'location': location, 'date': date, 'url': url_ext}
        events_list.append(event_dic)

    df = pd.DataFrame(events_list)
    # df.date = df.date.str.replace('\n', '')
    url_base = r'https://bluelighttickets.co.uk'
    # df['url'] = url_base + df.url 
    df['website'] = 'bluelight_tickets'

    return df



async def main():
    finished_tasks = await fetch_html()
    results = [await result for result in finished_tasks]
    cards_html = [card for sublist in results for card in sublist]
    event_df = await html_to_dataframe(cards_html)
    return event_df



loop = asyncio.get_event_loop()
card_df = loop.run_until_complete(main())

print(card_df)