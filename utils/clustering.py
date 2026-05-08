import pandas as pd
from sklearn.cluster import KMeans

from utils.data_loading import AVAILABLE_YEARS, OUTDIR_MODEL
from utils.data_flow import load_or_process_data


def cluster_data(
    df_pre_clustering: pd.DataFrame,
    x_scaled: pd.DataFrame,
) -> pd.DataFrame:
    """Runs KMeans and reorders clusters by average performance.

    Args:
        df_pre_clustering: Aggregated DataFrame for the analyzed level
            (city or state), containing score and income metrics.
        x_scaled: DataFrame with features used in KMeans.

    Returns:
        Post-clustering DataFrame with the CLUSTER column reordered by
        average performance (0 = lowest, 2 = highest).
    """

    kmeans = KMeans(n_clusters=3, n_init=200, random_state=0)
    kmeans.fit(x_scaled)

    labels = kmeans.labels_
    df_post_clustering = df_pre_clustering.copy()
    df_post_clustering["CLUSTER_ORIGINAL"] = labels

    performance_by_cluster = (
        df_post_clustering.groupby("CLUSTER_ORIGINAL")["OVERALL_SCORE_AVG"]
        .mean()
        .sort_values(ascending=True)
    )

    cluster_map = {
        original_cluster: new_cluster
        for new_cluster, original_cluster in enumerate(performance_by_cluster.index)
    }

    df_post_clustering["CLUSTER"] = df_post_clustering["CLUSTER_ORIGINAL"].map(
        cluster_map
    )
    df_post_clustering = df_post_clustering.drop(columns=["CLUSTER_ORIGINAL"])

    return df_post_clustering


def process_year(year: int) -> None:
    """Processes a full year: data processing, clustering, and export.

    Args:
        year: Reference year to process.
    """

    print(f"Starting processing for year {year}...\n")
    (
        df_pre_clustering_city,
        x_scaled_city,
        df_pre_clustering_state,
        x_scaled_state,
    ) = load_or_process_data(year)

    print(f"Running city-level clustering for year {year}...\n")
    df_post_clustering_city = cluster_data(
        df_pre_clustering_city,
        x_scaled_city,
    )
    print(f"City-level clustering completed successfully for year {year}.\n")

    (OUTDIR_MODEL / str(year)).mkdir(parents=True, exist_ok=True)

    city_cluster_path = (
        OUTDIR_MODEL
        / str(year)
        / f"ANALISE_NOTAS_ENEM_MUNICIPIOS_BRASIL_CLUSTERS_{year}.csv"
    )
    df_post_clustering_city.to_csv(city_cluster_path, index=False)
    print(f"City clustering data saved successfully to {city_cluster_path}\n")

    print(f"Running state-level clustering for year {year}...\n")
    df_post_clustering_state = cluster_data(
        df_pre_clustering_state,
        x_scaled_state,
    )
    print(f"State-level clustering completed successfully for year {year}.\n")

    state_cluster_path = (
        OUTDIR_MODEL / str(year) / f"ANALISE_NOTAS_ENEM_UF_BRASIL_CLUSTERS_{year}.csv"
    )
    df_post_clustering_state.to_csv(state_cluster_path, index=False)
    print(f"State clustering data saved successfully to {state_cluster_path}\n")


def run_all_years() -> None:
    """Runs the clustering pipeline for all available years."""

    for year in AVAILABLE_YEARS:
        process_year(year)
