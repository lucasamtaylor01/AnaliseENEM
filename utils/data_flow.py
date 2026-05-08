from typing import Tuple

import pandas as pd

from utils.data_loading import (
    processing_files_exist,
    load_raw_data,
    get_processing_paths,
    prepare_directories,
)
from utils.data_processing import (
    process_data,
)

prepare_directories()


def load_or_process_data(ano: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Orchestrates the flow between files, processing, and annual persistence.

    Args:
        ano: Reference year between 2015 and 2023.

    Returns:
        Tuple containing, in this order:
        1) pre-clustering DataFrame by city,
        2) scaled DataFrame by city,
        3) pre-clustering DataFrame by state,
        4) scaled DataFrame by state.

    Raises:
        ValueError: When the provided year is not supported.
    """

    (
        processed_city_path,
        city_model_path,
        processed_state_path,
        state_model_path,
    ) = get_processing_paths(ano)

    if processing_files_exist(ano):
        print(f"Processed data for {ano} already exists. Skipping processing step...\n")
        df_pre_clustering_city = pd.read_csv(processed_city_path)
        x_scaled_city = pd.read_csv(city_model_path)
        df_pre_clustering_state = pd.read_csv(processed_state_path)
        x_scaled_state = pd.read_csv(state_model_path)
        return (
            df_pre_clustering_city,
            x_scaled_city,
            df_pre_clustering_state,
            x_scaled_state,
        )

    print(f"Loading raw data for {ano}...\n")
    df_participants_raw, df_results_raw = load_raw_data(ano)

    print(f"Raw data for {ano} loaded successfully.\n")

    print(f"Processing data for {ano}...\n")
    (
        df_pre_clustering_city,
        x_scaled_city,
        df_pre_clustering_state,
        x_scaled_state,
    ) = process_data(df_participants_raw, df_results_raw, ano)
    print(f"Data for {ano} processed successfully.\n")

    print(f"Saving processed city data for {ano}...\n")
    df_pre_clustering_city.to_csv(processed_city_path, index=False)
    print(f"Processed data saved successfully to {processed_city_path}\n")

    print(f"Saving city model data for {ano}...\n")
    x_scaled_city.to_csv(city_model_path, index=False)
    print(f"Clustering model data saved successfully to {city_model_path}\n")

    print(f"Saving processed state data for {ano}...\n")
    df_pre_clustering_state.to_csv(processed_state_path, index=False)
    print(f"Processed data saved successfully to {processed_state_path}\n")

    print(f"Saving state model data for {ano}...\n")
    x_scaled_state.to_csv(state_model_path, index=False)
    print(f"Clustering model data saved successfully to {state_model_path}\n")

    return (
        df_pre_clustering_city,
        x_scaled_city,
        df_pre_clustering_state,
        x_scaled_state,
    )
