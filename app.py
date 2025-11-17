import os
from pathlib import Path

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SOPL 2025 - Partnership Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== GLOBAL PATHS ====================
APP_DIR = Path(__file__).parent
DEFAULT_CSV_PATH = APP_DIR / "data" / "SOPL 1002 Results - Raw.csv"

# ==================== LIGHT THEME + CSS ====================
st.markdown(
    """
<style>
/* Force light background everywhere */
html, body, .stApp {
    background-color: #ffffff !important;
}

/* Main view container */
[data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
}

/* Main block container */
main.block-container {
    background-color: #ffffff !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f9fafb !important;
}

/* Base tokens */
:root {
    --bg: #ffffff;
    --panel: #ffffff;
    --card: #ffffff;
    --muted: #64748b;
    --text: #020617;
    --accent: #3b308f;  /* Atlas "Minsk" */
    --success: #16a34a;
    --warning: #f59e0b;
    --danger: #ef4444;
    --glass: rgba(15,23,42,0.04);
}

/* Make sure ALL text is dark and readable on white */
.app-wrapper,
.app-wrapper * {
    color: #020617 !important;
}

/* Layout + typography */
.app-wrapper {
    background: var(--bg);
    padding: 18px 24px 40px 24px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.header-row {
    display:flex;
    align-items:flex-start;
    justify-content:space-between;
    gap:12px;
    margin-bottom: 16px;
}
.main-header {
    font-size: 1.9rem;
    font-weight: 800;
    margin: 0;
}
.sub-header {
    font-size: 0.95rem;
    color: var(--muted) !important;
    margin-top: 4px;
}

.section-header {
    font-size: 1.1rem;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 8px;
}

.chart-caption {
    font-size: 0.8rem;
    color: var(--muted) !important;
    margin-top: 4px;
}

.card {
    background: var(--panel);
    border-radius: 10px;
    padding: 12px 14px;
    border: 1px solid rgba(148,163,184,0.4);
}

/* Widget polish */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: 8px;
    border-color: #d4d4d8;
}

.stTabs [data-baseweb="tab"] {
    font-size: 0.9rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==================== ALTAIR LIGHT THEME ====================
def atlas_light_theme():
    return {
        "config": {
            "view": {"stroke": "transparent"},
            "background": "#ffffff",
            "range": {
                "category": ["#3b308f", "#64748b", "#93c5fd", "#1d4ed8", "#0f766e"]
            },
            "axis": {
                "labelColor": "#475569",
                "titleColor": "#020617",
                "titleFontWeight": 600,
                "gridColor": "#e5e7eb",
                "domainColor": "#d4d4d8",
            },
            "legend": {
                "labelColor": "#475569",
                "titleColor": "#020617",
                "titleFontWeight": 600,
            },
            "title": {
                "color": "#020617",
                "fontSize": 16,
                "fontWeight": 700,
                "anchor": "start",
            },
        }
    }

alt.themes.register("atlas_light", atlas_light_theme)
alt.themes.enable("atlas_light")

# ==================== HELPERS ====================
@st.cache_data(show_spinner=False)
def load_data(uploaded_file, encoding_choice: str = "auto") -> pd.DataFrame:
    """
    Load SOPL data either from an uploaded file or from the bundled CSV.
    Tries cp1252 first (Qualtrics-style export), then a few common encodings.
    """
    encodings = ["cp1252", "utf-8-sig", "utf-8", "latin-1"]

    def _read_any(path_or_buf):
        buf = path_or_buf
        tried = []
        for enc in (encodings if encoding_choice == "auto" else [encoding_choice]):
            try:
                return pd.read_csv(buf, encoding=enc)
            except Exception as e:
                tried.append(f"{enc}: {e}")
                continue
        raise RuntimeError("All decode attempts failed:\n" + "\n".join(tried))

    # 1) Uploaded
    if uploaded_file is not None:
        name = (uploaded_file.name or "").lower()
        if name.endswith((".xlsx", ".xls")):
            try:
                return pd.read_excel(uploaded_file)
            except Exception:
                pass
        try:
            return _read_any(uploaded_file)
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")
            return pd.DataFrame()

    # 2) Fallback to repo CSV
    if DEFAULT_CSV_PATH.exists():
        try:
            return _read_any(str(DEFAULT_CSV_PATH))
        except Exception as e:
            st.error(
                f"Bundled SOPL CSV found at {DEFAULT_CSV_PATH} but could not be read: {e}"
            )
            return pd.DataFrame()

    st.error(
        "No data available. Upload a SOPL CSV/XLSX, or ensure the default CSV is packaged at /data/SOPL 1002 Results - Raw.csv."
    )
    return pd.DataFrame()


def value_counts_pct(series: pd.Series) -> pd.DataFrame:
    """Return a DataFrame with category + percentage (0–100) for non-null responses."""
    s = series.dropna()
    if s.empty:
        return pd.DataFrame(columns=["category", "pct"])
    counts = s.value_counts()
    pct = (counts / counts.sum()) * 100.0
    out = pct.reset_index()
    out.columns = ["category", "pct"]
    return out


def multi_select_pct(df: pd.DataFrame, col_prefix: str = None, contains_substring: str = None) -> pd.DataFrame:
    """
    For Qualtrics-style multi-select (one column per option with 1/0/NaN),
    compute share of respondents selecting each option.
    """
    if col_prefix:
        cols = [c for c in df.columns if c.startswith(col_prefix)]
    elif contains_substring:
        cols = [c for c in df.columns if contains_substring in c]
    else:
        return pd.DataFrame(columns=["option", "pct"])

    if not cols:
        return pd.DataFrame(columns=["option", "pct"])

    n = len(df)
    rows = []
    for c in cols:
        col = df[c]
        selected = ((col == 1) | (col == 1.0) | (col == True)).sum()
        pct = (selected / n * 100.0) if n > 0 else 0.0
        label = c.split("_", 1)[1] if "_" in c else c
        rows.append({"option": label, "pct": pct})

    out = pd.DataFrame(rows)
    out = out.sort_values("pct", ascending=False)
    return out


def create_section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def bar_chart_from_pct(df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str, horizontal: bool = True):
    if df_pct.empty:
        st.info("No responses for this question in the current filter.")
        return

    data = df_pct.copy()
    data[cat_field] = data[cat_field].astype(str)

    if horizontal:
        chart = (
            alt.Chart(data)
            .mark_bar()
            .encode(
                x=alt.X(
                    f"{pct_field}:Q",
                    title="Share of respondents (%)",
                    axis=alt.Axis(format=".0f"),
                ),
                y=alt.Y(f"{cat_field}:N", sort="-x", title=None),
                color=alt.value("#3b308f"),
                tooltip=[
                    alt.Tooltip(f"{cat_field}:N", title="Category"),
                    alt.Tooltip(f"{pct_field}:Q", title="Share (%)", format=".1f"),
                ],
            )
            .properties(height=max(220, 26 * len(data)), title=title)
            .interactive()
        )
    else:
        chart = (
            alt.Chart(data)
            .mark_bar()
            .encode(
                x=alt.X(f"{cat_field}:N", sort="-y", title=None),
                y=alt.Y(
                    f"{pct_field}:Q",
                    title="Share of respondents (%)",
                    axis=alt.Axis(format=".0f"),
                ),
                color=alt.value("#3b308f"),
                tooltip=[
                    alt.Tooltip(f"{cat_field}:N", title="Category"),
                    alt.Tooltip(f"{pct_field}:Q", title="Share (%)", format=".1f"),
                ],
            )
            .properties(height=360, title=title)
            .interactive()
        )

    st.altair_chart(chart, use_container_width=True)


def donut_chart_from_pct(df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str):
    if df_pct.empty:
        st.info("No responses for this question in the current filter.")
        return

    data = df_pct.copy()
    data[cat_field] = data[cat_field].astype(str)

    chart = (
        alt.Chart(data)
        .mark_arc(innerRadius=70)
        .encode(
            theta=alt.Theta(f"{pct_field}:Q", stack=True),
            color=alt.Color(f"{cat_field}:N", legend=alt.Legend(title=None)),
            tooltip=[
                alt.Tooltip(f"{cat_field}:N", title="Category"),
                alt.Tooltip(f"{pct_field}:Q", title="Share (%)", format=".1f"),
            ],
        )
        .properties(width=360, height=360, title=title)
        .interactive()
    )

    st.altair_chart(chart, use_container_width=True)


def win_rate_distribution_pct(df: pd.DataFrame, col: str):
    series = df[col].dropna()
    if series.empty:
        st.info("No win-rate responses in the current filter.")
        return

    # Bin into 0–10, 10–20, ..., 90–100
    bins = list(range(0, 101, 10))
    labels = [f"{b}–{b+10}%" for b in bins[:-1]]
    binned = pd.cut(series, bins=bins, labels=labels, include_lowest=True, right=False)
    pct_df = value_counts_pct(binned)
    pct_df = pct_df.rename(columns={"category": "bin", "pct": "pct"})

    bar_chart_from_pct(
        pct_df,
        "bin",
        "pct",
        "Win rate distribution (10-point bands)",
        horizontal=False,
    )
    st.markdown(
        '<div class="chart-caption">Percentages are based on respondents who answered the win-rate question.</div>',
        unsafe_allow_html=True,
    )


# ==================== MAIN APP ====================
def main():
    st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)

    # ---- Header ----
    st.markdown(
        """
<div class="header-row">
  <div>
    <div class="main-header">SOPL 2025 Insights Platform</div>
    <div class="sub-header">Partnership analytics and strategic insights - SOPL</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    # ---- Data upload (optional) ----
    with st.expander("Upload Data (optional)", expanded=False):
        uploaded = st.file_uploader(
            "Upload SOPL Data",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
        )
        encoding_choice = st.selectbox(
            "Encoding (auto will try cp1252, utf-8-sig, utf-8, latin-1)",
            options=["auto", "cp1252", "utf-8-sig", "utf-8", "latin-1"],
            index=0,
        )
        st.caption(
            "If you don't upload anything, the dashboard will use the bundled SOPL CSV "
            "packaged with the app (data/SOPL 1002 Results - Raw.csv)."
        )

    df = load_data(uploaded, encoding_choice)

    if df.empty:
        st.stop()

    # Column names used in the dashboard
    COL_REGION = "Please select the region where your company is headquartered."
    COL_INDUSTRY = "What industry sector does your company operate in?"
    COL_REVENUE = "What is your company’s estimated annual revenue?"
    COL_EMPLOYEES = "What is your company’s total number of employees?"
    COL_DEAL_SIZE = "How does your average deal size involving partners compare to direct or non-partner deals?"
    COL_CAC = "How does your customer acquisition cost (CAC) from partners compared to direct sales and marketing?"
    COL_SALES_CYCLE = "How does your partner-led sales cycle compare to your direct sales cycle?"
    COL_WIN_RATE = "What’s your win rate for deals where partners are involved?"

    # ---- Sidebar filters: Region, Revenue, Employees ----
    st.sidebar.header("Filters")

    # Region filter
    if COL_REGION in df.columns:
        region_options = sorted(df[COL_REGION].dropna().unique().tolist())
        selected_regions = st.sidebar.multiselect(
            "Region (HQ)",
            options=region_options,
            default=region_options,
        )
    else:
        selected_regions = None

    # Revenue filter
    if COL_REVENUE in df.columns:
        revenue_options = df[COL_REVENUE].dropna().unique().tolist()
        revenue_order = [
            "Less than $50 million",
            "$50M – $250M",
            "$250M – $1B",
            "$1B – $10B",
            "More than $10B",
        ]
        ordered_revenue = [r for r in revenue_order if r in revenue_options] + [
            r for r in revenue_options if r not in revenue_order
        ]
        selected_revenue = st.sidebar.multiselect(
            "Annual revenue band",
            options=ordered_revenue,
            default=ordered_revenue,
        )
    else:
        selected_revenue = None

    # Employee-count filter
    if COL_EMPLOYEES in df.columns:
        emp_options = df[COL_EMPLOYEES].dropna().unique().tolist()
        emp_order = [
            "Less than 100 employees",
            "100 – 500 employees",
            "501 – 5,000 employees",
            "More than 5,000 employees",
        ]
        ordered_emp = [e for e in emp_order if e in emp_options] + [
            e for e in emp_options if e not in emp_order
        ]
        selected_employees = st.sidebar.multiselect(
            "Total employees",
            options=ordered_emp,
            default=ordered_emp,
        )
    else:
        selected_employees = None

    # Apply filters
    flt = df.copy()
    if selected_regions:
        flt = flt[flt[COL_REGION].isin(selected_regions)]
    if selected_revenue:
        flt = flt[flt[COL_REVENUE].isin(selected_revenue)]
    if selected_employees:
        flt = flt[flt[COL_EMPLOYEES].isin(selected_employees)]

    st.caption(f"Responses in current view: {len(flt)}")

    # ---- Tabs ----
    tab_overview, tab_performance, tab_geo, tab_multi, tab_data = st.tabs(
        ["Overview", "Performance", "Geography", "Partner & Impact", "Data"]
    )

    # ===== Overview tab =====
    with tab_overview:
        create_section_header("Company profile (percentage breakdown)")

        # Bigger charts: 2 columns instead of 3
        c1, c2 = st.columns(2)

        with c1:
            if COL_REGION in flt.columns:
                region_pct = value_counts_pct(flt[COL_REGION])
                donut_chart_from_pct(
                    region_pct, "category", "pct", "Region (HQ) share of respondents"
                )
                st.markdown(
                    '<div class="chart-caption">Percentages are based on respondents who selected a region.</div>',
                    unsafe_allow_html=True,
                )

        with c2:
            if COL_REVENUE in flt.columns:
                rev_pct = value_counts_pct(flt[COL_REVENUE])
                order = [
                    "Less than $50 million",
                    "$50M – $250M",
                    "$250M – $1B",
                    "$1B – $10B",
                    "More than $10B",
                ]
                rev_pct["category"] = pd.Categorical(
                    rev_pct["category"], categories=order, ordered=True
                )
                rev_pct = rev_pct.sort_values("category")
                bar_chart_from_pct(
                    rev_pct,
                    "category",
                    "pct",
                    "Annual revenue band (share of respondents)",
                    horizontal=True,
                )
                st.markdown(
                    '<div class="chart-caption">Percentages are based on respondents who answered the revenue question.</div>',
                    unsafe_allow_html=True,
                )

        c3, c4 = st.columns(2)

        with c3:
            if COL_EMPLOYEES in flt.columns:
                emp_pct = value_counts_pct(flt[COL_EMPLOYEES])
                emp_order = [
                    "Less than 100 employees",
                    "100 – 500 employees",
                    "501 – 5,000 employees",
                    "More than 5,000 employees",
                ]
                emp_pct["category"] = pd.Categorical(
                    emp_pct["category"], categories=emp_order, ordered=True
                )
                emp_pct = emp_pct.sort_values("category")
                bar_chart_from_pct(
                    emp_pct,
                    "category",
                    "pct",
                    "Company size (employees)",
                    horizontal=True,
                )
                st.markdown(
                    '<div class="chart-caption">Percentages are based on respondents who answered the employee-count question.</div>',
                    unsafe_allow_html=True,
                )

        with c4:
            if COL_INDUSTRY in flt.columns:
                ind_pct = value_counts_pct(flt[COL_INDUSTRY])
                bar_chart_from_pct(
                    ind_pct,
                    "category",
                    "pct",
                    "Industry sector (share of respondents)",
                    horizontal=True,
                )
                st.markdown(
                    '<div class="chart-caption">Each bar shows the percentage of respondents in that industry.</div>',
                    unsafe_allow_html=True,
                )

    # ===== Performance tab =====
    with tab_performance:
        create_section_header("Deal performance vs direct motion")

        p1, p2 = st.columns(2)

        with p1:
            if COL_DEAL_SIZE in flt.columns:
                ds_pct = value_counts_pct(flt[COL_DEAL_SIZE])
                bar_chart_from_pct(
                    ds_pct,
                    "category",
                    "pct",
                    "Average deal size: partner vs direct",
                    horizontal=True,
                )
                st.markdown(
                    '<div class="chart-caption">Percentages are based on respondents who answered the deal-size comparison.</div>',
                    unsafe_allow_html=True,
                )

        with p2:
            if COL_CAC in flt.columns:
                cac_pct = value_counts_pct(flt[COL_CAC])
                bar_chart_from_pct(
                    cac_pct,
                    "category",
                    "pct",
                    "Partner-sourced CAC vs direct",
                    horizontal=True,
                )
                st.markdown(
                    '<div class="chart-caption">Percentages are based on respondents who answered the CAC comparison.</div>',
                    unsafe_allow_html=True,
                )

        create_section_header("Sales cycle & win rate")

        p3, p4 = st.columns(2)

        with p3:
            if COL_SALES_CYCLE in flt.columns:
                sc_pct = value_counts_pct(flt[COL_SALES_CYCLE])
                bar_chart_from_pct(
                    sc_pct,
                    "category",
                    "pct",
                    "Partner-led sales cycle vs direct",
                    horizontal=True,
                )
                st.markdown(
                    '<div class="chart-caption">Percentages are based on respondents who answered the sales-cycle comparison.</div>',
                    unsafe_allow_html=True,
                )

        with p4:
            if COL_WIN_RATE in flt.columns:
                win_rate_distribution_pct(flt, COL_WIN_RATE)

    # ===== Geography tab =====
    with tab_geo:
        create_section_header("Regional distribution (percentages)")

        if COL_REGION in flt.columns:
            region_pct = value_counts_pct(flt[COL_REGION])

            g1, g2 = st.columns(2)

            with g1:
                donut_chart_from_pct(
                    region_pct,
                    "category",
                    "pct",
                    "Region share of respondents",
                )

            with g2:
                bar_chart_from_pct(
                    region_pct,
                    "category",
                    "pct",
                    "Region share (bar view)",
                    horizontal=True,
                )

            st.markdown(
                '<div class="chart-caption">Percentages are relative to all respondents in the current filter.</div>',
                unsafe_allow_html=True,
            )

            # --- Map view (using percentages) ---
            create_section_header("Regional map (bubble size = share of respondents)")

            # Map basic region names to lat/lon
            region_coords = {
                "North America": (40.0, -100.0),
                "Latin America": (-20.0, -60.0),
                "Europe": (50.0, 10.0),
                "Asia Pacific": (20.0, 100.0),
                "Asia-Pacific": (20.0, 100.0),
                "APAC": (20.0, 100.0),
            }

            map_df = region_pct.copy()
            map_df["lat"] = map_df["category"].map(lambda r: region_coords.get(r, (None, None))[0])
            map_df["lon"] = map_df["category"].map(lambda r: region_coords.get(r, (None, None))[1])
            map_df = map_df.dropna(subset=["lat", "lon"])

            if not map_df.empty:
                # Radius scaled by percentage
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    map_df,
                    get_position=["lon", "lat"],
                    get_radius="pct * 120000",  # tune for visual balance
                    get_fill_color=[59, 48, 143, 180],
                    pickable=True,
                )

                view_state = pdk.ViewState(
                    latitude=20,
                    longitude=0,
                    zoom=1,
                    pitch=0,
                )

                deck = pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={"text": "{category}\nShare: {pct}%"},
                )
                st.pydeck_chart(deck)
                st.markdown(
                    '<div class="chart-caption">Bubble size reflects the percentage share of respondents in each region, not raw counts.</div>',
                    unsafe_allow_html=True,
                )

        # Region x Revenue (within-region %)
        if COL_REGION in flt.columns and COL_REVENUE in flt.columns:
            create_section_header("Revenue bands by region (within-region share)")

            tmp = flt[[COL_REGION, COL_REVENUE]].dropna()
            if not tmp.empty:
                total_by_region = (
                    tmp.groupby(COL_REGION)[COL_REVENUE]
                    .count()
                    .rename("total")
                )
                cross = (
                    tmp.groupby([COL_REGION, COL_REVENUE])[COL_REVENUE]
                    .count()
                    .rename("count")
                    .reset_index()
                )
                cross = cross.merge(total_by_region, on=COL_REGION, how="left")
                cross["pct"] = cross["count"] / cross["total"] * 100.0

                chart = (
                    alt.Chart(cross)
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "pct:Q",
                            title="Share within region (%)",
                            axis=alt.Axis(format=".0f"),
                        ),
                        y=alt.Y(f"{COL_REGION}:N", title=None),
                        color=alt.Color(f"{COL_REVENUE}:N", title="Revenue band"),
                        tooltip=[
                            alt.Tooltip(f"{COL_REGION}:N", title="Region"),
                            alt.Tooltip(f"{COL_REVENUE}:N", title="Revenue band"),
                            alt.Tooltip("pct:Q", title="Share (%)", format=".1f"),
                        ],
                    )
                    .properties(height=340)
                    .interactive()
                )
                st.altair_chart(chart, use_container_width=True)
                st.markdown(
                    '<div class="chart-caption">Within each region, bars show how respondents are distributed across revenue bands (percentages sum to ~100% per region).</div>',
                    unsafe_allow_html=True,
                )

    # ===== Partner & Impact tab =====
    with tab_multi:
        create_section_header("How influence is measured (beyond sourced revenue)")

        influence_prefix = (
            "Besides Sourced Revenue, how else does your company measure partner influence impact?"
        )
        infl_pct = multi_select_pct(flt, col_prefix=influence_prefix)
        if not infl_pct.empty:
            bar_chart_from_pct(
                infl_pct,
                "option",
                "pct",
                "Share of companies using each influence metric",
                horizontal=True,
            )
            st.markdown(
                '<div class="chart-caption">Percentages are based on all respondents in the current filter; each company can select multiple metrics.</div>',
                unsafe_allow_html=True,
            )

        create_section_header("Partnership types in place today")

        types_substr = "Which of the following Partnership types does your company hav"
        types_pct = multi_select_pct(flt, contains_substring=types_substr)
        if not types_pct.empty:
            bar_chart_from_pct(
                types_pct,
                "option",
                "pct",
                "Share of companies with each partnership type",
                horizontal=True,
            )
            st.markdown(
                '<div class="chart-caption">Percentages are based on all respondents in the current filter; each company can select multiple partnership types.</div>',
                unsafe_allow_html=True,
            )

    # ===== Data tab =====
    with tab_data:
        create_section_header("Filtered data")

        cols_available = flt.columns.tolist()
        default_cols = [
            COL_REGION,
            COL_INDUSTRY,
            COL_REVENUE,
            COL_EMPLOYEES,
            COL_DEAL_SIZE,
            COL_CAC,
            COL_SALES_CYCLE,
            COL_WIN_RATE,
        ]
        default_cols = [c for c in default_cols if c in cols_available]

        selected_cols = st.multiselect(
            "Columns to display",
            options=cols_available,
            default=default_cols if default_cols else cols_available[:8],
        )

        st.dataframe(flt[selected_cols], use_container_width=True)

    # ---- Footer ----
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#64748b !important; font-size:0.85rem;'>"
        "SOPL 2025 Insights Platform • Partnership analytics and strategic insights"
        "</div>",
        unsafe_allow_html=True,
    )

    # ===== Embedded Pickaxe assistant (always visible, large) =====
    st.markdown("## Assistant (SOPL Q&A)")
    st.markdown(
        "<div class='chart-caption'>Use this assistant to ask questions about what you're seeing in the dashboard.</div>",
        unsafe_allow_html=True,
    )
    pickaxe_html = """
<div id="deployment-5870ff7d-8fcf-4395-976b-9e9fdefbb0ff" style="width:100%; max-width:1200px; margin:0 auto;"></div>
<script src="https://studio.pickaxe.co/api/embed/bundle.js" defer></script>
"""
    components.html(pickaxe_html, height=650, scrolling=True)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
