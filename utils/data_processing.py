import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Sequence, Tuple

import pandas as pd
from utils.data_loading import (
    split_participants_results as split_participants_results_base,
)

SCORE_COLUMNS_CLUSTERING = [
    "NATURAL_SCIENCES_SCORE_AVG",
    "HUMANITIES_SCORE_AVG",
    "LANGUAGES_SCORE_AVG",
    "MATH_SCORE_AVG",
    "ESSAY_SCORE_AVG",
]


def process_participants(df_participants_raw: pd.DataFrame) -> pd.DataFrame:
    """Filters valid participants and calculates average family income by city.

    Args:
        df_participants_raw: Raw DataFrame with participant data.

    Returns:
        DataFrame aggregated by city with columns:
        CITY_CODE, CITY, and FAMILY_INCOME_SM_AVG.
    """

    df_participants = df_participants_raw.rename(columns={
        'NO_MUNICIPIO_PROVA': 'CITY',
        'CO_MUNICIPIO_PROVA': 'CITY_CODE',
    })

    income_map_sm = {
        "A": 0.0,
        "B": 0.5,
        "C": 1.25,
        "D": 1.75,
        "E": 2.25,
        "F": 2.75,
        "G": 3.5,
        "H": 4.5,
        "I": 5.5,
        "J": 6.5,
        "K": 7.5,
        "L": 8.5,
        "M": 9.5,
        "N": 11.0,
        "O": 13.5,
        "P": 17.5,
        "Q": 20.0,
    }

    df_participants["Q006"] = (
        df_participants["Q006"].squeeze().map(income_map_sm).astype("float64")
    )
    df_participants = df_participants.rename(columns={"Q006": "FAMILY_INCOME_SM"})

    if "FAMILY_INCOME_SM" in df_participants.columns:
        if not np.issubdtype(
            df_participants["FAMILY_INCOME_SM"].dropna().dtype, np.number
        ):
            df_participants["FAMILY_INCOME_SM"] = (
                df_participants["FAMILY_INCOME_SM"].squeeze().map(income_map_sm)
            )

        mean_income_by_state = df_participants.groupby("SG_UF_PROVA")[
            "FAMILY_INCOME_SM"
        ].transform("mean")
        df_participants["FAMILY_INCOME_SM"] = df_participants[
            "FAMILY_INCOME_SM"
        ].fillna(mean_income_by_state)

        df_participants["FAMILY_INCOME_SM"] = df_participants[
            "FAMILY_INCOME_SM"
        ].fillna(df_participants["FAMILY_INCOME_SM"].mean())

    df_participants = df_participants[df_participants["IN_TREINEIRO"] != 1]
    df_participants = df_participants.drop(columns=["IN_TREINEIRO"])

    df_participants["CITY"] = df_participants["CITY"].str.upper()

    df_participants["FAMILY_INCOME_SM_LOG"] = np.log1p(
        df_participants["FAMILY_INCOME_SM"]
    )

    df_outlier_filtered = df_participants.copy()

    q1_values = [0.25, 0.2, 0.15, 0.1, 0.05]
    q3_values = [0.75, 0.8, 0.85, 0.9, 0.95]

    col = "FAMILY_INCOME_SM_LOG"

    for q1_val, q3_val in zip(q1_values, q3_values):
        df_filtered = df_outlier_filtered.copy()

        Q1 = df_outlier_filtered[col].quantile(q1_val)
        Q3 = df_outlier_filtered[col].quantile(q3_val)
        IQR = Q3 - Q1

        df_filtered = df_filtered[
            (df_filtered[col] >= Q1 - 1.5 * IQR)
            & (df_filtered[col] <= Q3 + 1.5 * IQR)
        ]

        removed_proportion = (
            (df_outlier_filtered.shape[0] - df_filtered.shape[0])
            / df_outlier_filtered.shape[0]
        ) * 100

        if removed_proportion <= 5:
            print(
                f"Income outlier treatment | Q1={q1_val}, Q3={q3_val} {removed_proportion:.2f}% removed"
            )
            df_outlier_filtered = df_filtered.copy()
            break
    else:
        print(f"No suitable cut for {col} — keeping original data\n")

    df_participants = df_outlier_filtered.copy()
    df_participants = df_participants.drop(columns=["FAMILY_INCOME_SM_LOG"])

    df_city = (
        df_participants.groupby("CITY_CODE")
        .agg(
            CITY=("CITY", "first"),
            FAMILY_INCOME_SM_AVG=("FAMILY_INCOME_SM", "mean"),
        )
        .reset_index()
    )

    return df_city


