from __future__ import annotations

import math
import pandas as pd
import streamlit as st


def kpi_cards(df: pd.DataFrame) -> None:
    n_movies = int(df.shape[0])
    avg_vote = float(df["vote_average"].mean()) if n_movies else math.nan
    med_rev = float(df["revenue"].median()) if n_movies else math.nan
    med_roi = float(df["roi"].median()) if n_movies else math.nan

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Number of Movies", f"{n_movies:,}")
    c2.metric("Average Rating", f"{avg_vote:.2f}" if not math.isnan(avg_vote) else "—")
    c3.metric("Median Revenue", f"${med_rev:,.0f}" if not math.isnan(med_rev) else "—")
    c4.metric("Median ROI", f"{med_roi:.2f}" if not math.isnan(med_roi) else "—")

