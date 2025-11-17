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

# ==================== ENHANCED CSS / LIGHT THEME ====================
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
    padding-top: 1rem;
}

/* Sidebar enhancements */
[data-testid="stSidebar"] {
    background-color: #f9fafb !important;
    border-right: 1px solid #e2e8f0;
}

[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] .stMultiSelect {
    margin-bottom: 1rem;
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

/* Enhanced Layout + typography */
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
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e2e8f0;
}

/* ENHANCED MAIN TITLE */
.main-header {
    font-size: 2.8rem;
    font-weight: 900;
    margin: 0;
    color: #ec3d72 !important;      /* Amaranth */
    letter-spacing: -0.5px;
    line-height: 1.1;
    background: linear-gradient(135deg, #ec3d72 0%, #3b308f 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.main-header::after {
    content: "";
    display: block;
    width: 80px;
    height: 5px;
    background: linear-gradient(90deg, #ec3d72, #3b308f);
    border-radius: 4px;
    margin-top: 8px;
}

/* Enhanced Subtitle */
.sub-header {
    font-size: 1.25rem;
    color: #64748b !important;
    margin-top: 8px;
    font-weight: 400;
}

/* Enhanced Section Headers */
.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #f1f5f9;
    color: #1e293b !important;
}

.chart-caption {
    font-size: 0.85rem;
    color: var(--muted) !important;
    margin-top: 8px;
    font-style: italic;
}

/* Enhanced Cards */
.card {
    background: var(--panel);
    border-radius: 12px;
    padding: 16px 18px;
    border: 1px solid rgba(148,163,184,0.3);
    box-shadow: 0 2px 8px rgba(15,23,42,0.04);
    transition: all 0.2s ease;
}

.card:hover {
    box-shadow: 0 4px 12px rgba(15,23,42,0.08);
    transform: translateY(-1px);
}

/* Enhanced Widget polish */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: 10px;
    border-color: #d4d4d8;
    transition: all 0.2s ease;
}

.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: #3b308f;
    box-shadow: 0 0 0 3px rgba(59, 48, 143, 0.1);
}

/* Enhanced Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #f8fafc;
    padding: 4px;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    font-size: 0.95rem;
    font-weight: 600;
    border-radius: 8px;
    padding: 8px 16px;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #3b308f;
    color: white !important;
}

.stTabs [data-baseweb="tab"][aria-selected="false"] {
    color: #64748b !important;
}

/* Enhanced KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin: 1.5rem 0;
}

/* Enhanced Chart Containers */
.chart-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(15,23,42,0.03);
    margin-bottom: 1.5rem;
}

/* Enhanced Footer */
.footer {
    text-align: center;
    color: #64748b !important;
    font-size: 0.9rem;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
}

/* Responsive improvements */
@media (max-width: 768px) {
    .main-header {
        font-size: 2.2rem;
    }
    .kpi-grid {
        grid-template-columns: 1fr;
    }
}

/* Enhanced loading states */
.stSpinner > div {
    border-top-color: #3b308f !important;
}

/* Improved data table */
.dataframe {
    border-radius: 10px !important;
    overflow: hidden !important;
}

/* Enhanced assistant section */
.assistant-header {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 2rem 0 1rem 0;
    border: 1px solid #e2e8f0;
}

/* FIXED: Altair/Vega actions menu - light theme with visible text */
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
                "category": ["#3b308f", "#ec3d72", "#64748b", "#93c5fd", "#1d4ed8", "#0f766e", "#f59e0b", "#ef4444"]
            },
            "axis": {
                "labelColor": "#475569",
                "titleColor": "#020617",
                "titleFontWeight": 600,
                "gridColor": "#f1f5f9",
                "domainColor": "#d4d4d8",
                "labelLimit": 260,
                "labelFontSize": 11,
                "titleFontSize": 12,
            },
            "legend": {
                "labelColor": "#475569",
                "titleColor": "#020617",
                "titleFontWeight": 600,
                "labelFontSize": 11,
                "titleFontSize": 12,
            },
            "title": {
                "color": "#020617",
                "fontSize": 16,
                "fontWeight": 700,
                "anchor": "start",
                "offset": 10,
            },
            "header": {
                "labelFontSize": 12,
                "titleFontSize": 14,
            }
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

