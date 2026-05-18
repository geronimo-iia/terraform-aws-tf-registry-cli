"""Python logger definition."""

import logging
import os

from rich.console import Console
from rich.logging import RichHandler

__all__ = ["init_root_logger"]


default_log_level = int(os.getenv("LOG_LEVEL", str(logging.INFO)))


def init_root_logger(
    log_level=default_log_level,
    fmt="%(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
):
    """Return a configured root logger."""

    _logger = logging.getLogger()
    _logger.setLevel(log_level)

    logging.getLogger(name="envclasses").setLevel(logging.ERROR)

    handler = RichHandler(console=Console(stderr=True), show_time=True, show_path=True)
    handler.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    _logger.addHandler(handler)

    logging.getLogger("generator").setLevel(logging.NOTSET)

    return _logger
