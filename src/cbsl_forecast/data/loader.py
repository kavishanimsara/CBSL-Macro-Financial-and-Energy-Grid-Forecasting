from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from cbsl_forecast.config import get_project_root, load_config

def find_data_file(custom_path: Optional[str] = None) -> Path:
    """Resolve data file path checking custom, config, processed, and root paths."""
    root = get_project_root()
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            return p
        if (root / custom_path).exists():
            return root / custom_path

    cfg = load_config()
    proc_path = root / cfg.get("data", {}).get("processed_csv_path", "data/processed/cbsl_daily_economic_indicators_2020_2026_preprocesd.csv")
    if proc_path.exists():
        return proc_path

    root_csv = root / cfg.get("data", {}).get("fallback_csv_path", "cbsl_daily_economic_indicators_2020_2026_preprocesd.csv")
    if root_csv.exists():
        return root_csv

    # Default fallback to root csv
    return root / "cbsl_daily_economic_indicators_2020_2026_preprocesd.csv"

def generate_synthetic_data() -> pd.DataFrame:
    """Generate calibrated synthetic dataset in case real data is unavailable."""
    dates = pd.date_range(start="2020-01-01", end="2026-08-10", freq="B")
    np.random.seed(42)
    n = len(dates)

    usd_rate = np.linspace(185, 310, n) + np.sin(np.linspace(0, 10, n)) * 15 + np.random.normal(0, 2, n)
    peak_demand = 2200 + np.sin(np.linspace(0, 30, n)) * 300 + np.random.normal(0, 40, n)
    total_energy = peak_demand * 0.019 + np.random.normal(0, 1, n)

    df = pd.DataFrame({
        "report_date": dates,
        "usd_tt_selling": usd_rate,
        "usd_tt_buying": usd_rate * 0.98,
        "indicative_usd_spot": usd_rate * 0.99,
        "peak_demand": peak_demand,
        "total_energy": total_energy,
        "hydro_pct": np.clip(40 + np.sin(np.linspace(0, 20, n)) * 20, 10, 75),
        "thermal_coal_pct": np.clip(35 + np.cos(np.linspace(0, 20, n)) * 10, 10, 60),
        "thermal_oil_pct": np.clip(15 + np.sin(np.linspace(0, 10, n)) * 8, 5, 40),
        "wind_pct": np.clip(10 + np.random.normal(0, 2, n), 2, 20),
        "real_gdp_growth": np.random.uniform(-2, 4, n),
        "ncpi_yoy": np.random.uniform(5, 50, n),
        "ccpi_yoy": np.random.uniform(4, 45, n)
    })
    return df

def load_and_preprocess_data(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load CBSL daily economic indicators and calculate temporal & normalized generation features.
    """
    target_path = find_data_file(custom_path=csv_path)
    if target_path.exists():
        df = pd.read_csv(target_path)
        df['report_date'] = pd.to_datetime(df['report_date'])
        df = df.sort_values('report_date').reset_index(drop=True)
    else:
        df = generate_synthetic_data()

    energy_cols = ["thermal_coal_pct", "thermal_oil_pct", "hydro_pct", "wind_pct"]
    for c in energy_cols:
        if c not in df.columns:
            df[c] = 0.0

    df[energy_cols] = df[energy_cols].clip(lower=0.0)
    e_sum = df[energy_cols].sum(axis=1)
    for c in energy_cols:
        df[c] = np.where(e_sum > 0, (df[c] / e_sum) * 100.0, df[c])

    df["year"] = df["report_date"].dt.year
    df["month"] = df["report_date"].dt.month
    df["month_name"] = df["report_date"].dt.strftime("%B")
    df["quarter"] = df["report_date"].dt.to_period("Q").astype(str)
    df["day_name"] = df["report_date"].dt.day_name()
    df["is_weekend"] = df["report_date"].dt.dayofweek >= 5

    return df
