import logging

from src.core.settings import get_settings

settings = get_settings()

LOGGER_FORMAT = logging.Formatter(
    fmt="{asctime} | {levelname} | {name} | {requested_by} | {message}",
    datefmt="%d/%m/%y %H:%M:%S",
    style="{",  # Enables f-string syntax.
)


class NameFilter(logging.Filter):
    def filter(self, record):
        if record.name == "uvicorn.error":
            record.name = "fastapi"
        if record.name == "uvicorn.access":
            record.name = "fastapi"
        return True


def init_logging() -> logging.Logger:
    """Init simple console logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    root_log = logging.getLogger()
    root_log.setLevel(log_level)

    if root_log.hasHandlers():
        root_log.handlers.clear()

    handle_console = logging.StreamHandler()
    handle_console.setLevel(logging.DEBUG)
    handle_console.setFormatter(LOGGER_FORMAT)

    process_name_filter = NameFilter()
    handle_console.addFilter(process_name_filter)

    root_log.addHandler(handle_console)

    for log_name in ("websockets", "uvicorn"):
        logging.getLogger(log_name).setLevel(logging.INFO)

    return root_log
