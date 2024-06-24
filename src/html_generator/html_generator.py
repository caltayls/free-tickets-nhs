from jinja2 import Environment, FileSystemLoader
import os


def render_html(new_events, tfg_status):
    pwd = os.getcwd()
    env = Environment(loader=FileSystemLoader(pwd))
    template_path = r"/src/html_templates/new_events_email_template/jinja_template.html"
    template = env.get_template(template_path)
    obj_array = new_events.to_dict(orient='records')
   
    data = {
        'tfg_status': tfg_status,
        'events': obj_array,
        'columns': ['event_name', 'location', 'date', 'website'],
        'count': len(obj_array),
    }
    output = template.render(data)

    return output
