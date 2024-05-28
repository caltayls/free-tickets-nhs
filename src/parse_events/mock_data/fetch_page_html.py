import requests
from bs4 import BeautifulSoup
import json
import os

print(os.getcwd())
def html_json_export(urls, data_dir, file_name):
    
    bluelight_pages_html = {f"page{i}": requests.get(url).text for i, url in enumerate(urls)}

    with open(f'./src/parse_events/mock_data/{data_dir}/{file_name}', 'w') as f:
        json.dump(bluelight_pages_html, f)


## Bluelight
bl_urls = [
    r"https://bluelighttickets.co.uk/event/all",
    r"https://bluelighttickets.co.uk/event/all2"
]

html_json_export(bl_urls, "bluelighttickets", 'page_html.json')

tfg_urls = [
    r'https://nhs.ticketsforgood.co.uk/?page=1',
    r'https://nhs.ticketsforgood.co.uk/?page=2',        
]

html_json_export(tfg_urls, "ticketsforgood", 'page_html.json')

cfc_url = [
    r'https://www.concertsforcarers.org.uk/events'
]

html_json_export(cfc_url, "concertsforcarers", 'page_html.json')

