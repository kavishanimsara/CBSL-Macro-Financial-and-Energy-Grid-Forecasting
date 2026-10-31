# CBSL Macro-Financial and Energy Grid Forecasting
### An Integrated Multi-Track Analytical & Predictive Framework

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-brightgreen.svg)](tests/)

---

## 📌 Executive Summary

This repository houses the end-to-end data science capstone project examining the intersection between macroeconomic indicators published by the **Central Bank of Sri Lanka (CBSL)** and national electricity grid dispatch metrics published by the **Ceylon Electricity Board (CEB)** across the 2020–2026 economic crisis, adjustment, and recovery periods.

The framework provides:
1. **Automated Daily Ingestion & Preprocessing**: Extraction and standardization of over 1,400+ daily indicator bulletins into an integrated analytical cohort.
2. **Day-Ahead Peak Electricity Demand Forecasting**: Regularized predictive modeling incorporating autoregressive demand differences, fuel mix lags, and cyclic temporal dynamics.
3. **Macroeconomic & Energy Regime Clustering**: Unsupervised machine learning (PCA + K-Means) mapping the structural transition across Crisis, Stabilization, and Growth regimes.
4. **Interactive Executive Telemetry Dashboard**: A Streamlit application equipped with interactive scenario simulators, fuel mix breakdowns, and time-horizon navigation.

---

## 📁 Repository Structure

```plaintext
CBSL Macro-Financial and Energy Grid Forecasting/
│
├── config/                                       # Project configuration
│   └── config.yaml                               # Data paths, feature sets, model hyper-parameters
│
├── data/                                         # Structured data stages
│   ├── raw/                                      # Reference to raw PDF archives
│   ├── interim/                                  # Intermediate parsed extracts
│   └── processed/                                # Cleaned & normalized modeling datasets
│       └── cbsl_daily_economic_indicators_2020_2026_preprocesd.csv
│
├── docs/                                         # Architecture, diagrams, and reports
│   ├── architecture.md                           # System technical specification
│   └── figures/                                  # System methodology & use-case diagrams
│       ├── methodology_diagram.svg
│       └── use_case_diagram.svg
│
├── raw_pdfs/                                     # 1,400+ CBSL Daily Indicator PDF Bulletins (2020–2026)
│   ├── 2020/ ... 2026/
│
├── src/                                          # Core modular Python package
│   └── cbsl_forecast/
│       ├── config.py                             # Configuration loader
│       ├── data/                                 # Ingestion & preprocessing routines
│       │   └── loader.py
│       ├── features/                             # Lag creation & cyclical time encodings
│       │   └── build_features.py
│       ├── models/                               # Forecasting & unsupervised clustering
│       │   ├── demand_model.py
│       │   └── regimes.py
│       └── utils/                                # Unified Plotly presentation styling
│           └── visualization.py
│
├── tests/                                        # Automated test suite
│   ├── test_data_loader.py                       # Validates data parsing, dates & fuel sums
│   └── test_models.py                            # Validates model training, predictions & PCA
│
├── scratch/                                      # Document generation & formatting scripts
│   ├── generate_methodology_diagram.py
│   └── update_docx.py
│
├── app.py                                        # Streamlit Interactive Decision Support Dashboard
├── CBSL Macro-Financial and Energy Grid Forecasting.ipynb # Exploratory analysis & research notebook
├── cbsl_daily_economic_indicators_2020_2026_preprocesd.csv # Processed dataset (workspace root copy)
├── Capstone project II.docx                      # Academic thesis manuscript
├── requirements.txt                              # Python environment specifications
└── README.md                                     # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites & Environment Setup
Clone this repository and create a Python virtual environment:

```bash
# Clone the repository
git clone <repo-url>
cd "CBSL Macro-Financial and Energy Grid Forecasting"

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 2. Launching the Interactive Dashboard
Launch the Streamlit executive application:

```bash
streamlit run app.py
```

The application runs at `http://localhost:8501` featuring:
- **Tab 1: Executive Macro Telemetry & FX**: USD/LKR exchange trends, gold reserves, overnight liquidity, ASPI index, and rolling correlations.
- **Tab 2: Power Grid & Fuel Mix Decompositions**: Hydro vs. Coal vs. Fuel Oil vs. Wind dispatch shares with monthly seasonality overlays.
- **Tab 3: Day-Ahead Peak Demand Predictor**: Interactive inference tool to forecast day-ahead peak grid MW using recent load differences and cyclic calendar features.
- **Tab 4: Macro Regimes & Scenario Simulator**: Unsupervised PCA + K-Means cluster analysis with interactive FX shock & hydro generation stress testing.

---

### 3. Using the Modular Python Package (`cbsl_forecast`)

You can also use the modular library directly in Python scripts, automated jobs, or external notebooks:

```python
import sys
sys.path.append("src")

from cbsl_forecast.data import load_and_preprocess_data
from cbsl_forecast.models import DemandForecaster, fit_macro_regimes

# 1. Load normalized dataset
df = load_and_preprocess_data()

# 2. Train peak demand forecaster
forecaster = DemandForecaster(alpha=0.2)
forecaster.fit(df)

# 3. Fit macroeconomic regime clusters (K-Means + PCA)
kmeans, pca, scaler, df_clustered = fit_macro_regimes(df, n_clusters=3)
print(f"Data clustered into regimes: {df_clustered['cluster_id'].value_counts().to_dict()}")
```

---

### 4. Running Automated Tests

Run the test suite using `pytest`:

```bash
# On Windows PowerShell:
$env:PYTHONPATH="src"; pytest tests -v

# On Linux / macOS:
PYTHONPATH=src pytest tests -v
```

All 8 test cases validate:
- Dataset discovery and non-empty loading
- Temporal feature consistency (`year`, `month`, `day_name`, `is_weekend`)
- Normalized generation fuel mix summing to 100%
- Autoregressive feature calculations
- Day-ahead peak demand model convergence and inference
- K-Means regime clustering and 2D PCA projection consistency

---

## 📊 Methodology & Analytical Framework

The framework integrates four concurrent pipelines:
1. **Macro-Financial Ingestion**: Daily exchange rates (USD, GBP, EUR, JPY), gold, stock exchange turnover (ASPI, S&P SL20), inflation rates (CCPI, NCPI).
2. **Energy Grid Dynamics**: CEB daily peak demand (MW), total energy generated (GWh), and dispatch shares across Hydro, Coal, Heavy Fuel Oil, and Wind.
3. **Forecasting Engine**: Autoregressive difference formulation ($\Delta \text{Demand}_t$) regularized via Lasso ($L_1$) to prevent overfitting across crisis anomalies.
4. **Stress-Testing Simulation**: Scenario modeling quantifying the foreign exchange transmission effect on thermal fuel imports and hydro displacement risks.

---

## 📜 Citation & Academic Use
This work is submitted as part of **Capstone Project in Data Science II (Semester IV)**.  
All secondary data cohorts sourced from the Central Bank of Sri Lanka (CBSL) and Ceylon Electricity Board (CEB) are acknowledged and used for academic and research purposes.
