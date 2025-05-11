from pathlib import Path

from fastapi.templating import Jinja2Templates

templates_dir = Path("../templates")
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)