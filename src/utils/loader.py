import logging
import time
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class DataLoaderError(Exception):
    """Raised when the CSV cannot be loaded or fails validation."""


# Default schema we expect in the dataset
REQUIRED_COLUMNS_DEFAULT = [
    "date",
    "campaign_name",
    "impressions",
    "clicks",
    "spend",
    "revenue",
]


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
      - retry logic
      - schema validation
      - basic cleaning of bad rows

    Parameters
    ----------
    path : str
        Path to the CSV file.
    retries : int
        Max number of attempts to load.
    delay_seconds : float
        Delay between retries.
    required_columns : Iterable[str] | None
        If provided, overrides the default REQUIRED_COLUMNS_DEFAULT.

    Returns
    -------
    pd.DataFrame
    """
    csv_path = Path(path)
    attempt = 1

    # decide which columns to validate
    cols_to_check = list(required_columns) if required_columns else REQUIRED_COLUMNS_DEFAULT

    while True:
        try:
            if not csv_path.exists():
                msg = f"CSV file not found at: {csv_path}"
                logger.error(msg)
                raise DataLoaderError(msg)

            logger.info("Loading CSV from %s (attempt %d)", csv_path, attempt)

            df = pd.read_csv(
                csv_path,
                parse_dates=["date"],
            )

            logger.info("Raw CSV loaded: %d rows x %d columns", len(df), df.shape[1])

            # schema validation
            missing = [c for c in cols_to_check if c not in df.columns]
            if missing:
                msg = f"Missing required columns in dataset: {missing}"
                logger.error(msg)
                raise DataLoaderError(msg)

            # basic cleaning: drop rows with NA in critical columns
            before_rows = len(df)
            df = df.dropna(subset=["date", "impressions", "clicks", "spend", "revenue"])
            after_dropna = len(df)

            if after_dropna < before_rows:
                logger.warning(
                    "Dropped %d rows with missing critical values",
                    before_rows - after_dropna,
                )

            # filter out non-positive impressions
            before_impr = len(df)
            df = df[df["impressions"] > 0]
            after_impr = len(df)

            if after_impr < before_impr:
                logger.warning(
                    "Filtered out %d rows with non-positive impressions",
                    before_impr - after_impr,
                )

            logger.info(
                "Final cleaned dataframe: %d rows x %d columns",
                len(df),
                df.shape[1],
            )

            return df

        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to load/validate CSV on attempt %d: %s",
                attempt,
                exc,
            )

            if attempt >= retries:
                logger.error(
                    "Giving up after %d attempts to load %s. Last error: %s",
                    attempt,
                    csv_path,
                    exc,
                )
                # re-raise as DataLoaderError if not already
                if isinstance(exc, DataLoaderError):
                    raise
                raise DataLoaderError(str(exc)) from exc

            attempt += 1
            time.sleep(delay_seconds)
