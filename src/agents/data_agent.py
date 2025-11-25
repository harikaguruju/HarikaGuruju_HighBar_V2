import os
import pandas as pd
import numpy as np
from datetime import timedelta
from src.utils.loader import load_csv

class DataAgent:
    """
    Loads, validates, and summarizes the dataset.
    Produces daily + campaign-level summaries used by other agents.
    """

    def __init__(self, cfg):
        self.cfg = cfg
        # Load from environment variable or config.yaml
        self.path = os.environ.get("DATA_CSV", cfg.get("data_csv"))

    def load_and_summarize(self):
        # Load CSV using loader utility
        df = load_csv(self.path)

        # Convert numeric columns safely
        numeric_cols = ["impressions", "clicks", "purchases", "spend", "revenue"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Compute CTR if missing
        if "ctr" not in df.columns:
            df["ctr"] = (
                df["clicks"] / df["impressions"]
            ).replace([np.inf, -np.inf], 0).fillna(0)

        # DAILY SUMMARY
        daily = (
            df.groupby("date")
            .agg(
                impressions=("impressions", "sum"),
                clicks=("clicks", "sum"),
                spend=("spend", "sum"),
                revenue=("revenue", "sum"),
                purchases=("purchases", "sum"),
            )
            .reset_index()
        )

        daily["ctr"] = (
            daily["clicks"] / daily["impressions"]
        ).replace([np.inf, -np.inf], 0).fillna(0)

        daily["roas"] = (
            daily["revenue"] / daily["spend"]
        ).replace([np.inf, -np.inf], 0).fillna(0)

        # CAMPAIGN SUMMARY
        campaign = (
            df.groupby("campaign_name")
            .agg(
                impressions=("impressions", "sum"),
                clicks=("clicks", "sum"),
                spend=("spend", "sum"),
                revenue=("revenue", "sum"),
            )
            .reset_index()
        )

        campaign["ctr"] = (
            campaign["clicks"] / campaign["impressions"]
        ).replace([np.inf, -np.inf], 0).fillna(0)

        campaign["roas"] = (
            campaign["revenue"] / campaign["spend"]
        ).replace([np.inf, -np.inf], 0).fillna(0)

        # DATE RANGE
        date_range = [
            str(df["date"].min().date()),
            str(df["date"].max().date()),
        ]

        # LAST 7 DAYS SUMMARY
        max_date = df["date"].max()
        recent_window = df[df["date"] >= (max_date - timedelta(days=7))]

        recent_summary = recent_window.agg(
            {
                "impressions": "sum",
                "clicks": "sum",
                "spend": "sum",
                "revenue": "sum",
            }
        ).to_dict()

        recent_summary["ctr"] = (
            recent_summary["clicks"] / recent_summary["impressions"]
            if recent_summary["impressions"] > 0
            else 0
        )

        recent_summary["roas"] = (
            recent_summary["revenue"] / recent_summary["spend"]
            if recent_summary["spend"] > 0
            else 0
        )

        # DETECT LOW-CTR CAMPAIGNS
        low_ctr_threshold = self.cfg.get("low_ctr_threshold", 0.01)
        low_ctr_campaigns = campaign[campaign["ctr"] < low_ctr_threshold].to_dict(
            orient="records"
        )

        # FINAL SUMMARY DICTIONARY (returned to Planner → other agents)
        summary = {
            "n_rows": len(df),
            "date_range": date_range,
            "daily": daily.to_dict(orient="records"),
            "campaign": campaign.to_dict(orient="records"),
            "recent_summary": recent_summary,
            "low_ctr_campaigns": low_ctr_campaigns,
        }

        return summary
