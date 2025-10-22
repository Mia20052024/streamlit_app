from __future__ import annotations

import re
import numpy as np
import pandas as pd
import altair as alt


def chart_budget_vs_revenue(df: pd.DataFrame) -> alt.Chart:
    base = alt.Chart(df).mark_circle(opacity=0.6).encode(
        x=alt.X("budget_clip", title="Budget", axis=alt.Axis(format="~s")),
        y=alt.Y("revenue_clip", title="Revenue", axis=alt.Axis(format="~s")),
        color=alt.Color("roi", title="ROI", scale=alt.Scale(scheme="tealblues")),
        size=alt.Size("popularity", title="Popularity", scale=alt.Scale(range=[10, 300])),
        tooltip=["title", "release_year", "budget", "revenue", alt.Tooltip("roi", format=".2f")],
    )
    reg = (
        alt.Chart(df)
        .transform_regression("budget_clip", "revenue_clip")
        .mark_line(color="orangered", size=2)
        .encode(x="budget_clip:Q", y="revenue_clip:Q")
    )
    return (base + reg).properties(height=420)


def chart_vote_vs_budget(df: pd.DataFrame) -> alt.Chart:
    sub = df.dropna(subset=["budget_clip", "vote_average"]).query("budget_clip > 0")
    base = alt.Chart(sub).mark_circle(opacity=0.5).encode(
        x=alt.X("budget_clip:Q", title="Budget (clipped, log scale)", scale=alt.Scale(type="log")),
        y=alt.Y("vote_average:Q", title="Rating"),
        color=alt.Color("genres_list:N", legend=None),
        tooltip=["title", "release_year", "budget", "vote_average"],
    )
    reg = (
        alt.Chart(sub)
        .transform_regression("budget_clip", "vote_average")
        .mark_line(color="#d62728", size=2)
        .encode(x="budget_clip:Q", y="vote_average:Q")
    )
    return (base + reg).properties(height=380)


 


def chart_popularity_vs_revenue(df: pd.DataFrame) -> alt.Chart:
    sub = df.dropna(subset=["popularity", "revenue_clip"]).query("revenue_clip > 0")
    return (
        alt.Chart(sub)
        .mark_circle(opacity=0.6)
        .encode(
            x=alt.X("popularity:Q", title="Popularity"),
            y=alt.Y("revenue_clip:Q", title="Revenue (clipped)", axis=alt.Axis(format="~s")),
            color=alt.Color("vote_average:Q", title="Rating", scale=alt.Scale(scheme="viridis")),
            tooltip=["title", "release_year", "popularity", "revenue", "vote_average"],
        )
        .properties(height=380)
    )


def chart_country_roi(df: pd.DataFrame, top_k: int = 15, min_count: int = 10) -> alt.Chart:
    if "production_countries_list" not in df.columns:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_bar()
    exploded = df.explode("production_countries_list")
    grp = exploded.groupby("production_countries_list").agg(count=("id", "count"), median_roi=("roi", "median")).reset_index()
    grp = grp[grp["count"] >= min_count].dropna(subset=["production_countries_list"])
    top = grp.sort_values("median_roi", ascending=False).head(top_k)
    return (
        alt.Chart(top)
        .mark_bar()
        .encode(
            x=alt.X("median_roi:Q", title="Median ROI"),
            y=alt.Y("production_countries_list:N", sort="-x", title="Production Country"),
            tooltip=["production_countries_list", alt.Tooltip("count", title="Count"), alt.Tooltip("median_roi", format=".2f")],
            color=alt.Color("median_roi:Q", legend=None, scale=alt.Scale(scheme="greens")),
        )
        .properties(height=28 * len(top))
    )


def chart_company_roi(df: pd.DataFrame, top_k: int = 15, min_count: int = 20) -> alt.Chart:
    if "production_companies_list" not in df.columns:
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_bar()
    exploded = df.explode("production_companies_list")
    grp = exploded.groupby("production_companies_list").agg(count=("id", "count"), median_roi=("roi", "median")).reset_index()
    grp = grp[grp["count"] >= min_count].dropna(subset=["production_companies_list"])
    top = grp.sort_values("median_roi", ascending=False).head(top_k)
    return (
        alt.Chart(top)
        .mark_bar()
        .encode(
            x=alt.X("median_roi:Q", title="Median ROI"),
            y=alt.Y("production_companies_list:N", sort="-x", title="Production Company"),
            tooltip=["production_companies_list", alt.Tooltip("count", title="Count"), alt.Tooltip("median_roi", format=".2f")],
            color=alt.Color("median_roi:Q", legend=None, scale=alt.Scale(scheme="blues")),
        )
        .properties(height=24 * len(top))
    )


