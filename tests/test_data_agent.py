import pandas as pd
import pytest

from src.agents.data_agent import DataAgent


def test_data_agent_summary_basic_metrics(tmp_path):
    """
    DataAgent should correctly aggregate totals and compute CTR & ROAS.
    """
    csv_path = tmp_path / "sample_fb_ads.csv"

    df = pd.DataFrame(
        {
            "date": ["2025-01-01", "2025-01-02"],
            "campaign_name": ["A", "B"],
            "spend": [10.0, 20.0],
            "impressions": [100, 200],
            "clicks": [5, 15],
            "revenue": [50.0, 60.0],
        }
    )
    df.to_csv(csv_path, index=False)

    cfg = {"data_csv": str(csv_path)}

    agent = DataAgent(cfg=cfg)
    summary = agent.load_and_summarize()

    totals = summary["totals"]
    overall = summary["overall"]

    # totals
    assert totals["spend"] == pytest.approx(30.0)
    assert totals["revenue"] == pytest.approx(110.0)
    assert totals["clicks"] == 20
    assert totals["impressions"] == 300

    # CTR = clicks / impressions
    expected_ctr = 20 / 300
    assert overall["ctr"] == pytest.approx(expected_ctr)

    # ROAS = revenue / spend
    expected_roas = 110.0 / 30.0
    assert overall["roas"] == pytest.approx(expected_roas)