# ==================== ENHANCED HELPERS ====================
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
    """Enhanced Donut with % labels on slices."""
    if df_pct.empty:
        st.info("No responses for this question in the current filter.")
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)
    data["PercentLabel"] = data["Percent"].map(lambda v: f"{v:.1f}%")

    base = alt.Chart(data).encode(
        theta=alt.Theta("Percent:Q", stack=True),
        color=alt.Color(f"{cat_field}:N", 
                       legend=alt.Legend(title=None, orient='right'),
                       scale=alt.Scale(scheme='category10')),
        tooltip=[f'{cat_field}:N', alt.Tooltip('Percent:Q', format='.1f')]
    )

    donut = base.mark_arc(innerRadius=70, stroke="#fff", strokeWidth=2)
    text = base.mark_text(radius=115, size=12, fontWeight=600, color="#020617").encode(
        text=alt.Text("PercentLabel:N")
    )

    chart = (donut + text).properties(
        width=400,
        height=400,
        title=alt.TitleParams(title, fontSize=16, fontWeight=700, anchor='start')
    ).configure_view(strokeWidth=0)

    st.altair_chart(chart, use_container_width=True)


def bar_chart_from_pct(
    df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str, horizontal: bool = True
):
    """Enhanced Bar chart with % labels and better styling."""
    if df_pct.empty:
        st.info("No responses for this question in the current filter.")
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)
    data["PercentLabel"] = data["Percent"].map(lambda v: f"{v:.1f}%")

    # Fix the scale domain issue - use proper Altair syntax
    max_percent = data['Percent'].max()
    domain_max = 100 if max_percent <= 100 else None
    
    if horizontal:
        base = alt.Chart(data).encode(
            x=alt.X(
                "Percent:Q",
                title="Share of respondents (%)",
                axis=alt.Axis(format=".0f", grid=True, gridColor="#f1f5f9"),
                scale=alt.Scale(domain=[0, domain_max] if domain_max else None)
            ),
            y=alt.Y(
                f"{cat_field}:N",
                sort="-x",
                title=None,
                axis=alt.Axis(labelLimit=280, labelOverlap=False, labelFontSize=11),
            ),
            tooltip=[f'{cat_field}:N', alt.Tooltip('Percent:Q', format='.1f', title='Percentage')]
        )

        bars = base.mark_bar(color="#3b308f", cornerRadius=4)
        labels = base.mark_text(
            align="left", baseline="middle", dx=4, color="#020617", fontWeight=600
        ).encode(text=alt.Text("PercentLabel:N"))

        chart = (bars + labels).properties(
            height=max(300, 35 * len(data)),
            title=alt.TitleParams(title, fontSize=16, fontWeight=700, anchor='start')
        ).configure_axisY(labelPadding=8)
    else:
        base = alt.Chart(data).encode(
            x=alt.X(
                f"{cat_field}:N",
                sort="-y",
                title=None,
                axis=alt.Axis(labelLimit=280, labelOverlap=False, labelAngle=0, labelFontSize=11),
            ),
            y=alt.Y(
                "Percent:Q",
                title="Share of respondents (%)",
                axis=alt.Axis(format=".0f", grid=True, gridColor="#f1f5f9"),
                scale=alt.Scale(domain=[0, domain_max] if domain_max else None)
            ),
            tooltip=[f'{cat_field}:N', alt.Tooltip('Percent:Q', format='.1f', title='Percentage')]
        )
        bars = base.mark_bar(color="#3b308f", cornerRadius=4)
        labels = base.mark_text(
            align="center", baseline="bottom", dy=-6, color="#020617", fontWeight=600
        ).encode(text=alt.Text("PercentLabel:N"))

        chart = (bars + labels).properties(
            height=400,
            title=alt.TitleParams(title, fontSize=16, fontWeight=700, anchor='start')
        )

    st.altair_chart(chart, use_container_width=True)


