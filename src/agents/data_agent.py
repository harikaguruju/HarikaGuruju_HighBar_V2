from dataclasses import dataclass
import logging
from typing import Any, Dict

import numpy as np
import pandas as pd

from src.utils.loader import load_csv, EXPECTED_COLUMNS

logger = logging.getLogger(__name__)


@dataclass
class DataAgent:
    """
    DataAgent is responsible for:
    - loading the Facebook Ads dataset
    - doing basic cleaning / safety checks
    - producing aggregate stats that downstream agents use
    """

    config: Dict[str, Any]

    def _load_raw(self) -> pd.DataFrame:
        path = self.config["data_csv"]
        logger.info("DataAgent: loading dataset from %s", path)

        df = load_csv(path, expected_columns=EXPECTED_COLUMNS)

        # Basic cleaning: replace NaNs in numeric columns to avoid NaN propagation.
        numeric_cols = [col for col in df.columns if df[col].dtype.kind in "if"]
        if numeric_cols:
            df[numeric_cols] = df[numeric_cols].replace([np.inf, -np.inf], np.nan)
            df[numeric_cols] = df[numeric_cols].fillna(0.0)

        if df.empty:
            logger.error("DataAgent: dataset is empty after cleaning")
            raise ValueError("Dataset is empty after cleaning")

        logger.info(
            "DataAgent: dataset loaded with %d rows and %d columns",
            df.shape[0],
            df.shape[1],
        )
        return df

    def load_and_summarize(self) -> Dict[str, Any]:
        """
        Load data and return a compact summary used by other agents.

        Returns:
            Dictionary with totals + basic KPIs.
        """
        df = self._load_raw()

        total_spend = float(df["spend"].sum())
        total_impressions = float(df["impressions"].sum())
        total_clicks = float(df["clicks"].sum())
        total_revenue = float(df["revenue"].sum())

        ctr = (total_clicks / total_impressions) if total_impressions > 0 else 0.0
        roas = (total_revenue / total_spend) if total_spend > 0 else 0.0

        summary = {
            "rows": int(df.shape[0]),
            "cols": int(df.shape[1]),
            "total_spend": total_spend,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_revenue": total_revenue,
            "overall_ctr": ctr,
            "overall_roas": roas,
        }

        logger.info(
            "DataAgent summary created: spend=%.2f, revenue=%.2f, clicks=%d, "
            "impressions=%d, CTR=%.4f, ROAS=%.2f",
            total_spend,
            total_revenue,
            int(total_clicks),
            int(total_impressions),
            ctr,
            roas,
        )

        return summary
