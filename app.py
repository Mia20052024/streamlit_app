from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import re

from data_loader import load_tmdb_via_kagglehub, clean_movies, LoadResult
from constants import PAGE_TITLE, PAGE_DESC
from filters import build_sidebar, apply_filters
from components import kpi_cards
from sections import (
    section_question_1,
    section_question_2,
    section_questions_hub,
    section_eda,
    section_leaderboard,
)

PAGE_TITLE = PAGE_TITLE
PAGE_DESC = PAGE_DESC




def render_header() -> None:
    st.set_page_config(page_title=PAGE_TITLE, page_icon="", layout="wide")
    st.title(PAGE_TITLE)
    st.caption(PAGE_DESC)


def render_data_loader() -> LoadResult:
    with st.expander("Data Loading (KaggleHub)", expanded=False):
        st.write("The app downloads the TMDB 5000 dataset via kagglehub.")

    try:
        return load_tmdb_via_kagglehub()
    except Exception:
        st.error("Unable to load data via KaggleHub. Please check network/permissions. Error details are hidden.")
        st.stop()
        return LoadResult(df=pd.DataFrame(), source="Empty data (KaggleHub load failed)")


def main() -> None:
    render_header()

    # Data loading
    load_res = render_data_loader()
    df_full = load_res.df
    # Keep full dataset for chart fallback when no data after filters
    st.session_state["df_full"] = df_full.copy()

    # Sidebar filters
    f = build_sidebar(df_full)
    df_filtered = apply_filters(df_full, f)

    # KPI cards
    kpi_cards(df_filtered)

    # Analysis questions and EDA
    section_question_1(df_filtered)
    section_question_2(df_filtered)
    section_questions_hub(df_filtered)
    section_eda(df_filtered)
    section_leaderboard(df_filtered)



if __name__ == "__main__":
    main()
