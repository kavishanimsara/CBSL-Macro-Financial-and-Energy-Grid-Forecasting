import numpy as np
import pandas as pd
from typing import Tuple, List

FEATURE_COLUMNS = ["demand_diff1", "demand_diff7", "energy_lag1", "hydro_lag1", "sin_dow", "cos_dow"]

def create_demand_forecasting_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Construct autoregressive lag features, day-of-week cyclic encodings, and delta target for peak demand.
    
    Returns:
        X (DataFrame): Feature matrix with valid non-null rows
        y (Series): Delta change target (peak_demand - demand_lag1)
        feature_names (List[str]): List of predictor column names
    """
    df_t2 = df[["report_date", "peak_demand", "total_energy", "hydro_pct", "thermal_coal_pct"]].dropna().copy().reset_index(drop=True)
    df_t2["demand_lag1"] = df_t2["peak_demand"].shift(1)
    df_t2["demand_lag2"] = df_t2["peak_demand"].shift(2)
    df_t2["demand_lag7"] = df_t2["peak_demand"].shift(7)
    df_t2["energy_lag1"] = df_t2["total_energy"].shift(1)
    df_t2["hydro_lag1"]  = df_t2["hydro_pct"].shift(1)

    df_t2["demand_delta_target"] = df_t2["peak_demand"] - df_t2["demand_lag1"]
    df_t2["demand_diff1"] = df_t2["demand_lag1"] - df_t2["demand_lag2"]
    df_t2["demand_diff7"] = df_t2["demand_lag1"] - df_t2["demand_lag7"]
    df_t2["sin_dow"] = np.sin(2 * np.pi * df_t2["report_date"].dt.dayofweek / 5.0)
    df_t2["cos_dow"] = np.cos(2 * np.pi * df_t2["report_date"].dt.dayofweek / 5.0)

    df_t2_clean = df_t2.dropna().reset_index(drop=True)
    X = df_t2_clean[FEATURE_COLUMNS]
    y = df_t2_clean["demand_delta_target"]

    return X, y, FEATURE_COLUMNS
