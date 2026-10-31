import pytest
import pandas as pd
import numpy as np
from cbsl_forecast.data.loader import load_and_preprocess_data
from cbsl_forecast.features.build_features import create_demand_forecasting_features
from cbsl_forecast.models.demand_model import DemandForecaster, train_demand_forecaster
from cbsl_forecast.models.regimes import fit_macro_regimes

@pytest.fixture(scope="module")
def dataset():
    return load_and_preprocess_data()

def test_feature_creation(dataset):
    X, y, features = create_demand_forecasting_features(dataset)
    assert len(X) == len(y)
    assert not X.isnull().values.any()
    assert not y.isnull().values.any()
    assert "demand_diff1" in features
    assert "sin_dow" in features

def test_demand_forecaster_fit_and_predict(dataset):
    forecaster = DemandForecaster(alpha=0.2, random_state=42)
    forecaster.fit(dataset)
    assert forecaster.is_fitted
    
    X, _, _ = create_demand_forecasting_features(dataset)
    sample_X = X.iloc[[0]]
    last_demand = 2000.0
    pred = forecaster.predict_peak_demand(last_demand, sample_X)
    assert isinstance(pred, float)
    assert 1000.0 < pred < 4000.0

def test_functional_train_forecaster(dataset):
    reg, scaler, features = train_demand_forecaster(dataset, alpha=0.2)
    assert hasattr(reg, "coef_")
    assert len(features) == 6

def test_macro_regimes_clustering(dataset):
    kmeans, pca, scaler, df_clustered = fit_macro_regimes(dataset, n_clusters=3, random_state=42)
    assert "cluster_id" in df_clustered.columns
    assert "pca_1" in df_clustered.columns
    assert "pca_2" in df_clustered.columns
    assert set(df_clustered["cluster_id"].unique()) == {0, 1, 2}
