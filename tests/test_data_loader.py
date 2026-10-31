import pytest
import pandas as pd
import numpy as np
from cbsl_forecast.data.loader import load_and_preprocess_data, find_data_file

def test_find_data_file_exists():
    path = find_data_file()
    assert path.exists(), f"Data file does not exist at {path}"

def test_load_and_preprocess_data_shape():
    df = load_and_preprocess_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 100, f"Expected more than 100 rows, got {len(df)}"

def test_temporal_columns_exist():
    df = load_and_preprocess_data()
    required_temporal = ["report_date", "year", "month", "month_name", "quarter", "day_name", "is_weekend"]
    for col in required_temporal:
        assert col in df.columns, f"Missing temporal column: {col}"

def test_energy_shares_sum_to_approx_100():
    df = load_and_preprocess_data()
    energy_cols = ["thermal_coal_pct", "thermal_oil_pct", "hydro_pct", "wind_pct"]
    for c in energy_cols:
        assert c in df.columns
    total_shares = df[energy_cols].sum(axis=1)
    # Check that rows with energy generation sum approximately to 100%
    active_rows = total_shares[total_shares > 0]
    np.testing.assert_allclose(active_rows, 100.0, atol=1e-2)