def chart_genre_share_by_decade(df: pd.DataFrame, top_n_genres: int = 6) -> alt.Chart:
    sub = df.dropna(subset=["release_year"]).copy()
    sub["decade"] = (sub["release_year"] // 10 * 10).astype("Int64")
    exploded = sub.explode("genres_list")
    counts = exploded.groupby("genres_list").size().sort_values(ascending=False).head(top_n_genres)
    top_genres = set(counts.index.tolist())
    exploded = exploded[exploded["genres_list"].isin(top_genres)]
    agg = exploded.groupby(["decade", "genres_list"]).size().reset_index(name="n")
    total = agg.groupby("decade")["n"].transform("sum")
    agg["share"] = agg["n"] / total
    return (
        alt.Chart(agg)
        .mark_bar()
        .encode(
            x=alt.X("decade:O", title="Decade"),
            y=alt.Y("share:Q", title="Share", axis=alt.Axis(format="%")),
            color=alt.Color("genres_list:N", title="Genre"),
            tooltip=["decade", "genres_list", alt.Tooltip("share", format=".1%")],
        )
        .properties(height=380)
    )


def chart_genre_roi(df: pd.DataFrame, top_k: int = 10) -> alt.Chart:
    exploded = df.explode("genres_list")
    grp = (
        exploded.groupby("genres_list", dropna=True)
        .agg(count=("id", "count"), median_roi=("roi", "median"))
        .reset_index()
        .dropna(subset=["genres_list"])
    )
    top = grp.sort_values("median_roi", ascending=False).head(top_k)
    return (
        alt.Chart(top)
        .mark_bar()
        .encode(
            x=alt.X("median_roi:Q", title="Median ROI"),
            y=alt.Y("genres_list:N", sort="-x", title="Genre"),
            color=alt.Color("median_roi:Q", scale=alt.Scale(scheme="greens"), legend=None),
            tooltip=["genres_list", alt.Tooltip("count", title="Count"), alt.Tooltip("median_roi", format=".2f")],
        )
        .properties(height=30 * len(top))
    )



def chart_runtime_vote_loess_facet(df: pd.DataFrame, top_k: int = 4) -> alt.Chart:
    sub = df.dropna(subset=["runtime", "vote_average"]).explode("genres_list")
    counts = sub.groupby("genres_list").size().sort_values(ascending=False).head(top_k)
    sub = sub[sub["genres_list"].isin(counts.index)].copy()
    base = alt.Chart(sub).mark_circle(opacity=0.2, size=18).encode(x=alt.X("runtime:Q", title="Runtime"), y=alt.Y("vote_average:Q", title="Rating"))
    loess = alt.Chart(sub).transform_loess("runtime", "vote_average", bandwidth=0.3, groupby=["genres_list"]).mark_line(color="#1f77b4").encode(x="runtime:Q", y="vote_average:Q")
    return alt.layer(base, loess).facet(column=alt.Column("genres_list:N", title="Genre"))


def chart_tag_count_relation(df: pd.DataFrame, target: str = "vote") -> alt.Chart:
    sub = df.copy()
    sub["tag_count"] = df["genres_list"].apply(lambda x: len(x or []))
    y_col = "vote_average" if target == "vote" else "roi"
    sub = sub.dropna(subset=[y_col])
    base = alt.Chart(sub).mark_circle(opacity=0.5).encode(
        x=alt.X("tag_count:Q", title="Genre tag count"),
        y=alt.Y(f"{y_col}:Q", title="Rating" if target == "vote" else "ROI"),
        color=alt.Color("popularity:Q", title="Popularity", scale=alt.Scale(scheme="tealblues")),
        tooltip=["title", "tag_count", y_col],
    )
    reg = alt.Chart(sub).transform_regression("tag_count", y_col).mark_line(color="#d62728").encode(x="tag_count:Q", y=f"{y_col}:Q")
    return (base + reg).properties(height=360)


def chart_country_language_heat(df: pd.DataFrame, metric: str = "roi", min_count: int = 10, top_c: int = 15, top_l: int = 10) -> alt.Chart:
    if "production_countries_list" not in df.columns or "original_language" not in df.columns:
        return alt.Chart(pd.DataFrame({"x": [], "y": [], "v": []})).mark_rect()
    exploded = df.explode("production_countries_list").dropna(subset=["production_countries_list", "original_language"])
    grp = exploded.groupby(["production_countries_list", "original_language"]).agg(n=("id", "count"), v=(metric, "median")).reset_index()
    top_countries = grp.groupby("production_countries_list")["n"].sum().sort_values(ascending=False).head(top_c).index
    top_langs = grp.groupby("original_language")["n"].sum().sort_values(ascending=False).head(top_l).index
    use = grp[(grp["n"] >= min_count) & grp["production_countries_list"].isin(top_countries) & grp["original_language"].isin(top_langs)]
    title_map = {"roi": "Median ROI", "revenue": "Median Revenue"}
    return alt.Chart(use).mark_rect().encode(
        x=alt.X("original_language:N", title="Language"),
        y=alt.Y("production_countries_list:N", title="Country"),
        color=alt.Color("v:Q", title=title_map.get(metric, metric), scale=alt.Scale(scheme="redblue")),
        tooltip=["production_countries_list", "original_language", alt.Tooltip("v", format=".2f"), alt.Tooltip("n", title="Count")],
    ).properties(height=26 * use["production_countries_list"].nunique() if not use.empty else 200)


 


 


def chart_month_seasonality(df: pd.DataFrame) -> alt.VConcatChart:
    if "release_date" not in df.columns:
        return alt.vconcat()
    sub = df.dropna(subset=["release_date"]).copy()
    sub["month"] = sub["release_date"].dt.month
    grp = sub.groupby("month").agg(avg_rev=("revenue", "mean"), avg_vote=("vote_average", "mean")).reset_index()
    bar_rev = alt.Chart(grp).mark_bar(color="#2ca02c").encode(x=alt.X("month:O", title="Month"), y=alt.Y("avg_rev:Q", title="Average revenue", axis=alt.Axis(format="~s")))
    bar_vote = alt.Chart(grp).mark_bar(color="#1f77b4").encode(x=alt.X("month:O", title="Month"), y=alt.Y("avg_vote:Q", title="Average rating"))
    return alt.vconcat(bar_rev.properties(height=260), bar_vote.properties(height=220))


def chart_decade_multi_trend(df: pd.DataFrame) -> alt.Chart:
    sub = df.dropna(subset=["release_year"]).copy()
    sub["decade"] = (sub["release_year"] // 10 * 10).astype("Int64")
    grp = sub.groupby("decade").agg(avg_budget=("budget", "mean"), avg_revenue=("revenue", "mean"), avg_vote=("vote_average", "mean")).reset_index()
    tidy = grp.melt(id_vars=["decade"], var_name="metric", value_name="value")
    return alt.Chart(tidy).mark_line(point=True).encode(
        x=alt.X("decade:O", title="Decade"), y=alt.Y("value:Q", title=None), color=alt.Color("metric:N", title="Metric"), tooltip=["decade", alt.Tooltip("value", format="~s")]
    ).properties(height=380)


 


 


 


 


def chart_budget_bin_roi_turning(df: pd.DataFrame, bins: int = 8) -> alt.Chart:
    sub = df.dropna(subset=["budget_clip", "roi"]).query("budget_clip > 0")
    if sub.empty:
        return alt.Chart(pd.DataFrame()).mark_line()
    b = pd.qcut(sub["budget_clip"], q=min(bins, sub.shape[0]), duplicates="drop")
    agg = sub.assign(bin=b.astype(str)).groupby("bin").agg(med_roi=("roi", "median"), x=("budget_clip", "median"), n=("id", "count")).reset_index()
    peak_idx = agg["med_roi"].idxmax()
    peak = agg.loc[[peak_idx]]
    line = alt.Chart(agg).mark_line(point=True, color="#1f77b4").encode(
        x=alt.X("x:Q", title="Budget (bin median)"), y=alt.Y("med_roi:Q", title="Median ROI"), tooltip=["bin", alt.Tooltip("med_roi", format=".2f"), alt.Tooltip("n", title="Count")]
    )
    peak_mark = alt.Chart(peak).mark_point(color="red", size=120).encode(x="x:Q", y="med_roi:Q")
    return (line + peak_mark).properties(height=360)


def chart_genre_country_heat(df: pd.DataFrame, top_g: int = 10, top_c: int = 12, min_count: int = 8) -> alt.Chart:
    if "production_countries_list" not in df.columns:
        return alt.Chart(pd.DataFrame()).mark_rect()
    sub = df.explode("genres_list").explode("production_countries_list").dropna(subset=["genres_list", "production_countries_list"])
    grp = sub.groupby(["genres_list", "production_countries_list"]).agg(n=("id", "count"), med_roi=("roi", "median")).reset_index()
    top_genres = grp.groupby("genres_list")["n"].sum().sort_values(ascending=False).head(top_g).index
    top_countries = grp.groupby("production_countries_list")["n"].sum().sort_values(ascending=False).head(top_c).index
    use = grp[(grp["n"] >= min_count) & grp["genres_list"].isin(top_genres) & grp["production_countries_list"].isin(top_countries)]
    return alt.Chart(use).mark_rect().encode(
        x=alt.X("production_countries_list:N", title="Country"),
        y=alt.Y("genres_list:N", title="Genre"),
        color=alt.Color("med_roi:Q", title="Median ROI", scale=alt.Scale(scheme="reds")),
        tooltip=["genres_list", "production_countries_list", alt.Tooltip("med_roi", format=".2f"), alt.Tooltip("n", title="Count")],
    ).properties(height=26 * (use["genres_list"].nunique() if not use.empty else 6))


def chart_vote_dispersion_by_genre_errorbar(df: pd.DataFrame, top_k: int = 10, min_count: int = 20) -> alt.Chart:
    exploded = df.explode("genres_list").dropna(subset=["genres_list", "vote_average"])
    counts = exploded.groupby("genres_list").size().reset_index(name="n").sort_values("n", ascending=False)
    keep = counts[counts["n"] >= min_count].head(top_k)["genres_list"].tolist()
    sub = exploded[exploded["genres_list"].isin(keep)]
    agg = sub.groupby("genres_list").agg(mean=("vote_average", "mean"), std=("vote_average", "std")).reset_index()
    agg["lo"] = agg["mean"] - agg["std"].fillna(0)
    agg["hi"] = agg["mean"] + agg["std"].fillna(0)
    err = alt.Chart(agg).mark_errorbar().encode(
        y=alt.Y("genres_list:N", sort="-x", title="Genre"),
        x=alt.X("lo:Q", title="Rating"),
        x2="hi:Q",
    )
    pts = alt.Chart(agg).mark_point(color="#1f77b4", size=60).encode(
        y="genres_list:N", x=alt.X("mean:Q", title="Rating"),
        tooltip=["genres_list", alt.Tooltip("mean", title="Mean", format=".2f"), alt.Tooltip("std", title="Std Dev", format=".2f")],
    )
    return (err + pts).properties(height=28 * len(keep))


def chart_country_language_facet_bar(df: pd.DataFrame, metric: str = "roi", min_count: int = 10, top_c: int = 12, top_l: int = 8) -> alt.Chart:
    if "production_countries_list" not in df.columns or "original_language" not in df.columns:
        return alt.Chart(pd.DataFrame()).mark_bar()
    exploded = df.explode("production_countries_list").dropna(subset=["production_countries_list", "original_language"])
    grp = exploded.groupby(["production_countries_list", "original_language"]).agg(n=("id", "count"), v=(metric, "median")).reset_index()
    top_countries = grp.groupby("production_countries_list")["n"].sum().sort_values(ascending=False).head(top_c).index
    top_langs = grp.groupby("original_language")["n"].sum().sort_values(ascending=False).head(top_l).index
    use = grp[(grp["n"] >= min_count) & grp["production_countries_list"].isin(top_countries) & grp["original_language"].isin(top_langs)]
    bar = alt.Chart(use).mark_bar(color="#6baed6").encode(
        x=alt.X("v:Q", title="Median" if metric != "roi" else "Median ROI"),
        y=alt.Y("original_language:N", title="Language", sort="-x"),
        tooltip=["production_countries_list", "original_language", alt.Tooltip("v", format=".2f"), alt.Tooltip("n", title="Count")],
    )
    return bar.facet(row=alt.Row("production_countries_list:N", title="Country"))


 


def chart_month_seasonality_heat(df: pd.DataFrame, metric: str = "revenue") -> alt.Chart:
    if "release_date" not in df.columns:
        return alt.Chart(pd.DataFrame()).mark_rect()
    sub = df.dropna(subset=["release_date"]).copy()
    sub["month"] = sub["release_date"].dt.month
    sub["decade"] = (sub["release_date"].dt.year // 10 * 10).astype("Int64")
    y_col = metric if metric in sub.columns else "revenue"
    grp = sub.groupby(["decade", "month"]).agg(v=(y_col, "mean")).reset_index()
    title = "Average revenue" if y_col == "revenue" else "Average rating"
    return (
        alt.Chart(grp)
        .mark_rect()
        .encode(
            x=alt.X("month:O", title="Month"),
            y=alt.Y("decade:O", title="Decade"),
            color=alt.Color("v:Q", title=title, scale=alt.Scale(scheme="viridis")),
            tooltip=["decade", "month", alt.Tooltip("v", format=".2f")],
        )
        .properties(height=280)
    )


def chart_sequel_original_bar(df: pd.DataFrame, metric: str = "roi") -> alt.Chart:
    sub = df.copy()
    patt = re.compile(r"(\bPart\b|\bChapter\b|\bII\b|\bIII\b|\bIV\b|\bV\b|\bVI\b|\bVII\b|\bVIII\b|\bIX\b|\bX\b|\b2\b|\b3\b|\b4\b|\b5\b)", re.IGNORECASE)
    sub["tag"] = sub["title"].astype(str).apply(lambda s: "Sequel" if patt.search(s) else "Original")
    y_col = metric if metric in sub.columns else "roi"
    grp = sub.dropna(subset=[y_col]).groupby("tag").agg(med=("roi" if y_col == "roi" else y_col, "median"), n=("id", "count")).reset_index()
    return (
        alt.Chart(grp)
        .mark_bar()
        .encode(
            x=alt.X("tag:N", title="Category"),
            y=alt.Y("med:Q", title=("Median ROI" if y_col == "roi" else f"Median {y_col}")),
            color=alt.Color("tag:N", legend=None),
            tooltip=["tag", alt.Tooltip("med", format=".2f"), alt.Tooltip("n", title="Count")],
        )
        .properties(height=280)
    )


def chart_vote_count_stability_line(df: pd.DataFrame, bins: int = 6) -> alt.Chart:
    sub = df.dropna(subset=["vote_count", "vote_average"]).copy()
    if sub.empty:
        return alt.Chart(pd.DataFrame()).mark_line()
    q = pd.qcut(sub["vote_count"], q=min(bins, sub.shape[0]), duplicates="drop")
    agg = sub.assign(b=q.astype(str)).groupby("b").agg(mean=("vote_average", "mean"), std=("vote_average", "std")).reset_index()
    line = alt.Chart(agg).mark_line(point=True, color="#1f77b4").encode(x=alt.X("b:N", title="Vote count bins"), y=alt.Y("mean:Q", title="Mean rating"))
    band = alt.Chart(agg.assign(lo=agg["mean"] - agg["std"].fillna(0), hi=agg["mean"] + agg["std"].fillna(0))).mark_errorband(color="#aec7e8").encode(x="b:N", y="lo:Q", y2="hi:Q")
    return (band + line).properties(height=300)


def chart_roi_profile_compare(df: pd.DataFrame, k: int = 30) -> alt.Chart:
    sub = df.dropna(subset=["roi"]).copy().sort_values("roi", ascending=False)
    if sub.shape[0] < k * 2:
        k = max(1, sub.shape[0] // 2)
    top = sub.head(k)
    bot = sub.tail(k)
    metrics = ["budget", "revenue", "profit", "roi", "vote_average", "runtime", "popularity"]
    prof = pd.DataFrame({
        "group": ["TopK"] * len(metrics) + ["BottomK"] * len(metrics),
        "metric": metrics + metrics,
        "value": [top[m].mean() for m in metrics] + [bot[m].mean() for m in metrics],
    })
    return alt.Chart(prof).mark_bar().encode(
        x=alt.X("value:Q", title="Mean"),
        y=alt.Y("metric:N", sort="-x", title="Metric"),
        color=alt.Color("group:N", title="Group"),
        tooltip=["group", "metric", alt.Tooltip("value", format="~s")],
    ).properties(height=28 * len(metrics))


def chart_roi_profile_radar(df: pd.DataFrame, k: int = 30) -> alt.Chart:
    """Radar-like line chart: normalized curves for two groups across metrics"""
    sub = df.dropna(subset=["roi"]).copy().sort_values("roi", ascending=False)
    if sub.shape[0] < k * 2:
        k = max(1, sub.shape[0] // 2)
    top = sub.head(k)
    bot = sub.tail(k)
    metrics = ["budget", "revenue", "profit", "roi", "vote_average", "runtime", "popularity"]
    prof = pd.DataFrame({
        "group": ["TopK"] * len(metrics) + ["BottomK"] * len(metrics),
        "metric": metrics + metrics,
        "value": [top[m].mean() for m in metrics] + [bot[m].mean() for m in metrics],
    })
    # Normalize to 0-1 for comparison
    prof["norm"] = prof.groupby("metric")["value"].transform(lambda s: (s - s.min()) / (s.max() - s.min() + 1e-9))
    return (
        alt.Chart(prof)
        .mark_line(point=True)
        .encode(
            x=alt.X("metric:N", title="Metric"),
            y=alt.Y("norm:Q", title="Normalized value"),
            color=alt.Color("group:N", title="Group"),
            tooltip=["group", "metric", alt.Tooltip("value", format="~s"), alt.Tooltip("norm", format=".2f")],
        )
        .properties(height=320)
    )


def chart_vote_hist(df: pd.DataFrame) -> alt.Chart:
    """Histogram: rating distribution."""
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(x=alt.X("vote_average:Q", bin=alt.Bin(maxbins=20), title="Rating"), y="count()")
        .properties(height=280)
    )


def chart_year_trend(df: pd.DataFrame) -> alt.Chart:
    """Line chart: yearly trends of average rating and popularity."""
    yearly = (
        df.dropna(subset=["release_year"]).groupby("release_year")
        .agg(avg_vote=("vote_average", "mean"), avg_pop=("popularity", "mean"))
        .reset_index()
    )
    line1 = alt.Chart(yearly).mark_line(color="#1f77b4").encode(
        x=alt.X("release_year:O", title="Year"),
        y=alt.Y("avg_vote:Q", title="Average rating"),
        tooltip=["release_year", alt.Tooltip("avg_vote", format=".2f")],
    )
    line2 = (
        alt.Chart(yearly)
        .mark_line(color="#ff7f0e")
        .encode(x="release_year:O", y=alt.Y("avg_pop:Q", title="Average popularity"))
    )
    return alt.layer(line1, line2).resolve_scale(y="independent").properties(height=380)


def chart_runtime_box_by_genre(df: pd.DataFrame, top_k: int = 10) -> alt.Chart:
    """Box plot: runtime distribution of popular genres."""
    exploded = df.explode("genres_list")
    counts = exploded.groupby("genres_list").size().reset_index(name="n").sort_values("n", ascending=False)
    top_genres = counts.head(top_k)["genres_list"].tolist()
    sub = exploded[exploded["genres_list"].isin(top_genres)].dropna(subset=["runtime"])
    return (
        alt.Chart(sub)
        .mark_boxplot()
        .encode(
            x=alt.X("runtime:Q", title="Runtime (minutes)"),
            y=alt.Y("genres_list:N", sort="-x", title="Genre"),
            color=alt.value("#6baed6"),
        )
        .properties(height=30 * len(top_genres))
    )


def chart_corr_heatmap(df: pd.DataFrame) -> alt.Chart:
    """Heatmap: correlation among numerical features."""
    num_cols = [
        c for c in [
            "budget", "revenue", "runtime", "popularity", "vote_average", "vote_count", "profit", "roi"
        ] if c in df.columns
    ]
    if len(num_cols) < 2:
        return alt.Chart(pd.DataFrame({"x": [], "y": [], "corr": []})).mark_rect()
    corr = df[num_cols].corr().stack().rename("corr").reset_index().rename(columns={"level_0": "x", "level_1": "y"})
    return (
        alt.Chart(corr)
        .mark_rect()
        .encode(
            x=alt.X("x:N", title="Feature"), y=alt.Y("y:N", title="Feature"),
            color=alt.Color("corr:Q", scale=alt.Scale(scheme="redblue", domain=[-1, 1])),
            tooltip=["x", "y", alt.Tooltip("corr", format=".2f")],
        )
        .properties(height=280)
    )