def process_results(df_results_raw: pd.DataFrame) -> pd.DataFrame:
    """Filters valid attendance and calculates average scores by city.

    Args:
        df_results_raw: Raw DataFrame with individual participant results.

    Returns:
        DataFrame aggregated by city with participant count,
        subject averages, and overall average.
    """

    df_results = df_results_raw.rename(columns={'CO_MUNICIPIO_PROVA': 'CITY_CODE'})

    df_results = df_results[df_results["TP_PRESENCA_CN"] == 1]
    df_results = df_results[df_results["TP_PRESENCA_CH"] == 1]
    df_results = df_results[df_results["TP_PRESENCA_LC"] == 1]
    df_results = df_results[df_results["TP_PRESENCA_MT"] == 1]

    df_results = df_results.drop(
        columns=["TP_PRESENCA_CN", "TP_PRESENCA_CH", "TP_PRESENCA_LC", "TP_PRESENCA_MT"]
    )

    score_columns = [
        "NU_NOTA_CN",
        "NU_NOTA_CH",
        "NU_NOTA_LC",
        "NU_NOTA_MT",
        "NU_NOTA_REDACAO",
    ]

    df_outlier_filtered = df_results.copy()

    q1_values = [0.25, 0.2, 0.15, 0.1, 0.05]
    q3_values = [0.75, 0.8, 0.85, 0.9, 0.95]

    n_original = df_results.shape[0]

    for q1_val, q3_val in zip(q1_values, q3_values):

        df_temp = df_results.copy()

        for col in score_columns:
            Q1 = df_results[col].quantile(q1_val)
            Q3 = df_results[col].quantile(q3_val)
            IQR = Q3 - Q1

            df_temp = df_temp[
                (df_temp[col] >= Q1 - 1.5 * IQR) & (df_temp[col] <= Q3 + 1.5 * IQR)
            ]

        total_proportion = ((n_original - df_temp.shape[0]) / n_original) * 100

        if total_proportion <= 5:
            print(
                f"Score outlier treatment | Q1={q1_val}, Q3={q3_val} {total_proportion:.2f}% removed"
            )
            df_outlier_filtered = df_temp.copy()
            break
    else:
        print("No valid global cut — keeping data")

    df_results = df_outlier_filtered.copy()

    df_results = df_results.groupby('CITY_CODE').agg(
        STATE=('SG_UF_PROVA', 'first'),
        NUM_PARTICIPANTS=('CITY_CODE', 'size'),
        NATURAL_SCIENCES_SCORE_AVG=('NU_NOTA_CN', 'mean'),
        HUMANITIES_SCORE_AVG=('NU_NOTA_CH', 'mean'),
        LANGUAGES_SCORE_AVG=('NU_NOTA_LC', 'mean'),
        MATH_SCORE_AVG=('NU_NOTA_MT', 'mean'),
        ESSAY_SCORE_AVG=('NU_NOTA_REDACAO', 'mean'),
    ).reset_index()

    df_results["OVERALL_SCORE_AVG"] = df_results[
        [
            "NATURAL_SCIENCES_SCORE_AVG",
            "HUMANITIES_SCORE_AVG",
            "LANGUAGES_SCORE_AVG",
            "MATH_SCORE_AVG",
            "ESSAY_SCORE_AVG",
        ]
    ].mean(axis=1)

    return df_results


