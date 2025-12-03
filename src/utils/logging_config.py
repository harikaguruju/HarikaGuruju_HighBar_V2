import logging
from pathlib import Path
from datetime import datetime


def setup_logging() -> Path:
    """
    Configure logging to write both to console and to a timestamped log file.

    Returns
    -------
    Path
        Path to the log file created for this run.
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = logs_dir / f"run_{timestamp}.log"

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Root logger config
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()  # avoid duplicate logs
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Silence very noisy libraries if needed
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    return log_path
