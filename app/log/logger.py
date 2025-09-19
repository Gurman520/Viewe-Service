from .AppLogger import AppLogger

logger = AppLogger(
    name="Markdown Viewer",
    log_file="app.log",
    json_format=False
)