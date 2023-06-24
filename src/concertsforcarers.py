
import requests
import pandas as pd
import asyncio
from bs4 import BeautifulSoup
import re
import aiohttp

async def fetch_html():
    async with aiohttp.ClientSession() as session: # create a session so login is cached and cookies are stored

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        # All events are on one page 
        url = r'https://www.concertsforcarers.org.uk/events/'
        async with session.get(url, headers=headers) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
        event_cards = soup.select("li.event")
        events_html_lst = event_cards

        return events_html_lst

async def html_to_dataframe(cards_html):
    html_list = await fetch_html()
    events_list = []
    for event_card in html_list:
        details = event_card.select('span')[:5]
        details_text = [element.text for element in details]
        event_name1, event_name2, location, _, date  = details_text
        event_name = f"{event_name1} - {event_name2}"
        url_ext = event_card.select_one("a.button")['href']
        event_dic = {'name':event_name, 'location': location, 'date': date, 'url': url_ext}
        events_list.append(event_dic)
    event_df = pd.DataFrame(events_list)
    # df.date = df.date.str.replace('\n', '')
    url_base = r'https://www.concertsforcarers.org.uk'
    event_df['url'] = url_base + event_df.url 
    event_df['website'] = 'concerts_for_carers'

    return event_df



async def main():
    cards_html = await fetch_html()
    event_df = await html_to_dataframe(cards_html)
    return event_df



loop = asyncio.get_event_loop()
card_df = loop.run_until_complete(main())

print(card_df)