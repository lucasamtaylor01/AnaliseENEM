from pathlib import Path
from typing import Tuple

import pandas as pd

INDIR = Path("data/data_raw")
OUTDIR_PROCESSING_BASE = Path("data/data_processed")
OUTDIR_MODEL = Path("data/data_model")

MICRODATA_FILES = {
    2023: "MICRODADOS_ENEM_2023.csv",
    2022: "MICRODADOS_ENEM_2022.csv",
    2021: "MICRODADOS_ENEM_2021.csv",
    2020: "MICRODADOS_ENEM_2020.csv",
    2019: "MICRODADOS_ENEM_2019.csv",
    2018: "MICRODADOS_ENEM_2018.csv",
    2017: "MICRODADOS_ENEM_2017.csv",
    2016: "MICRODADOS_ENEM_2016.csv",
    2015: "MICRODADOS_ENEM_2015.csv",
}

AVAILABLE_YEARS = list(range(2015, 2024))

REQUIRED_MICRODATA_COLUMNS = [
    "NO_MUNICIPIO_PROVA",
    "CO_MUNICIPIO_PROVA",
    "IN_TREINEIRO",
    "SG_UF_PROVA",
    "Q006",
    "TP_PRESENCA_CN",
    "TP_PRESENCA_CH",
    "TP_PRESENCA_LC",
    "TP_PRESENCA_MT",
    "NU_NOTA_CN",
    "NU_NOTA_CH",
    "NU_NOTA_LC",
    "NU_NOTA_MT",
    "NU_NOTA_REDACAO",
]


def split_participants_results(
    df_microdata: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Splits annual microdata into participants and results DataFrames.

    Args:
        df_microdata: Raw annual DataFrame with participant and score columns.

    Returns:
        Tuple containing:
        1) Participants DataFrame (socioeconomic profile and exam location),
        2) Results DataFrame (attendance and scores).
    """

    df_participants = df_microdata[
        [
            "NO_MUNICIPIO_PROVA",
            "CO_MUNICIPIO_PROVA",
            "IN_TREINEIRO",
            "SG_UF_PROVA",
            "Q006",
        ]
    ]
    df_results = df_microdata[
        [
            "SG_UF_PROVA",
            "CO_MUNICIPIO_PROVA",
            "NO_MUNICIPIO_PROVA",
            "TP_PRESENCA_CN",
            "TP_PRESENCA_CH",
            "TP_PRESENCA_LC",
            "TP_PRESENCA_MT",
            "NU_NOTA_CN",
            "NU_NOTA_CH",
            "NU_NOTA_LC",
            "NU_NOTA_MT",
            "NU_NOTA_REDACAO",
        ]
    ]

    return df_participants, df_results


def prepare_directories() -> None:
    """Creates pipeline output directories if they do not already exist."""

    OUTDIR_PROCESSING_BASE.mkdir(parents=True, exist_ok=True)
    OUTDIR_MODEL.mkdir(parents=True, exist_ok=True)


def get_processed_paths(ano: int) -> Tuple[Path, Path]:
    """Builds city-level output paths for a given year.

    Args:
        ano: Reference year for processing.

    Returns:
        Tuple with the processed CSV path and the model CSV path for cities.
    """

    processing_outdir = OUTDIR_PROCESSING_BASE / str(ano)
    processing_outdir.mkdir(parents=True, exist_ok=True)

    processed_path = (
        processing_outdir / f"ANALISE_NOTAS_ENEM_MUNICIPIOS_BRASIL_TRATADO_{ano}.csv"
    )
    model_path = (
        processing_outdir / f"ANALISE_NOTAS_ENEM_MUNICIPIOS_BRASIL_MODELO_{ano}.csv"
    )

    return processed_path, model_path


def get_processing_paths(ano: int) -> Tuple[Path, Path, Path, Path]:
    """Builds all processing output paths for a given year.

    Args:
        ano: Reference year for processing.

    Returns:
        Tuple with the paths in this order:
        1) processed by city,
        2) model by city,
        3) processed by state,
        4) model by state.
    """

    processed_city_path, city_model_path = get_processed_paths(ano)
    processing_outdir = processed_city_path.parent
    processed_state_path = (
        processing_outdir / f"ANALISE_NOTAS_ENEM_UF_BRASIL_TRATADO_{ano}.csv"
    )
    state_model_path = (
        processing_outdir / f"ANALISE_NOTAS_ENEM_UF_BRASIL_MODELO_{ano}.csv"
    )

    return (
        processed_city_path,
        city_model_path,
        processed_state_path,
        state_model_path,
    )


def processed_files_exist(ano: int) -> bool:
    """Checks whether the output files for a year have already been generated.

    Args:
        ano: Reference year for processing.

    Returns:
        True when both expected files exist; False otherwise.
    """

    processed_path, model_path = get_processed_paths(ano)
    return processed_path.exists() and model_path.exists()


def processing_files_exist(ano: int) -> bool:
    """Checks whether all processing output files for a year have been generated.

    Args:
        ano: Reference year for processing.

    Returns:
        True when all expected files exist; False otherwise.
    """

    (
        processed_city_path,
        city_model_path,
        processed_state_path,
        state_model_path,
    ) = get_processing_paths(ano)

    return all(
        path.exists()
        for path in (
            processed_city_path,
            city_model_path,
            processed_state_path,
            state_model_path,
        )
    )


def load_raw_data(ano: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Loads raw ENEM data and returns participants and results DataFrames.

    Only the columns required by the pipeline are loaded to reduce
    memory usage and read time.

    Args:
        ano: Reference year between 2015 and 2023.

    Returns:
        Tuple with raw participants and results DataFrames.

    Raises:
        ValueError: When the provided year is not supported.
    """

    if ano in MICRODATA_FILES:
        microdata_file = INDIR / MICRODATA_FILES[ano]
        df_microdata = pd.read_csv(
            microdata_file,
            sep=";",
            encoding="latin-1",
            usecols=REQUIRED_MICRODATA_COLUMNS,
        )
        return split_participants_results(df_microdata)

    raise ValueError("Invalid year. Please choose a year between 2015 and 2023.")
