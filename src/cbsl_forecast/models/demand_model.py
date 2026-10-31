from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso
from sklearn.preprocessing import StandardScaler
from cbsl_forecast.features.build_features import create_demand_forecasting_features

class DemandForecaster:
    """Day-ahead peak electricity demand forecaster using regularized linear modeling."""

    def __init__(self, alpha: float = 0.2, random_state: int = 42):
        self.alpha = alpha
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = Lasso(alpha=self.alpha, random_state=self.random_state)
        self.feature_names = []
        self.is_fitted = False

    def fit(self, df: pd.DataFrame) -> "DemandForecaster":
        X, y, features = create_demand_forecasting_features(df)
        self.feature_names = features
        X_sc = self.scaler.fit_transform(X)
        self.model.fit(X_sc, y)
        self.is_fitted = True
        return self

    def predict_delta(self, X_input: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted. Call fit() first.")
        X_sc = self.scaler.transform(X_input[self.feature_names])
        return self.model.predict(X_sc)

    def predict_peak_demand(self, last_demand: float, X_input: pd.DataFrame) -> float:
        delta = self.predict_delta(X_input)[0]
        return float(last_demand + delta)

def train_demand_forecaster(df: pd.DataFrame, alpha: float = 0.2) -> Tuple[Lasso, StandardScaler, list]:
    """Functional interface matching app.py training pipeline."""
    X, y, features = create_demand_forecasting_features(df)
    scaler = StandardScaler()
    X_sc = scaler.fit_transform(X)
    reg = Lasso(alpha=alpha, random_state=42)
    reg.fit(X_sc, y)
    return reg, scaler, features
