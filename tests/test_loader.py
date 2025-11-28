import pandas as pd
import pytest

from src.utils.loader import load_csv, DataLoaderError


def _make_minimal_df():
    """Helper to build a minimal valid dataframe for our loader tests."""
    return pd.DataFrame(
        {
            "date": ["2025-01-01"],
            "campaign_name": ["Test Campaign"],
            "spend": [10.0],
            "impressions": [100],
            "clicks": [5],
            "revenue": [50.0],
        }
    )


def test_load_csv_success(tmp_path):
    """CSV loads correctly and returns expected columns."""
    csv_path = tmp_path / "sample.csv"
    df_in = _make_minimal_df()
    df_in.to_csv(csv_path, index=False)

    df_out = load_csv(
        str(csv_path),
        required_columns=df_in.columns,
    )

    assert len(df_out) == 1
    assert set(df_in.columns).issubset(df_out.columns)


def test_load_csv_missing_required_column_raises(tmp_path):
    """If a required column is missing, DataLoaderError is raised."""
    csv_path = tmp_path / "sample_missing_col.csv"
    df_in = _make_minimal_df()
    # drop a column to simulate schema drift
    df_in = df_in.drop(columns=["revenue"])
    df_in.to_csv(csv_path, index=False)

    with pytest.raises(DataLoaderError):
        load_csv(
            str(csv_path),
            required_columns=[
                "date",
                "campaign_name",
                "spend",
                "impressions",
                "clicks",
                "revenue",  # this one is missing -> should raise
            ],
        )
