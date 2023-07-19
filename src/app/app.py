from src.parse_events.parse_events import EventParser 
from src.html_generator.html_generator import render_html
from src.aws_utils.utils import AWS_tools, get_active_events_dataset, events_to_email, add_end_date_to_df, update_active_events
import pandas as pd

def find_events():
    # fetches and parses new events from 3 websites
    event_dic = EventParser.new_events() 
    all_events_df = event_dic['events']
    all_events_df = add_end_date_to_df(all_events_df)
    tfg_status = event_dic['tfg_status']

    # Compares new search to the previous
    aws_tools_instance = AWS_tools()
    active_events_df = get_active_events_dataset(aws_tools_instance)
    new_events_df = events_to_email(all_events_df, active_events_df, aws_tools_instance)
    update_active_events(active_events_df, new_events_df, aws_tools_instance)
    # concat columns to form link then render new events html
    new_events_df['url'] = new_events_df.website + new_events_df.url
    html = render_html(new_events_df, tfg_status, r"/src/html_templates/new_events_email_template/jinja_template.html")


    # Email new events 
    aws_tools_instance.send_email(
        address_list=['callumtaylor955@gmail.com', 'tomebbatson@live.co.uk'], 
        source_email_address='callumtaylor955@gmail.com', 
        html=html
    )


if __name__ == '__main__':
    # fetches and parses new events from 3 websites
    # event_dic = EventParser.new_events() 
    all_events_df = pd.read_csv('data/test_all_events.csv')

    # all_events_df.to_csv('data/test_all_events.csv')
    tfg_status = True

    # Compares new search to the previous
    aws_tools_instance = AWS_tools()
    active_events_df = pd.read_csv('data/active_events_test.csv')

    new_events_df = events_to_email(all_events_df, active_events_df)
    new_events_df
    # update_active_events(active_events_df, new_events_df, aws_tools_instance)
    # concat columns to form link then render new events html
    new_events_df['url'] = new_events_df.website + new_events_df.url
    html = render_html(new_events_df, tfg_status, r"/src/html_templates/new_events_email_template/jinja_template.html")


    # Email new events 
    aws_tools_instance.send_email(
        address_list=['callumtaylor955@gmail.com', ], 
        source_email_address='callumtaylor955@gmail.com', 
        html=html
    )
