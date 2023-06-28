from src.parse_events.parse_events import EventParser 
from src.html_generator.html_generator import render_html
from src.aws_utils.utils import AWS_tools, compare_previous_search, update_event_history


def find_events():
    # fetches and parses new events from 3 websites
    event_dic = EventParser.new_events() 
    all_events_df = event_dic['events']
    tfg_status = event_dic['tfg_status']

    # Compares new search to the previous
    aws_tools_instance = AWS_tools()
    new_events_df = compare_previous_search(all_events_df, aws_tools_instance)

    # concat columns to form link then render new events html
    new_events_df['url'] = new_events_df.website + new_events_df.url
    print(new_events_df['url'])
    html = render_html(new_events_df, tfg_status, r"/src/html_templates/new_events_email_template/jinja_template.html")

    # Email new events 
    aws_tools_instance.send_email(
        address_list=['callumtaylor955@gmail.com'], 
        source_email_address='callumtaylor955@gmail.com', 
        html=html
    )

    # Update active events csv
    aws_tools_instance.df_to_bucket(all_events_df, "active_events.csv", "nhs-free-events")

    # Update event history csv
    update_event_history(new_events_df, aws_tools_instance)

