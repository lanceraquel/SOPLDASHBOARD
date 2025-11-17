import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SOPL 2025 - Partnership Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== CSS / LIGHT THEME ====================
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
html, body, .stApp, .stApp * {
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

/* MAIN TITLE – Amaranth & bigger */
.main-header {
    font-size: 2.6rem;
    font-weight: 900;
    margin: 0;
    color: #ec3d72 !important;      /* Amaranth */
    letter-spacing: -0.5px;
}
.main-header::after {
    content: "";
    display: block;
    width: 58px;
    height: 4px;
    background: #ec3d72;
    border-radius: 3px;
    margin-top: 6px;
}

/* Subtitle */
.sub-header {
    font-size: 1.15rem;
    color: #64748b !important;
    margin-top: 6px;
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

/* Vega/Altair actions menu (export, fullscreen) – light theme */
.vega-embed .vega-actions {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #020617 !important;
    border-radius: 6px !important;
    box-shadow: 0 4px 12px rgba(15,23,42,0.18);
    padding: 4px 8px !important;
}
.vega-embed .vega-actions a {
    color: #020617 !important;
    font-weight: 500 !important;
}

/* Fix fullscreen / menu icon color */
.vega-embed details > summary svg {
    stroke: #020617 !important;
    fill: #020617 !important;
}
.vega-embed details {
    color: #020617 !important;
}
.vega-embed details > summary {
    background-color:#ffffff !important;
    border-radius:50% !important;
    border:1px solid #e2e8f0 !important;
}
.vega-embed details[open] > summary {
    box-shadow:0 2px 6px rgba(15,23,42,0.2);
}

/* Make axis labels more likely to show fully */
.vega-embed text {
    font-size: 11px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ==================== ALTAIR LIGHT THEME & EXPORT ====================
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
                "labelLimit": 260,
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

# Allow PNG/SVG export from the Altair menu
alt.data_transformers.disable_max_rows()
alt.renderers.set_embed_options(
    actions={"export": True, "source": False, "compiled": False, "editor": False}
)

# ==================== GOOGLE SHEETS LOADER ====================
@st.cache_data(show_spinner=True)
def load_data() -> pd.DataFrame:
    """
    Load SOPL data from Google Sheets using st.secrets["gsheet_url"].
    """
    url = st.secrets.get("gsheet_url", None)
    if not url:
        st.error(
            "❌ Missing gsheet_url in Streamlit secrets. "
            "Add it in your app settings as `gsheet_url = \"...\"`."
        )
        return pd.DataFrame()

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    for enc in encodings:
        try:
            df = pd.read_csv(url, encoding=enc)
            return df
        except Exception:
            continue

    st.error("❌ Could not load Google Sheet. Check the export URL and sharing settings.")
    return pd.DataFrame()

# ==================== HELPERS ====================
def value_counts_pct(series: pd.Series) -> pd.DataFrame:
    """
    Return a DataFrame with category + percentage (0–100) for non-null responses.
    % = count(category) / total_non_null * 100.
    """
    s = series.dropna()
    if s.empty:
        return pd.DataFrame(columns=["category", "pct"])
    counts = s.value_counts()
    pct = (counts / counts.sum()) * 100.0
    out = pct.reset_index()
    out.columns = ["category", "pct"]
    return out


def multi_select_pct(
    df: pd.DataFrame, col_prefix: str | None = None, contains_substring: str | None = None
) -> pd.DataFrame:
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


def donut_chart_with_labels(df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str):
    """Donut with % labels on slices (no axes)."""
    if df_pct.empty:
        st.info("No responses for this question in the current filter.")
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)
    data["PercentLabel"] = data["Percent"].map(lambda v: f"{v:.1f}%")

    base = alt.Chart(data).encode(
        theta=alt.Theta("Percent:Q", stack=True),
        color=alt.Color(f"{cat_field}:N", legend=alt.Legend(title=None)),
    )

    donut = base.mark_arc(innerRadius=70)
    text = base.mark_text(radius=110, size=13, color="#020617").encode(
        text=alt.Text("PercentLabel:N")
    )

    chart = (donut + text).properties(
        width=380,
        height=380,
        title=title,
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


def bar_chart_from_pct(
    df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str, horizontal: bool = True
):
    """Bar chart with % labels on bars."""
    if df_pct.empty:
        st.info("No responses for this question in the current filter.")
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)
    data["PercentLabel"] = data["Percent"].map(lambda v: f"{v:.1f}%")

    if horizontal:
        base = alt.Chart(data).encode(
            x=alt.X(
                "Percent:Q",
                title="Share of respondents (%)",
                axis=alt.Axis(format=".0f"),
            ),
            y=alt.Y(
                f"{cat_field}:N",
                sort="-x",
                title=None,
                axis=alt.Axis(labelLimit=260, labelOverlap=False),
            ),
        )

        bars = base.mark_bar(color="#3b308f")
        labels = base.mark_text(
            align="left", baseline="middle", dx=4, color="#020617"
        ).encode(text=alt.Text("PercentLabel:N"))

        chart = (bars + labels).properties(
            height=max(260, 30 * len(data)),
            title=title,
        ).interactive()
    else:
        base = alt.Chart(data).encode(
            x=alt.X(
                f"{cat_field}:N",
                sort="-y",
                title=None,
                axis=alt.Axis(labelLimit=260, labelOverlap=False),
            ),
            y=alt.Y(
                "Percent:Q",
                title="Share of respondents (%)",
                axis=alt.Axis(format=".0f"),
            ),
        )
        bars = base.mark_bar(color="#3b308f")
        labels = base.mark_text(
            align="center", baseline="bottom", dy=-4, color="#020617"
        ).encode(text=alt.Text("PercentLabel:N"))

        chart = (bars + labels).properties(
            height=380,
            title=title,
        ).interactive()

    st.altair_chart(chart, use_container_width=True)


def win_rate_distribution_pct(df: pd.DataFrame, col: str):
    series = df[col].dropna()
    if series.empty:
        st.info("No win-rate responses in the current filter.")
        return

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


def normalize_region_label(x):
    """Standardize region labels for mapping & aggregation."""
    if pd.isna(x):
        return None
    s = str(x)
    if "North America" in s:
        return "North America"
    if "Latin America" in s:
        return "Latin America"
    if "Asia-Pacific" in s or "Asia Pacific" in s or "APAC" in s:
        return "Asia Pacific"
    if "Europe" in s or "EMEA" in s:
        return "Europe"
    return s


def kpi_value_str(pct: float | None) -> str:
    if pct is None:
        return "—"
    return f"{pct:.1f}%"


def kpi_card(title: str, value: str, subtitle: str | None = None, accent: bool = False):
    """Nice-looking KPI card for execs."""
    border_color = "#ec3d72" if accent else "#e2e8f0"
    html = f"""
<div style="
    background:#ffffff;
    border-radius:12px;
    padding:12px 14px;
    border:1px solid #e2e8f0;
    border-top:3px solid {border_color};
    box-shadow:0 4px 12px rgba(15,23,42,0.04);
    min-height:96px;
">
  <div style="font-size:0.78rem; letter-spacing:0.06em; text-transform:uppercase;
              color:#64748b; font-weight:600; margin-bottom:4px;">
    {title}
  </div>
  <div style="font-size:1.8rem; font-weight:700; color:#020617; margin-bottom:2px; word-break:break-word;">
    {value}
  </div>
  {f'<div style="font-size:0.85rem; color:#64748b;">{subtitle}</div>' if subtitle else ''}
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


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

    df = load_data()
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

    # Normalized region
    if COL_REGION in df.columns:
        df = df.copy()
        df["RegionStd"] = df[COL_REGION].map(normalize_region_label)
    else:
        df["RegionStd"] = None

    # ---- Sidebar filters: Region, Revenue, Employees ----
    st.sidebar.header("Filters")

    # Region filter
    if "RegionStd" in df.columns:
        region_options = sorted(df["RegionStd"].dropna().unique().tolist())
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
        flt = flt[flt["RegionStd"].isin(selected_regions)]
    if selected_revenue:
        flt = flt[flt[COL_REVENUE].isin(selected_revenue)]
    if selected_employees:
        flt = flt[flt[COL_EMPLOYEES].isin(selected_employees)]

    # ---- Tabs ----
    tab_overview, tab_performance, tab_geo, tab_multi, tab_data = st.tabs(
        ["Overview", "Performance", "Geography", "Partner & Impact", "Data"]
    )

    # ======================================================
    # TAB 0 – EXECUTIVE SUMMARY (KPI CARDS + NARRATIVE)
    # ======================================================
    with tab_overview:
        create_section_header("Executive summary")

        # Top industry
        top_industry_name = None
        top_industry_pct = None
        if COL_INDUSTRY in flt.columns and not flt[COL_INDUSTRY].dropna().empty:
            ind_pct = value_counts_pct(flt[COL_INDUSTRY])
            ind_pct = ind_pct.sort_values("pct", ascending=False)
            if not ind_pct.empty:
                top_industry_name = str(ind_pct.iloc[0]["category"])
                top_industry_pct = float(ind_pct.iloc[0]["pct"])

        # Top region
        top_region_name = None
        top_region_pct = None
        if "RegionStd" in flt.columns and not flt["RegionStd"].dropna().empty:
            reg_pct = value_counts_pct(flt["RegionStd"])
            reg_pct = reg_pct.sort_values("pct", ascending=False)
            if not reg_pct.empty:
                top_region_name = str(reg_pct.iloc[0]["category"])
                top_region_pct = float(reg_pct.iloc[0]["pct"])

        # Larger companies (>= 501 employees)
        large_emp_pct = None
        if COL_EMPLOYEES in flt.columns:
            emp_series = flt[COL_EMPLOYEES].dropna().astype(str)
            if not emp_series.empty:
                mask_large = emp_series.str.contains("5,000", na=False) | emp_series.str.contains(
                    "501", na=False
                )
                large_count = mask_large.sum()
                large_emp_pct = (large_count / len(emp_series)) * 100.0 if len(emp_series) > 0 else None

        # Deal size higher than direct
        higher_deal_pct = None
        if COL_DEAL_SIZE in flt.columns:
            ds = flt[COL_DEAL_SIZE].dropna().astype(str)
            if not ds.empty:
                mask_high = ds.str.contains("Higher than direct deals", case=False, na=False)
                higher_deal_pct = (mask_high.sum() / len(ds)) * 100.0 if len(ds) > 0 else None

        # CAC lower than direct
        lower_cac_pct = None
        if COL_CAC in flt.columns:
            cac = flt[COL_CAC].dropna().astype(str)
            if not cac.empty:
                mask_low = cac.str.contains("Lower", case=False, na=False)
                lower_cac_pct = (mask_low.sum() / len(cac)) * 100.0 if len(cac) > 0 else None

        # Median win rate
        median_win_rate = None
        if COL_WIN_RATE in flt.columns:
            wr = pd.to_numeric(flt[COL_WIN_RATE], errors="coerce").dropna()
            if not wr.empty:
                median_win_rate = float(wr.median())

        # KPI cards (no ellipsis, richer styling)
        row1 = st.columns(4)
        with row1[0]:
            kpi_card(
                "Top industry by respondents",
                top_industry_name or "—",
                subtitle=f"Share of respondents: {top_industry_pct:.1f}%" if top_industry_pct is not None else None,
                accent=True,
            )
        with row1[1]:
            kpi_card(
                "Top HQ region",
                top_region_name or "—",
                subtitle=f"Share of respondents: {top_region_pct:.1f}%" if top_region_pct is not None else None,
            )
        with row1[2]:
            kpi_card(
                "Larger companies (≈500+ employees)",
                kpi_value_str(large_emp_pct),
                subtitle="Based on 501–5,000 and 5,000+ employee bins.",
            )
        with row1[3]:
            kpi_card(
                "Median partner-involved win rate",
                f"{median_win_rate:.1f}%" if median_win_rate is not None else "—",
            )

        row2 = st.columns(2)
        with row2[0]:
            kpi_card(
                "Deal size: partners > direct",
                kpi_value_str(higher_deal_pct),
                subtitle="Companies reporting larger partner-involved deals vs direct.",
            )
        with row2[1]:
            kpi_card(
                "CAC lower with partners",
                kpi_value_str(lower_cac_pct),
                subtitle="Companies reporting lower CAC from partner motions vs direct.",
            )

    # ======================================================
    # TAB 1 – OVERVIEW
    # ======================================================
    with tab_overview:
        create_section_header("Company profile (percentage breakdown)")

        c1, c2 = st.columns(2)

        with c1:
            if "RegionStd" in flt.columns:
                region_pct = value_counts_pct(flt["RegionStd"])
                donut_chart_with_labels(
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

    # ======================================================
    # TAB 2 – PERFORMANCE
    # ======================================================
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

    # ======================================================
    # TAB 3 – GEOGRAPHY
    # ======================================================
    with tab_geo:
        create_section_header("Regional distribution (percentages)")

        if "RegionStd" in flt.columns:
            region_pct = value_counts_pct(flt["RegionStd"])

            g1, g2 = st.columns(2)

            with g1:
                donut_chart_with_labels(
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

            # --- Map with bubbles sized by % ---
            create_section_header("Regional map (bubble size = share of respondents)")

            region_coords = {
                "North America": (40.0, -100.0),
                "Latin America": (-20.0, -60.0),
                "Europe": (50.0, 10.0),
                "Asia Pacific": (20.0, 100.0),
            }

            map_df = region_pct.rename(columns={"category": "region"}).copy()
            # Add the fields pydeck actually uses
            map_df["Percent"] = map_df["pct"]
            map_df["PercentLabel"] = map_df["Percent"].map(lambda v: f"{v:.1f}%")
            map_df["lat"] = map_df["region"].map(
                lambda r: region_coords.get(r, (None, None))[0]
            )
            map_df["lon"] = map_df["region"].map(
                lambda r: region_coords.get(r, (None, None))[1]
            )
            map_df = map_df.dropna(subset=["lat", "lon"])

            if not map_df.empty:
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    map_df,
                    get_position=["lon", "lat"],
                    get_radius="Percent * 400000",
                    radius_min_pixels=8,
                    radius_max_pixels=60,
                    get_fill_color=[59, 48, 143, 210],
                    get_line_color=[255, 255, 255, 230],
                    line_width_min_pixels=1,
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
                    tooltip={"text": "{region}\nShare: {PercentLabel}"},
                )
                st.pydeck_chart(deck)
                st.markdown(
                    '<div class="chart-caption">Bubble size reflects the percentage share of respondents in each region, not raw counts.</div>',
                    unsafe_allow_html=True,
                )

    # ======================================================
    # TAB 4 – PARTNER & IMPACT
    # ======================================================
    with tab_multi:
        create_section_header("How influence is measured (beyond sourced revenue)")

        influence_substr = "Besides Sourced Revenue, how else does your company measure partner influence impact?"
        infl_pct = multi_select_pct(flt, contains_substring=influence_substr)
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
        else:
            st.info("No influence-impact multi-select columns detected for the current dataset.")

        create_section_header("Partnership types in place today")

        types_substr = "Which of the following Partnership types does your company have?"
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
        else:
            st.info("No partnership-type multi-select columns detected for the current dataset.")

    # ======================================================
    # TAB 5 – DATA
    # ======================================================
    with tab_data:
        create_section_header("Filtered data")

        cols_available = flt.columns.tolist()
        default_cols = [
            COL_REGION,
            "RegionStd",
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

        csv_bytes = flt[selected_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download filtered data as CSV",
            csv_bytes,
            "sopl_filtered.csv",
            "text/csv",
        )

    # ---- Footer ----
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#64748b !important; font-size:0.85rem;'>"
        "SOPL 2025 Insights Platform • Partnership analytics and strategic insights"
        "</div>",
        unsafe_allow_html=True,
    )

    # ===== Embedded Pickaxe assistant (always visible, large) =====
    st.markdown(
        "<h2 style='color:#020617; margin-top:1.5rem;'>Assistant (SOPL Q&A)</h2>",
        unsafe_allow_html=True,
    )
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
