import logging
import time
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataLoaderError(Exception):
    """Raised when the CSV is missing required columns or cannot be loaded properly."""


def load_csv(
    path: str,
    *,
    retries: int = 3,
    delay_seconds: float = 1.0,
    required_columns: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Robust CSV loader with:
      - logging
      - basic retry logic
      - optional schema validation

    Parameters
    ----------
    path : str
        Path to the CSV file.
    retries : int
        Number of times to retry on failure.
    delay_seconds : float
        Delay between retries.
    required_columns : Iterable[str] | None
        If provided, ensures these columns exist in the CSV.

    Returns
    -------
    pd.DataFrame
    """
    csv_path = Path(path)
    attempt = 1

    while True:
        try:
            if not csv_path.exists():
                raise FileNotFoundError(csv_path)

            logger.info("Loading CSV from %s (attempt %d)", csv_path, attempt)

            df = pd.read_csv(
                csv_path,
                parse_dates=["date"],
                infer_datetime_format=True,
            )

            logger.info("CSV loaded successfully: %d rows x %d columns", len(df), df.shape[1])

            # basic schema check
            if required_columns:
                missing = [c for c in required_columns if c not in df.columns]
                if missing:
                    raise DataLoaderError(f"Missing required columns in dataset: {missing}")

            return df

        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to load CSV on attempt %d: %s", attempt, exc)

            if attempt >= retries:
                logger.error("Giving up after %d attempts. Last error: %s", attempt, exc)
                # raise the last error so caller can see what went wrong
                raise

            attempt += 1
            time.sleep(delay_seconds)