def prepare_clustering_data(
    df_city: pd.DataFrame,
    df_results: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Merges city data and standardizes features for clustering.

    Args:
        df_city: DataFrame with income indicators by city.
        df_results: DataFrame with performance indicators by city.

    Returns:
        Tuple with the pre-clustering DataFrame by city and the
        standardized features by city.
    """

    df_pre_clustering_city = df_results.merge(
        df_city,
        on='CITY_CODE',
        how='left',
    )

    x_scaled_city = scale_clustering_features(
        df_pre_clustering_city,
        [
            "CITY",
            "CITY_CODE",
            "FAMILY_INCOME_SM_AVG",
            "STATE",
            "NUM_PARTICIPANTS",
            "OVERALL_SCORE_AVG",
        ],
    )

    return df_pre_clustering_city, x_scaled_city


def aggregate_by_state(df_pre_clustering_city: pd.DataFrame) -> pd.DataFrame:
    """Aggregates city-level data by state using participant-weighted averages.

    Args:
        df_pre_clustering_city: Pre-clustering DataFrame at the city level.

    Returns:
        DataFrame aggregated by state with total participants, average income,
        and weighted average scores.
    """

    score_columns = [*SCORE_COLUMNS_CLUSTERING, "OVERALL_SCORE_AVG"]

    return (
        df_pre_clustering_city.groupby("STATE")
        .apply(
            lambda group: pd.Series(
                {
                    "NUM_PARTICIPANTS": group["NUM_PARTICIPANTS"].sum(),
                    "FAMILY_INCOME_SM_AVG": weighted_average(group, "FAMILY_INCOME_SM_AVG"),
                    **{col: weighted_average(group, col) for col in score_columns},
                }
            )
        )
        .reset_index()
        .sort_values("STATE")
        .reset_index(drop=True)
    )


def scale_clustering_features(
    df_pre_clustering: pd.DataFrame,
    columns_to_exclude: Sequence[str],
) -> pd.DataFrame:
    """Prepares features for clustering by removing metadata and scaling scores.

    Args:
        df_pre_clustering: DataFrame with numerical variables and metadata.
        columns_to_exclude: Columns removed before the scaling step.

    Returns:
        DataFrame with score features standardized by StandardScaler.
    """

    x_scaled = df_pre_clustering.drop(columns=columns_to_exclude).copy()
    scaler = StandardScaler()
    x_scaled[SCORE_COLUMNS_CLUSTERING] = scaler.fit_transform(
        x_scaled[SCORE_COLUMNS_CLUSTERING]
    )
    return x_scaled


def weighted_average(
    group: pd.DataFrame,
    column: str,
    weight: str = "NUM_PARTICIPANTS",
) -> float | object:
    """Calculates the weighted average of a column using the given weight.

    Args:
        group: DataFrame with values and weights.
        column: Name of the numeric column to aggregate.
        weight: Name of the weight column.

    Returns:
        Weighted average value, or pd.NA when the sum of weights is zero.
    """

    d = group[[column, weight]].dropna()
    total_weight = d[weight].sum()
    return (d[column] * d[weight]).sum() / total_weight if total_weight != 0 else pd.NA


def process_data(
    df_participants_raw: pd.DataFrame,
    df_results_raw: pd.DataFrame,
    year: int,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Runs the full processing pipeline for a specific year.

    Args:
        df_participants_raw: Raw participants DataFrame.
        df_results_raw: Raw results DataFrame.
        year: Reference year for processing.

    Returns:
        Tuple with 4 outputs in this order:
        1) pre-clustering data by city,
        2) scaled features by city,
        3) pre-clustering data by state,
        4) scaled features by state.
    """

    _ = year

    df_participants = process_participants(df_participants_raw)
    df_results = process_results(df_results_raw)
    df_pre_clustering_city, x_scaled_city = prepare_clustering_data(
        df_participants, df_results
    )
    df_pre_clustering_state = aggregate_by_state(df_pre_clustering_city)
    x_scaled_state = scale_clustering_features(
        df_pre_clustering_state,
        ["STATE", "FAMILY_INCOME_SM_AVG", "NUM_PARTICIPANTS", "OVERALL_SCORE_AVG"],
    )

    return (
        df_pre_clustering_city,
        x_scaled_city,
        df_pre_clustering_state,
        x_scaled_state,
    )


def split_participants_results(
    df_microdata: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Delegates microdata splitting to the cyearnical implementation.

    Args:
        df_microdata: Raw annual DataFrame with all relevant columns.

    Returns:
        Tuple containing participants DataFrame and results DataFrame.
    """

    return split_participants_results_base(df_microdata)