def win_rate_distribution_pct(df: pd.DataFrame, col: str):
    """Enhanced Win rate distribution chart."""
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
    """Enhanced KPI card for execs."""
    border_color = "#ec3d72" if accent else "#3b308f"
    html = f"""
<div style="
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    border-top: 4px solid {border_color};
    box-shadow: 0 4px 12px rgba(15,23,42,0.06);
    min-height: 120px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
">
  <div style="position: absolute; top: 0; right: 0; width: 60px; height: 60px; 
              background: {border_color}10; border-radius: 0 0 0 60px;"></div>
  
  <div style="font-size:0.8rem; letter-spacing:0.08em; text-transform:uppercase;
              color:#64748b; font-weight:600; margin-bottom:8px; position: relative;">
    {title}
  </div>
  <div style="font-size:2.2rem; font-weight:800; color:#020617; margin-bottom:4px; 
              line-height:1.1; position: relative;">
    {value}
  </div>
  {f'<div style="font-size:0.9rem; color:#64748b; position: relative;">{subtitle}</div>' if subtitle else ''}
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


# ==================== ENHANCED MAIN APP ====================
def main():
    st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)

    # ---- Enhanced Header ----
    st.markdown(
        """
<div class="header-row">
  <div>
    <div class="main-header">STATE OF PARTNERSHIP LEADERS 2025</div>
    <div class="sub-header">Strategic Insights Dashboard • Partnership Performance Analytics</div>
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
    COL_REVENUE = "What is your company's estimated annual revenue?"
    COL_EMPLOYEES = "What is your company's total number of employees?"
    COL_DEAL_SIZE = "How does your average deal size involving partners compare to direct or non-partner deals?"
    COL_CAC = "How does your customer acquisition cost (CAC) from partners compared to direct sales and marketing?"
    COL_SALES_CYCLE = "How does your partner-led sales cycle compare to your direct sales cycle?"
    COL_WIN_RATE = "What's your win rate for deals where partners are involved?"

    # Normalized region
    if COL_REGION in df.columns:
        df = df.copy()
        df["RegionStd"] = df[COL_REGION].map(normalize_region_label)
    else:
        df["RegionStd"] = None

    # ---- Enhanced Sidebar filters ----
    st.sidebar.header("🔍 Data Filters")
    st.sidebar.markdown("Apply filters to segment the data by company attributes.")

    # Region filter
    if "RegionStd" in df.columns:
        region_options = sorted(df["RegionStd"].dropna().unique().tolist())
        selected_regions = st.sidebar.multiselect(
            "🌍 Region (HQ)",
            options=region_options,
            default=region_options,
            help="Filter by company headquarters region"
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
            "💰 Annual revenue band",
            options=ordered_revenue,
            default=ordered_revenue,
            help="Filter by company annual revenue"
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
            "👥 Total employees",
            options=ordered_emp,
            default=ordered_emp,
            help="Filter by company size"
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

    # ---- Enhanced Tabs ----
    tab_overview, tab_performance, tab_geo, tab_multi, tab_data = st.tabs(
        ["📊 Overview", "🚀 Performance", "🌍 Geography", "🤝 Partner Impact", "📁 Data"]
    )

    # ======================================================
    # TAB 0 – ENHANCED EXECUTIVE SUMMARY
    # ======================================================
    with tab_overview:
        create_section_header("Executive Summary")

        # Calculate KPIs
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

        # Enhanced KPI cards in grid layout
        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            kpi_card(
                "🏭 Top Industry",
                top_industry_name or "—",
                subtitle=f"Share: {top_industry_pct:.1f}%" if top_industry_pct is not None else "No data",
                accent=True,
            )
        with col2:
            kpi_card(
                "🌍 Top Region",
                top_region_name or "—",
                subtitle=f"Share: {top_region_pct:.1f}%" if top_region_pct is not None else "No data",
            )
        with col3:
            kpi_card(
                "🏢 Large Companies",
                kpi_value_str(large_emp_pct),
                subtitle="500+ employees",
            )
        with col4:
            kpi_card(
                "🎯 Median Win Rate",
                f"{median_win_rate:.1f}%" if median_win_rate is not None else "—",
                subtitle="Partner-involved deals",
            )
        
        col5, col6 = st.columns(2)
        with col5:
            kpi_card(
                "💰 Larger Partner Deals",
                kpi_value_str(higher_deal_pct),
                subtitle="vs. direct deals",
            )
        with col6:
            kpi_card(
                "📉 Lower Partner CAC",
                kpi_value_str(lower_cac_pct),
                subtitle="vs. direct acquisition",
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Enhanced Company Profile Section
        create_section_header("Company Profile Distribution")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if "RegionStd" in flt.columns:
                region_pct = value_counts_pct(flt["RegionStd"])
                donut_chart_with_labels(
                    region_pct, "category", "pct", "Region (HQ) Distribution"
                )
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
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
                    "Annual Revenue Distribution",
                    horizontal=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

        c3, c4 = st.columns(2)

        with c3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
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
                    "Company Size Distribution",
                    horizontal=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_INDUSTRY in flt.columns:
                ind_pct = value_counts_pct(flt[COL_INDUSTRY])
                bar_chart_from_pct(
                    ind_pct,
                    "category",
                    "pct",
                    "Industry Sector Distribution",
                    horizontal=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # ENHANCED PERFORMANCE TAB
    # ======================================================
    with tab_performance:
        create_section_header("Partner Performance Metrics")

        st.markdown("""
        <div style="background: #f0f9ff; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border-left: 4px solid #3b308f;">
            <strong>💡 Performance Insights:</strong> Compare partner-led metrics against direct sales performance to understand partnership effectiveness.
        </div>
        """, unsafe_allow_html=True)

        p1, p2 = st.columns(2)

        with p1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_DEAL_SIZE in flt.columns:
                ds_pct = value_counts_pct(flt[COL_DEAL_SIZE])
                bar_chart_from_pct(
                    ds_pct,
                    "category",
                    "pct",
                    "Average Deal Size: Partner vs Direct",
                    horizontal=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

        with p2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_CAC in flt.columns:
                cac_pct = value_counts_pct(flt[COL_CAC])
                bar_chart_from_pct(
                    cac_pct,
                    "category",
                    "pct",
                    "Partner-sourced CAC vs Direct",
                    horizontal=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

        create_section_header("Sales Efficiency Metrics")

        p3, p4 = st.columns(2)

        with p3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_SALES_CYCLE in flt.columns:
                sc_pct = value_counts_pct(flt[COL_SALES_CYCLE])
                bar_chart_from_pct(
                    sc_pct,
                    "category",
                    "pct",
                    "Partner-led Sales Cycle vs Direct",
                    horizontal=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

        with p4:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_WIN_RATE in flt.columns:
                win_rate_distribution_pct(flt, COL_WIN_RATE)
            st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # ENHANCED GEOGRAPHY TAB
    # ======================================================
    with tab_geo:
        create_section_header("Geographical Distribution")

        if "RegionStd" in flt.columns:
            region_pct = value_counts_pct(flt["RegionStd"])

            g1, g2 = st.columns(2)

            with g1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                donut_chart_with_labels(
                    region_pct,
                    "category",
                    "pct",
                    "Regional Distribution",
                )
                st.markdown('</div>', unsafe_allow_html=True)

            with g2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                bar_chart_from_pct(
                    region_pct,
                    "category",
                    "pct",
                    "Regional Share Comparison",
                    horizontal=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # Enhanced Map Section
            create_section_header("Global Respondent Distribution")

            region_coords = {
                "North America": (40.0, -100.0),
                "Latin America": (-20.0, -60.0),
                "Europe": (50.0, 10.0),
                "Asia Pacific": (20.0, 100.0),
            }

            map_df = region_pct.rename(columns={"category": "region"}).copy()
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
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    map_df,
                    get_position=["lon", "lat"],
                    get_radius="Percent * 400000",
                    radius_min_pixels=12,
                    radius_max_pixels=80,
                    get_fill_color=[59, 48, 143, 210],
                    get_line_color=[255, 255, 255, 230],
                    line_width_min_pixels=2,
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
                    tooltip={"html": "<b>{region}</b><br>Share: {PercentLabel}"},
                )
                st.pydeck_chart(deck)
                st.markdown('</div>', unsafe_allow_html=True)

    # ======================================================
    # ENHANCED PARTNER & IMPACT TAB
    # ======================================================
    with tab_multi:
        create_section_header("Partner Influence & Types")

        st.markdown("""
        <div style="background: #f0f9ff; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; border-left: 4px solid #3b308f;">
            <strong>📈 Multi-select Analysis:</strong> These charts show the percentage of companies that selected each option. Companies can select multiple options.
        </div>
        """, unsafe_allow_html=True)

        influence_substr = "Besides Sourced Revenue, how else does your company measure partner influence impact?"
        infl_pct = multi_select_pct(flt, contains_substring=influence_substr)
        if not infl_pct.empty:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            bar_chart_from_pct(
                infl_pct,
                "option",
                "pct",
                "Partner Influence Measurement Methods",
                horizontal=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No influence-impact multi-select columns detected for the current dataset.")

        create_section_header("Partnership Ecosystem")

        types_substr = "Which of the following Partnership types does your company have?"
        types_pct = multi_select_pct(flt, contains_substring=types_substr)
        if not types_pct.empty:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            bar_chart_from_pct(
                types_pct,
                "option",
                "pct",
                "Partnership Types in Use",
                horizontal=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No partnership-type multi-select columns detected for the current dataset.")

    # ======================================================
    # ENHANCED DATA TAB
    # ======================================================
    with tab_data:
        create_section_header("Data Explorer")

        st.markdown("""
        <div style="background: #f8fafc; border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
            <strong>🔍 Data Exploration:</strong> Browse and download the filtered dataset. Use the column selector to focus on specific data points.
        </div>
        """, unsafe_allow_html=True)

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
            "Select columns to display:",
            options=cols_available,
            default=default_cols if default_cols else cols_available[:8],
            help="Choose which columns to display in the data table below"
        )

        st.markdown(f"**Displaying {len(flt)} rows and {len(selected_cols)} columns**")
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.dataframe(flt[selected_cols], use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)

        csv_bytes = flt[selected_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Filtered Data as CSV",
            csv_bytes,
            "sopl_2025_filtered_data.csv",
            "text/csv",
            help="Download the currently filtered dataset as a CSV file",
            use_container_width=True
        )

    # ---- Enhanced Footer ----
    st.markdown(
        """
        <div class="footer">
            <strong>SOPL 2025 Insights Platform</strong> • Partnership analytics and strategic insights<br>
            <span style="color: #94a3b8; font-size: 0.8rem;">
                Last updated: 2025 • Data sourced from State of Partnership Leaders Survey
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ===== Enhanced Assistant Section =====
    st.markdown(
        """
        <div class="assistant-header">
            <h2 style='color:#020617; margin:0;'>🤖 SOPL Assistant</h2>
            <p style='color:#64748b; margin:0.5rem 0 0 0;'>Ask questions about the data and insights in this dashboard</p>
        </div>
        """,
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
