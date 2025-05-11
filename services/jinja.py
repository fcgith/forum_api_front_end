from pathlib import Path
from fastapi.templating import Jinja2Templates

templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=templates_dir)