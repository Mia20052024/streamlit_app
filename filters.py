from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import pandas as pd
import streamlit as st


@dataclass
class Filters:
    years: Tuple[int, int]
    genres: List[str]
    vote_range: Tuple[float, float]
    runtime_range: Tuple[float, float]
    languages: List[str]
    roi_min: float
    min_votes: int
    exclude_zero_revenue: bool
    title_kw: str


def build_sidebar(df: pd.DataFrame) -> Filters:
    st.sidebar.header("Filters")

    year_min = int(max(1900, np.nanmin(df["release_year"].values)))
    year_max = int(np.nanmax(df["release_year"].values))
    years = st.sidebar.slider("Release year range", year_min, year_max, (year_min, year_max))

    all_genres = sorted({g for lst in df["genres_list"] for g in (lst or [])})
    genres = st.sidebar.multiselect("Genres", all_genres, default=[])

    if "original_language" in df.columns:
        all_langs = sorted(list({str(x) for x in df["original_language"].dropna().unique()}))
    else:
        all_langs = []
    languages = st.sidebar.multiselect("Language (multi-select)", all_langs, default=[])

    v_min, v_max = float(np.nanmin(df["vote_average"])), float(np.nanmax(df["vote_average"]))
    vote_range = st.sidebar.slider("Vote average range", 0.0, 10.0, (max(0.0, v_min), min(10.0, v_max)))

    rt_min = float(np.nanmin(df["runtime"])) if df["runtime"].notna().any() else 0.0
    rt_max = float(np.nanmax(df["runtime"])) if df["runtime"].notna().any() else 300.0
    runtime_range = st.sidebar.slider(
        "Runtime (minutes)", 0.0, max(60.0, rt_max), (max(0.0, rt_min), min(max(60.0, rt_max), rt_max))
    )

    roi_max = float(np.nanpercentile(df["roi"], 98)) if df["roi"].notna().any() else 5.0
    roi_min = st.sidebar.slider("Minimum ROI", 0.0, max(1.0, roi_max), 0.0)
    if "vote_count" in df.columns and df["vote_count"].notna().any():
        vc_min = int(df["vote_count"].min())
        vc_max = int(df["vote_count"].max())
    else:
        vc_min, vc_max = 0, 0
    min_votes = st.sidebar.slider("Minimum vote count", vc_min, max(vc_min, vc_max), vc_min)

    title_kw = st.sidebar.text_input("Title keyword (optional)", value="")

    st.sidebar.markdown("---")
    exclude_zero_revenue = st.sidebar.checkbox("Exclude revenue = 0/missing", value=True)

    return Filters(
        years=years,
        genres=genres,
        vote_range=vote_range,
        runtime_range=runtime_range,
        languages=languages,
        roi_min=roi_min,
        min_votes=min_votes,
        exclude_zero_revenue=exclude_zero_revenue,
        title_kw=title_kw.strip(),
    )


def apply_filters(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)

    mask &= df["release_year"].between(f.years[0], f.years[1])

    if f.genres:
        mask &= df["genres_list"].apply(lambda lst: any(g in (lst or []) for g in f.genres))

    if f.languages and "original_language" in df.columns:
        mask &= df["original_language"].isin(f.languages)

    mask &= df["vote_average"].between(f.vote_range[0], f.vote_range[1])

    if df["runtime"].notna().any():
        mask &= df["runtime"].between(f.runtime_range[0], f.runtime_range[1])

    if df["roi"].notna().any() and f.roi_min > 0:
        mask &= df["roi"] >= f.roi_min

    if "vote_count" in df.columns and f.min_votes > 0:
        mask &= df["vote_count"] >= f.min_votes

    if f.exclude_zero_revenue and "revenue" in df.columns:
        mask &= df["revenue"].fillna(0) > 0

    if f.title_kw:
        kw = f.title_kw.lower()
        mask &= df["title"].astype(str).str.lower().str.contains(kw)

    return df.loc[mask].copy()


