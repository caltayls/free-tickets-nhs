import pandas as pd
import asyncio
from src.parse_events.parse_events import EventParser 
from src.aws_utils.utils import AWS_tools

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
# results = run_event_loop(completed_tasks)
# print(results)
results = run_new_event_loop(sendit)
combined = pd.concat(results)
combined = combined.reset_index()
print(combined)
combined.to_json("./src/html_templates/new_events.json", orient='table', index=False)
# aws_tools = AWS_tools()

    