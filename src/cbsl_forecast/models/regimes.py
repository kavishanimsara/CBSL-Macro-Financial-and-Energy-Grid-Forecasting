from typing import Tuple, Dict, Any, List
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

CLUSTER_COLUMNS = ["usd_tt_selling", "peak_demand", "total_energy", "hydro_pct", "thermal_coal_pct"]

def fit_macro_regimes(
    df: pd.DataFrame,
    cluster_cols: List[str] = CLUSTER_COLUMNS,
    n_clusters: int = 3,
    random_state: int = 42
) -> Tuple[KMeans, PCA, StandardScaler, pd.DataFrame]:
    """
    Fit K-Means clustering and PCA projection on multi-dimensional macro-energy observations.
    
    Returns:
        kmeans: Fitted KMeans model
        pca: Fitted 2-component PCA model
        scaler: Fitted StandardScaler
        df_clustered: DataFrame with cluster_id, pca_1, pca_2 columns added
    """
    cols = ["report_date"] + cluster_cols
    df_t4 = df[cols].dropna().copy().reset_index(drop=True)

    scaler = StandardScaler()
    X_sc = scaler.fit_transform(df_t4[cluster_cols])

    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    df_t4["cluster_id"] = kmeans.fit_predict(X_sc)

    pca = PCA(n_components=2, random_state=random_state)
    pca_2d = pca.fit_transform(X_sc)
    df_t4["pca_1"] = pca_2d[:, 0]
    df_t4["pca_2"] = pca_2d[:, 1]

    return kmeans, pca, scaler, df_t4
