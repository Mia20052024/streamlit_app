"""
Data loading and cleaning module (downloads Kaggle dataset via kagglehub).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional
import os
import ast

import numpy as np
import pandas as pd
import streamlit as st
import kagglehub


@dataclass
class LoadResult:
    """Data loading result."""
    df: pd.DataFrame
    source: str


# ------------------------------
# Cleaning and feature engineering
# ------------------------------
def _parse_json_list(x: str) -> List[str]:
    try:
        items = ast.literal_eval(x) if isinstance(x, str) else []
        return [d.get("name", "") for d in items if isinstance(d, dict)]
    except Exception:
        return []


def clean_movies(raw: pd.DataFrame) -> pd.DataFrame:
    """Perform structured cleaning and feature engineering for TMDB 5000 movies dataset."""
    df = raw.copy()

    # Basic type conversions
    df["release_date"] = pd.to_datetime(df.get("release_date"), errors="coerce")
    df["release_year"] = df["release_date"].dt.year

    # Parse JSON-like string columns
    if "genres" in df.columns:
        df["genres_list"] = df["genres"].apply(_parse_json_list)
    else:
        df["genres_list"] = [[] for _ in range(len(df))]

    # Parse production countries, companies, and spoken languages
    if "production_countries" in df.columns:
        df["production_countries_list"] = df["production_countries"].apply(_parse_json_list)
    else:
        df["production_countries_list"] = [[] for _ in range(len(df))]
    if "production_companies" in df.columns:
        df["production_companies_list"] = df["production_companies"].apply(_parse_json_list)
    else:
        df["production_companies_list"] = [[] for _ in range(len(df))]
    if "spoken_languages" in df.columns:
        df["spoken_languages_list"] = df["spoken_languages"].apply(_parse_json_list)
    else:
        df["spoken_languages_list"] = [[] for _ in range(len(df))]

    # Numeric cleaning
    for col in ["budget", "revenue", "runtime", "vote_average", "popularity", "vote_count"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derived metrics
    budget = df.get("budget", pd.Series([np.nan] * len(df)))
    revenue = df.get("revenue", pd.Series([np.nan] * len(df)))
    budget = budget.replace({0: np.nan})
    df["profit"] = revenue - budget
    df["roi"] = np.where(budget.notna(), revenue / budget, np.nan)

    # Simple clipping
    if "budget" in df.columns:
        df["budget_clip"] = df["budget"].clip(lower=0, upper=df["budget"].quantile(0.99))
    if "revenue" in df.columns:
        df["revenue_clip"] = df["revenue"].clip(lower=0, upper=df["revenue"].quantile(0.99))

    return df


# ------------------------------
# Loading: prefer kagglehub
# ------------------------------
@st.cache_data(show_spinner=True)
def load_tmdb_via_kagglehub() -> LoadResult:
    """Download and load the TMDB 5000 dataset via kagglehub."""
    # Download dataset directory (first time will download and cache locally)
    data_dir = kagglehub.dataset_download("tmdb/tmdb-movie-metadata")

    # Candidate CSV paths (official filenames)
    csv_path_candidates: Tuple[str, ...] = (
        os.path.join(data_dir, "tmdb_5000_movies.csv"),
        os.path.join(data_dir, "tmdb_5000_movies_2.csv"),
    )

    csv_path: Optional[str] = next((p for p in csv_path_candidates if os.path.exists(p)), None)
    if not csv_path:
        raise FileNotFoundError("tmdb_5000_movies.csv not found in kagglehub download directory")

    df = pd.read_csv(csv_path)
    df = clean_movies(df)
    return LoadResult(df=df, source=f"kagglehub: {csv_path}")
