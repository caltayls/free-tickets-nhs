import pandas as pd
import asyncio
from src.parse_events.parse_events import EventParser 
from jinja2 import Environment, FileSystemLoader
# from src.aws_utils.utils import AWS_tools
import os
print(os.getcwd())

def run_new_event_loop(method): 
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(method())


    
async def sendit():
    parser1 = EventParser('bluelighttickets')
    parser2 = EventParser('ticketsforgood')
    parser3 = EventParser('concertsforcarers')
    tasks = []
    for p in [parser1, parser2, parser3]:
        task = asyncio.create_task(p.main())
        tasks.append(task)
    completed_tasks = await asyncio.gather(*tasks)
    return completed_tasks

results = run_new_event_loop(sendit)
event_df = pd.concat(results)
event_df = event_df.reset_index()


obj_array = event_df.to_dict(orient='records')



env = Environment(loader=FileSystemLoader(r'C:\Users\callu\OneDrive\Documents\coding\webscrape\ticket_checker_app\ticket_checker_app\src\app'))
template = env.get_template(r'jinja_template.html')

data = {
     'events': obj_array,
     'columns': ['event_name', 'location', 'date'],
     'count': len(obj_array),
}
output = template.render(data)


print(data['count'])
with open(r"./email.html", 'w', encoding='utf-8') as f:
     f.write(output)
