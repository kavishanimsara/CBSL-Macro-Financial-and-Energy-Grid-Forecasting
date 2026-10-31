from pathlib import Path
import yaml
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "data": {
        "raw_pdf_dir": "raw_pdfs",
        "processed_csv_path": "data/processed/cbsl_daily_economic_indicators_2020_2026_preprocesd.csv",
        "fallback_csv_path": "cbsl_daily_economic_indicators_2020_2026_preprocesd.csv",
        "date_column": "report_date"
    },
    "columns": {
        "energy_generation": ["hydro_pct", "thermal_coal_pct", "thermal_oil_pct", "wind_pct"]
    },
    "models": {
        "demand_forecasting": {
            "alpha": 0.2,
            "random_state": 42,
            "feature_columns": ["demand_diff1", "demand_diff7", "energy_lag1", "hydro_lag1", "sin_dow", "cos_dow"]
        },
        "regime_clustering": {
            "n_clusters": 3,
            "random_state": 42,
            "n_init": 10,
            "pca_components": 2,
            "features": ["usd_tt_selling", "peak_demand", "total_energy", "hydro_pct", "thermal_coal_pct"]
        }
    }
}

def get_project_root() -> Path:
    """Return repository root path."""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "config" / "config.yaml").exists() or (parent / "cbsl_daily_economic_indicators_2020_2026_preprocesd.csv").exists():
            return parent
    return Path.cwd()

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml with fallback to defaults."""
    root = get_project_root()
    cfg_path = root / "config" / "config.yaml"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data:
                return data
    return DEFAULT_CONFIG
