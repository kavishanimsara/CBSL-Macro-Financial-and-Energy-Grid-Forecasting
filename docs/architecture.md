# System Architecture & Technical Specification

## Project Overview
**Title**: CBSL Macro-Financial and Energy Grid Forecasting: An Integrated Multi-Track Analytical & Predictive Framework  
**Course**: Capstone Project in Data Science II (Semester IV)  
**Institutions / Data Cohorts**: Central Bank of Sri Lanka (CBSL), Ceylon Electricity Board (CEB), Department of Census and Statistics (DCS).

---

## 1. Multi-Track Architectural Pipeline

```mermaid
flowchart TD
    subgraph Track1 ["Track 1: Data Ingestion & OCR Extraction"]
        PDFs["CBSL Daily Indicator Bulletins (1,400+ PDFs: 2020–2026)"]
        Parser["PDF Table Parser / OCR Pipeline"]
        ProcessedCSV["cbsl_daily_economic_indicators_2020_2026_preprocesd.csv"]
        PDFs --> Parser --> ProcessedCSV
    end

    subgraph Track2 ["Track 2: Feature Engineering & Preprocessing"]
        Norm["Energy Fuel Mix Normalization (Hydro, Coal, Oil, Wind = 100%)"]
        Temporal["Calendar & Cyclic Day-of-Week Encodings (sin_dow, cos_dow)"]
        Lags["Autoregressive Lags & Differencing (1-day, 2-day, 7-day Lags)"]
        ProcessedCSV --> Norm --> Temporal --> Lags
    end

    subgraph Track3 ["Track 3: Analytics & Forecasting Engines"]
        Model1["Day-Ahead Peak Electricity Demand Forecaster (Lasso / Regularized Linear)"]
        Model2["Macroeconomic & Energy Regime Clustering (K-Means, n=3 + PCA Projection)"]
        Model3["Scenario Simulation Engine (FX Shock & Hydro Sensitivity Stress-Testing)"]
        Lags --> Model1
        Lags --> Model2
        Lags --> Model3
    end

    subgraph Track4 ["Track 4: Executive Decision Support System"]
        UI["Streamlit Interactive Telemetry Dashboard (app.py)"]
        Tab1["Tab 1: Executive Macro Telemetry & FX"]
        Tab2["Tab 2: Power Grid & Fuel Mix Decompositions"]
        Tab3["Tab 3: Day-Ahead Peak Demand Predictor"]
        Tab4["Tab 4: Macro Regimes & Scenario Simulator"]
        Model1 --> Tab3
        Model2 --> Tab4
        Model3 --> Tab4
        ProcessedCSV --> Tab1
        ProcessedCSV --> Tab2
        Tab1 --> UI
        Tab2 --> UI
        Tab3 --> UI
        Tab4 --> UI
    end
```

---

## 2. Directory Layout & Module Responsibilities

- **`config/config.yaml`**: Centralized configuration specifying data sources, feature mappings, model hyper-parameters, and visualization styles.
- **`data/`**:
  - `data/raw/`: Reference to original daily PDF bulletins (`raw_pdfs/`).
  - `data/processed/`: Modeling-ready normalized daily time series (`cbsl_daily_economic_indicators_2020_2026_preprocesd.csv`).
- **`src/cbsl_forecast/`**:
  - `data/loader.py`: Automated ingestion, sorting, calendar generation, and synthetic fallback generation.
  - `features/build_features.py`: Computes autoregressive delta targets ($y_t = \text{Demand}_t - \text{Demand}_{t-1}$), multi-horizon lag differences, and cyclic day-of-week sine/cosine transformations.
  - `models/demand_model.py`: Day-ahead peak demand forecasting pipeline with standardization and L1 regularization.
  - `models/regimes.py`: Multi-indicator macroeconomic regime clustering (K-Means) with 2D principal component analysis (PCA).
  - `utils/visualization.py`: Unified Plotly styling, responsive layouts, color maps, and time navigation range sliders.
- **`app.py`**: Streamlit executive web application maintaining complete backward-compatibility and real-time interaction.
- **`tests/`**: Pytest test suite validating data integrity, preprocessing correctness, feature math, and model training convergence.
