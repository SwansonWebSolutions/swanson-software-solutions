import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from django.conf import settings


def get_script_logger(
    script_name: str,
    *,
    level: int = logging.INFO,
    when: str = "midnight",
    backup_count: int = 14,
    console: bool = True,
) -> logging.Logger:
    """Return a configured logger for an email_service script.

    Writes logs to `<BASE_DIR>/logs/<script_name>/<script_name>.log` and
    rotates them daily, keeping a limited history. Handlers are attached only
    once per process.
    """
    base_dir = Path(getattr(settings, "BASE_DIR", "."))
    logs_root = base_dir / "logs" / script_name
    logs_root.mkdir(parents=True, exist_ok=True)

    logfile = logs_root / f"{script_name}.log"

    logger_name = f"email_service.{script_name}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False

    # Common formatter for file/console
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Attach a single TimedRotatingFileHandler (if not already attached)
    if not any(
        isinstance(h, TimedRotatingFileHandler)
        and getattr(h, "baseFilename", None) == str(logfile)
        for h in logger.handlers
    ):
        file_handler = TimedRotatingFileHandler(
            filename=str(logfile),
            when=when,
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
            utc=False,
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    # Optional console handler for interactive runs
    if console and not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(level)
        logger.addHandler(sh)

    return logger

