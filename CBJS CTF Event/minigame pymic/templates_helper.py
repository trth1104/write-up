from jinja2 import Environment, FileSystemLoader
from pathlib import Path

template_dir = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(str(template_dir)))

def render_template(template_name: str, context: dict):
    template = env.get_template(template_name)
    return template.render(**context)

