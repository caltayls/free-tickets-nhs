from jinja2 import Environment, FileSystemLoader
import os


def render_html(event_df, template_path):
    pwd = os.getcwd()
    env = Environment(loader=FileSystemLoader(pwd))
    template = env.get_template(template_path)
    obj_array = event_df.to_dict(orient='records')
    data = {
        'events': obj_array,
        'columns': ['event_name', 'location', 'date', 'website'],
        'count': len(obj_array),
    }
    output = template.render(data)

    return output
