import altair as alt
import pandas as pd
import pydeck as pdk  # safe to keep
import streamlit as st
import streamlit.components.v1 as components

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SOPL 2025 - Partnership Analytics",
    page_icon="PL_transparent_1080.ico",
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
    color: #020617;
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
    background-color: #0b1120 !important; /* dark sidebar */
    border-right: 1px solid #1e293b;
}

/* Sidebar controls */
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
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e2e8f0;
}

/* MAIN TITLE – Amaranth + gradient */
.main-header {
    font-size: 2.8rem;
    font-weight: 900;
    margin: 0;
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

/* Subtitle */
.sub-header {
    font-size: 1.25rem;
    color: #64748b !important;
    margin-top: 8px;
    font-weight: 400;
}

/* Section headers */
.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #f1f5f9;
    color: #1e293b !important;
}

/* Chart caption */
.chart-caption {
    font-size: 0.85rem;
    color: var(--muted) !important;
    margin-top: 8px;
    font-style: italic;
}

/* Generic card (for charts / blocks) */
.chart-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(15,23,42,0.03);
    margin-bottom: 1.5rem;
}

/* KPI grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.5rem;
    margin: 1.5rem 0;
}

/* Widget polish + brand colors for filters */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: 10px;
    border-color: #ec3d72;
    transition: all 0.2s ease;
    background-color: #020617;   /* dark field background */
    color: #f9fafb !important;
}

.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: #f97373;
    box-shadow: 0 0 0 3px rgba(236, 61, 114, 0.4);
}

/* Multiselect tags aligned to brand */
.stMultiSelect [data-baseweb="tag"] {
    background-color: #ec3d72 !important;  /* Amaranth */
    color: #ffffff !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #020617;
    padding: 4px;
    border-radius: 12px;
}

/* Base tab style */
.stTabs [data-baseweb="tab"] {
    font-size: 0.95rem;
    font-weight: 600;
    border-radius: 999px;
    padding: 8px 18px;
    transition: all 0.2s ease;
    border: none;
}

/* Selected tab: dark-purple with white text, subtle underline accent */
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #3b308f;
    color: #ffffff !important;
    box-shadow: 0 0 0 1px #3b308f, 0 10px 18px rgba(0,0,0,0.35);
}
.stTabs [data-baseweb="tab"][aria-selected="true"]::after {
    content: "";
    display:block;
    height: 3px;
    width: 60%;
    margin: 4px auto 0;
    border-radius: 999px;
    background: linear-gradient(90deg, #ec3d72, #f97373);
}

/* Ensure all children text is white in the active tab */
.stTabs [data-baseweb="tab"][aria-selected="true"] * {
    color: #ffffff !important;
}

/* Unselected tab */
.stTabs [data-baseweb="tab"][aria-selected="false"] {
    background-color: transparent;
    color: #e5e7eb !important;
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

/* Footer */
.footer {
    text-align: center;
    color: #64748b !important;
    font-size: 0.9rem;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
}

/* Assistant header */
.assistant-header {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1.5rem 0 1rem 0;
    border: 1px solid #e2e8f0;
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

/* =========================================================
   FIX: REMOVE EMPTY RECTANGLES ABOVE CHARTS
   These hide empty Streamlit blocks that are picking up
   chart-container styling / column spacing.
   ========================================================= */
.chart-container:empty {
    display: none !important;
    padding: 0 !important;
    margin: 0 !important;
    border: 0 !important;
    box-shadow: none !important;
}
.chart-container > div:empty,
.chart-container > p:empty {
    display: none !important;
}
div[data-testid="column"]:empty {
    display: none !important;
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
                "category": [
                    "#3b308f",
                    "#ec3d72",
                    "#64748b",
                    "#93c5fd",
                    "#1d4ed8",
                    "#0f766e",
                    "#f59e0b",
                    "#ef4444",
                ]
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
            },
        }
    }

alt.themes.register("atlas_light", atlas_light_theme)
alt.themes.enable("atlas_light")

alt.data_transformers.disable_max_rows()
alt.renderers.set_embed_options(
    actions={"export": True, "source": False, "compiled": False, "editor": False}
)

# ==================== GOOGLE SHEETS LOADER ====================
@st.cache_data(show_spinner=True)
def load_data() -> pd.DataFrame:
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
    s = series.dropna()
    if s.empty:
        return pd.DataFrame(columns=["category", "pct"])
    counts = s.value_counts()
    total_non_null = len(s)
    pct = (counts / total_non_null) * 100.0
    out = pct.reset_index()
    out.columns = ["category", "pct"]
    return out

def multi_select_pct(
    df: pd.DataFrame, col_prefix: str | None = None, contains_substring: str | None = None
) -> pd.DataFrame:
    if col_prefix:
        cols = [c for c in df.columns if c.startswith(col_prefix)]
    elif contains_substring:
        cols = [c for c in df.columns if contains_substring in c]
    else:
        return pd.DataFrame(columns=["option", "pct"])

    if not cols:
        return pd.DataFrame(columns=["option", "pct"])

    total_selections = 0
    selection_counts = {}
    for c in cols:
        col = df[c]
        selected = ((col == 1) | (col == 1.0) | (col == True)).sum()
        selection_counts[c] = selected
        total_selections += selected

    if total_selections == 0:
        return pd.DataFrame(columns=["option", "pct"])

    rows = []
    for c in cols:
        selected = selection_counts[c]
        pct = (selected / total_selections * 100.0)
        label = c.split("_", 1)[1] if "_" in c else c
        rows.append({"option": label, "pct": pct})

    out = pd.DataFrame(rows).sort_values("pct", ascending=False)
    return out

def create_section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def donut_chart_with_labels(
    df_pct: pd.DataFrame,
    cat_field: str,
    pct_field: str,
    title: str,
    exclude_label_categories: list[str] | None = None
):
    if df_pct.empty:
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)

    exclude_set = set(exclude_label_categories or [])
    data["PercentLabel"] = data.apply(
        lambda r: "" if r[cat_field] in exclude_set else f"{r['Percent']:.1f}%",
        axis=1
    )

    base = alt.Chart(data).encode(
        theta=alt.Theta("Percent:Q", stack=True),
        color=alt.Color(
            f"{cat_field}:N",
            legend=alt.Legend(title=None, orient="right"),
            scale=alt.Scale(scheme="category10"),
        ),
        tooltip=[f"{cat_field}:N", alt.Tooltip("Percent:Q", format=".1f")],
    )

    donut = base.mark_arc(innerRadius=70, stroke="#fff", strokeWidth=2)

    # Only draw text when PercentLabel isn't empty
    text = base.transform_filter(
        alt.datum.PercentLabel != ""
    ).mark_text(
        radius=115, size=12, fontWeight=600, color="#020617"
    ).encode(text=alt.Text("PercentLabel:N"))

    chart = (donut + text).properties(
        width=400,
        height=400,
        title=alt.TitleParams(title, fontSize=16, fontWeight=700, anchor="start"),
    ).configure_view(strokeWidth=0)

    st.altair_chart(chart, use_container_width=True)

def bar_chart_from_pct(
    df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str, horizontal: bool = True
):
    if df_pct.empty:
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)
    data["PercentLabel"] = data["Percent"].map(lambda v: f"{v:.1f}%")

    max_percent = data["Percent"].max()
    domain_max = 100 if max_percent <= 100 else None

    if horizontal:
        base = alt.Chart(data).encode(
            x=alt.X(
                "Percent:Q",
                title="Share of respondents (%)",
                axis=alt.Axis(format=".0f", grid=True, gridColor="#f1f5f9"),
                scale=alt.Scale(domain=[0, domain_max] if domain_max else None),
            ),
            y=alt.Y(
                f"{cat_field}:N",
                sort="-x",
                title=None,
                axis=alt.Axis(labelLimit=280, labelOverlap=False, labelFontSize=11),
            ),
            tooltip=[
                f"{cat_field}:N",
                alt.Tooltip("Percent:Q", format=".1f", title="Percentage"),
            ],
        )

        bars = base.mark_bar(color="#3b308f", cornerRadius=4)
        labels = base.mark_text(
            align="left", baseline="middle", dx=4, color="#020617", fontWeight=600
        ).encode(text=alt.Text("PercentLabel:N"))

        chart = (bars + labels).properties(
            height=max(300, 35 * len(data)),
            title=alt.TitleParams(title, fontSize=16, fontWeight=700, anchor="start"),
        ).configure_axisY(labelPadding=8)
    else:
        base = alt.Chart(data).encode(
            x=alt.X(
                f"{cat_field}:N",
                sort="-y",
                title=None,
                axis=alt.Axis(
                    labelLimit=280,
                    labelOverlap=False,
                    labelAngle=0,
                    labelFontSize=11,
                ),
            ),
            y=alt.Y(
                "Percent:Q",
                title="Share of respondents (%)",
                axis=alt.Axis(format=".0f", grid=True, gridColor="#f1f5f9"),
                scale=alt.Scale(domain=[0, domain_max] if domain_max else None),
            ),
            tooltip=[
                f"{cat_field}:N",
                alt.Tooltip("Percent:Q", format=".1f", title="Percentage"),
            ],
        )
        bars = base.mark_bar(color="#3b308f", cornerRadius=4)
        labels = base.mark_text(
            align="center", baseline="bottom", dy=-6, color="#020617", fontWeight=600
        ).encode(text=alt.Text("PercentLabel:N"))

        chart = (bars + labels).properties(
            height=400,
            title=alt.TitleParams(title, fontSize=16, fontWeight=700, anchor="start"),
        )

    st.altair_chart(chart, use_container_width=True)

def win_rate_distribution_pct(df: pd.DataFrame, col: str):
    series = df[col].dropna()
    if series.empty:
        return False

    bins = list(range(0, 101, 10))
    labels = [f"{b}–{b+10}%" for b in bins[:-1]]
    binned = pd.cut(series, bins=bins, labels=labels, include_lowest=True, right=False)
    pct_df = value_counts_pct(binned).rename(columns={"category": "bin"})
    if pct_df.empty:
        return False

    bar_chart_from_pct(
        pct_df,
        "bin",
        "pct",
        "Win rate distribution (10-point bands)",
        horizontal=False,
    )
    st.markdown(
        '<div class="chart-caption" style="text-align:center;">'
        "Percentages are based on respondents who answered the win-rate question."
        "</div>",
        unsafe_allow_html=True,
    )
    return True

def normalize_region_label(x):
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

def find_col(df: pd.DataFrame, exact: str | None=None, substrings: list[str] | None=None):
    if exact and exact in df.columns:
        return exact
    if substrings:
        for s in substrings:
            matches = [c for c in df.columns if s in c]
            if matches:
                return matches[0]
    return None

def normalize_yes_no(series: pd.Series) -> pd.Series:
    """
    Convert common 0/1, True/False, yes/no variants into clean Yes/No labels.
    Leaves other strings unchanged.
    """
    s = series.dropna()
    if s.empty:
        return series

    # If numeric/boolean-ish, map to Yes/No
    coerced = pd.to_numeric(series, errors="coerce")
    if coerced.notna().any() and coerced.dropna().isin([0, 1]).all():
        return coerced.map({1: "Yes", 0: "No"})

    lower = series.astype(str).str.strip().str.lower()
    mapping = {
        "1": "Yes", "1.0": "Yes", "true": "Yes", "yes": "Yes",
        "0": "No", "0.0": "No", "false": "No", "no": "No",
    }
    mapped = lower.map(mapping)
    return mapped.where(mapped.notna(), series.astype(str))

# ---- Rendering guards ----
def render_container_if(has_data: bool, chart_fn):
    if not has_data:
        return
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    chart_fn()
    st.markdown("</div>", unsafe_allow_html=True)

def two_up_or_full(left_has: bool, left_fn, right_has: bool, right_fn):
    if left_has and right_has:
        c1, c2 = st.columns(2)
        with c1:
            render_container_if(True, left_fn)
        with c2:
            render_container_if(True, right_fn)
    elif left_has:
        render_container_if(True, left_fn)
    elif right_has:
        render_container_if(True, right_fn)
    else:
        return

# ==================== MAIN APP ====================
def main():
    st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)

    # ---- Header ----
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

    # ---- Welcome paragraph (persistent) ----
    st.markdown(
        """
<div class="chart-container" style="margin-top:0;">
  <p>
  Welcome to the State of Partnership Leaders 2025 dashboard. In prior years, we have released a 40+ page document with all of the data but with the advancements in AI adoption, we are trying something new.
  </p>
  <p><strong>Below you will find:</strong></p>
  <ul>
    <li>
      <strong>PartnerOps Agent</strong> - An AI agent trained on the SOPL dataset - think of it as your Partner Operations collaborator as you review the data.
      You can ask it questions about the data or about your own strategy, we will not collect any of your inputed data.
    </li>
    <li>
      <strong>SOPL Data Dashboard</strong> - You will find all of the data from the report in an interactive dashboard below.
      Use the filters on the left to customize the data to your interests and the Performance, and Partner Impact tabs to navigate the main themes.
    </li>
  </ul>
</div>
""",
        unsafe_allow_html=True,
    )

    # ---- Assistant ----
    st.markdown(
        """
        <div class="assistant-header">
            <h2 style='color:#020617; margin:0;'>Assistant (SOPL Q&amp;A)</h2>
            <p style='color:#64748b; margin:0.5rem 0 0 0;'>
                Ask questions about the SOPL dataset, methodology, or what you are seeing in the dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pickaxe_html = """
<div id="deployment-5870ff7d-8fcf-4395-976b-9e9fdefbb0ff" style="width:100%; max-width:1200px; margin:0 auto;"></div>
<script src="https://studio.pickaxe.co/api/embed/bundle.js" defer></script>
"""
    components.html(pickaxe_html, height=650, scrolling=False)

    # ---- Load data ----
    df = load_data()
    if df.empty:
        st.stop()

    # ---- Column names ----
    COL_REGION = "Please select the region where your company is headquartered."
    COL_INDUSTRY = "What industry sector does your company operate in?"
    COL_REVENUE = "What is your company’s estimated annual revenue?"
    COL_EMPLOYEES = "What is your company’s total number of employees?"
    COL_DEAL_SIZE = "How does your average deal size involving partners compare to direct or non-partner deals?"
    COL_CAC = "How does your customer acquisition cost (CAC) from partners compared to direct sales and marketing?"
    COL_SALES_CYCLE = "How does your partner-led sales cycle compare to your direct sales cycle?"
    COL_WIN_RATE = "What’s your win rate for deals where partners are involved?"

    COL_PRIMARY_GOAL = find_col(df, substrings=["main goal for partnerships in the next 12 months"])
    COL_EXEC_EXPECT = find_col(df, substrings=["executive team’s expectations of partnerships"])
    COL_EXPECTED_REV = find_col(df, substrings=["expected to come from partnerships in the next 12 months"])
    COL_RETENTION = find_col(df, substrings=["retention rate for partner-referred customers"])
    COL_MOST_IMPACTFUL_TYPE = find_col(df, substrings=["most impact on your organization", "most impactful"])
    COL_BIGGEST_CHALLENGE = find_col(df, substrings=["biggest challenge in scaling your partner program"])
    COL_MISS_GOALS_REASON = find_col(df, substrings=["most likely reason your Partnerships team could miss its goals"])
    COL_TEAM_SIZE = find_col(df, substrings=["people are on your Partnerships team"])
    COL_BUDGET = find_col(df, substrings=["annual budget", "Partnerships team’s annual budget"])
    COL_USE_TECH = find_col(df, substrings=["technology or automation tools to manage your partner ecosystem"])
    COL_USE_AI = find_col(df, substrings=["using AI in your partner organization"])
    COL_MARKETPLACE_LISTED = find_col(df, substrings=["listed in at least one third-party marketplace", "marketplace"])
    COL_MARKETPLACE_REV = find_col(df, substrings=["revenue comes through cloud marketplaces"])

    if COL_REGION in df.columns:
        df = df.copy()
        df["RegionStd"] = df[COL_REGION].map(normalize_region_label)
    else:
        df["RegionStd"] = None

    # ---- Sidebar filters ----
    st.sidebar.header("Filters")

    if "RegionStd" in df.columns:
        region_options = sorted(df["RegionStd"].dropna().unique().tolist())
        selected_regions = st.sidebar.multiselect("Region (HQ)", region_options, region_options)
    else:
        selected_regions = None

    if COL_REVENUE in df.columns:
        revenue_options = df[COL_REVENUE].dropna().unique().tolist()
        revenue_order = [
            "Less than $50 million", "$50M – $250M", "$250M – $1B",
            "$1B – $10B", "More than $10B",
        ]
        ordered_revenue = [r for r in revenue_order if r in revenue_options] + [
            r for r in revenue_options if r not in revenue_order
        ]
        selected_revenue = st.sidebar.multiselect("Annual revenue band", ordered_revenue, ordered_revenue)
    else:
        selected_revenue = None

    if COL_EMPLOYEES in df.columns:
        emp_options = df[COL_EMPLOYEES].dropna().unique().tolist()
        emp_order = [
            "Less than 100 employees", "100 – 500 employees",
            "501 – 5,000 employees", "More than 5,000 employees",
        ]
        ordered_emp = [e for e in emp_order if e in emp_options] + [
            e for e in emp_options if e not in emp_order
        ]
        selected_employees = st.sidebar.multiselect("Total employees", ordered_emp, ordered_emp)
    else:
        selected_employees = None

    flt = df.copy()
    if selected_regions:
        flt = flt[flt["RegionStd"].isin(selected_regions)]
    if selected_revenue:
        flt = flt[flt[COL_REVENUE].isin(selected_revenue)]
    if selected_employees:
        flt = flt[flt[COL_EMPLOYEES].isin(selected_employees)]

    # ---- About section (persistent) ----
    create_section_header("About this dashboard and dataset")
    st.markdown(
        """
<div class="chart-container" style="margin-top:0;">
  <p>
  Respondents represent organizations from four key regions, namely North America (NA),
  Europe the Middle East and Africa (EMEA), Asia Pacific (APAC), and Latin America (LATAM),
  and include companies of varying sizes and revenue levels ranging from less than 50 million
  dollars to over 10 billion dollars in annual revenue. All survey waves ensure a minimum of
  100 qualified respondents each year to provide consistent and data-driven insights across regions
  and industries.
  </p>
  <p style="margin-top:0.5rem;">
  Use the filters on the left (Region, Annual revenue band, Total employees) to narrow the view;
  the KPIs and charts in every tab update automatically to reflect the current selection.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    # ---- Tabs ----
    tab_perf, tab_strategy, tab_portfolio, tab_ops, tab_team, tab_tech, tab_market, tab_impact = st.tabs(
        [
            "Performance",
            "Strategic Direction",
            "Portfolio",
            "Operational Challenges",
            "Team & Investment",
            "Technology & AI",
            "Marketplaces",
            "Partner Impact",
        ]
    )

    # ======================================================
    # PERFORMANCE
    # ======================================================
    with tab_perf:
        create_section_header("Partner performance metrics")

        ds_has = COL_DEAL_SIZE in flt.columns and not flt[COL_DEAL_SIZE].dropna().empty
        def ds_chart():
            ds_pct = value_counts_pct(flt[COL_DEAL_SIZE])
            bar_chart_from_pct(ds_pct, "category", "pct", "Average deal size: partner vs direct", horizontal=True)

        cac_has = COL_CAC in flt.columns and not flt[COL_CAC].dropna().empty
        def cac_chart():
            cac_pct = value_counts_pct(flt[COL_CAC])
            bar_chart_from_pct(cac_pct, "category", "pct", "Partner-sourced CAC vs direct", horizontal=True)

        two_up_or_full(ds_has, ds_chart, cac_has, cac_chart)

        create_section_header("Sales cycle and win rate")

        sc_has = COL_SALES_CYCLE in flt.columns and not flt[COL_SALES_CYCLE].dropna().empty
        def sc_chart():
            sc_pct = value_counts_pct(flt[COL_SALES_CYCLE])
            bar_chart_from_pct(sc_pct, "category", "pct", "Partner-led sales cycle vs direct", horizontal=True)

        wr_has = COL_WIN_RATE in flt.columns and not flt[COL_WIN_RATE].dropna().empty
        def wr_chart():
            win_rate_distribution_pct(flt, COL_WIN_RATE)

        two_up_or_full(sc_has, sc_chart, wr_has, wr_chart)

        create_section_header("Retention of partner-referred customers")
        if COL_RETENTION and COL_RETENTION in flt.columns:
            ret_has = not flt[COL_RETENTION].dropna().empty
            def ret_chart():
                ret_series = pd.to_numeric(flt[COL_RETENTION], errors="coerce")
                if ret_series.notna().any():
                    bins = [0, 51, 76, 96, 101, 9999]
                    labels = ["0–50%", "51–75%", "76–95%", "96–100%", "More than 100%"]
                    binned = pd.cut(ret_series, bins=bins, labels=labels, include_lowest=True, right=False)
                    ret_pct = value_counts_pct(binned).rename(columns={"category": "bin"})
                    if not ret_pct.empty:
                        bar_chart_from_pct(ret_pct, "bin", "pct", "Retention rate distribution", horizontal=False)
                else:
                    ret_pct = value_counts_pct(flt[COL_RETENTION].astype(str))
                    if not ret_pct.empty:
                        bar_chart_from_pct(ret_pct, "category", "pct", "Retention rate distribution", horizontal=True)
            render_container_if(ret_has, ret_chart)

    # ======================================================
    # STRATEGIC DIRECTION
    # ======================================================
    with tab_strategy:
        create_section_header("Primary goal for partnerships (next 12 months)")
        if COL_PRIMARY_GOAL and COL_PRIMARY_GOAL in flt.columns:
            pg_has = not flt[COL_PRIMARY_GOAL].dropna().empty
            def pg_chart():
                pg_pct = value_counts_pct(flt[COL_PRIMARY_GOAL])
                bar_chart_from_pct(pg_pct, "category", "pct", "Primary goal for partnerships", horizontal=True)
            render_container_if(pg_has, pg_chart)

        create_section_header("Executive expectations of partnerships")
        if COL_EXEC_EXPECT and COL_EXEC_EXPECT in flt.columns:
            ex_has = not flt[COL_EXEC_EXPECT].dropna().empty
            def ex_chart():
                ex_pct = value_counts_pct(flt[COL_EXEC_EXPECT])
                bar_chart_from_pct(ex_pct, "category", "pct", "Executive expectations", horizontal=True)
            render_container_if(ex_has, ex_chart)

        create_section_header("Expected revenue from partnerships (next 12 months)")
        if COL_EXPECTED_REV and COL_EXPECTED_REV in flt.columns:
            er_has = not flt[COL_EXPECTED_REV].dropna().empty
            def er_chart():
                exp = flt[COL_EXPECTED_REV].dropna()
                as_num = pd.to_numeric(exp, errors="coerce")
                if as_num.notna().any():
                    bins = [0, 50, 75, 100, 9999]
                    labels = ["Less than 50%", "50–75%", "75–100%", "More than 100%"]
                    binned = pd.cut(as_num, bins=bins, labels=labels, include_lowest=True, right=False)
                    exp_pct = value_counts_pct(binned).rename(columns={"category": "bin"})
                    if not exp_pct.empty:
                        bar_chart_from_pct(exp_pct, "bin", "pct", "Expected revenue share from partnerships", horizontal=False)
                else:
                    exp_pct = value_counts_pct(exp.astype(str))
                    if not exp_pct.empty:
                        bar_chart_from_pct(exp_pct, "category", "pct", "Expected revenue share from partnerships", horizontal=True)
            render_container_if(er_has, er_chart)

    # ======================================================
    # PORTFOLIO
    # ======================================================
    with tab_portfolio:
        create_section_header("Partnership types currently in use")
        types_substr = "Which of the following Partnership types does your company have?"
        types_pct = multi_select_pct(flt, contains_substring=types_substr)
        types_has = not types_pct.empty
        def types_chart():
            bar_chart_from_pct(types_pct, "option", "pct", "Partnership types in place today", horizontal=True)
        render_container_if(types_has, types_chart)

        create_section_header("Most impactful partnership type")
        if COL_MOST_IMPACTFUL_TYPE and COL_MOST_IMPACTFUL_TYPE in flt.columns:
            mi_has = not flt[COL_MOST_IMPACTFUL_TYPE].dropna().empty
            def mi_chart():
                mi_pct = value_counts_pct(flt[COL_MOST_IMPACTFUL_TYPE])
                bar_chart_from_pct(mi_pct, "category", "pct", "Most impactful partnership type", horizontal=True)
            render_container_if(mi_has, mi_chart)

    # ======================================================
    # OPS CHALLENGES
    # ======================================================
    with tab_ops:
        create_section_header("Biggest challenge in scaling the partner program")
        if COL_BIGGEST_CHALLENGE and COL_BIGGEST_CHALLENGE in flt.columns:
            bc_has = not flt[COL_BIGGEST_CHALLENGE].dropna().empty
            def bc_chart():
                bc_pct = value_counts_pct(flt[COL_BIGGEST_CHALLENGE])
                bar_chart_from_pct(bc_pct, "category", "pct", "Biggest scaling challenge", horizontal=True)
            render_container_if(bc_has, bc_chart)

        create_section_header("Most likely reason for missing goals (next 12 months)")
        if COL_MISS_GOALS_REASON and COL_MISS_GOALS_REASON in flt.columns:
            mg_has = not flt[COL_MISS_GOALS_REASON].dropna().empty
            def mg_chart():
                mg_pct = value_counts_pct(flt[COL_MISS_GOALS_REASON])
                bar_chart_from_pct(mg_pct, "category", "pct", "Reason goals may be missed", horizontal=True)
            render_container_if(mg_has, mg_chart)

    # ======================================================
    # TEAM & INVESTMENT
    # ======================================================
    with tab_team:
        create_section_header("Partnerships team size")
        if COL_TEAM_SIZE and COL_TEAM_SIZE in flt.columns:
            ts_has = not flt[COL_TEAM_SIZE].dropna().empty
            def ts_chart():
                ts_pct = value_counts_pct(flt[COL_TEAM_SIZE])
                bar_chart_from_pct(ts_pct, "category", "pct", "Team size (people)", horizontal=True)
            render_container_if(ts_has, ts_chart)

        create_section_header("Annual partnerships budget (including headcount)")
        if COL_BUDGET and COL_BUDGET in flt.columns:
            bud_series = flt[COL_BUDGET].dropna().astype(str)
            bud_series = bud_series[
                ~bud_series.str.contains("I don’t have this data|I don't have this data", case=False, na=False)
            ]
            bud_pct = value_counts_pct(bud_series)
            bud_has = not bud_pct.empty
            def bud_chart():
                bar_chart_from_pct(bud_pct, "category", "pct", "Annual partnerships budget", horizontal=True)
                st.markdown(
                    '<div class="chart-caption">'
                    "Percentages exclude respondents who selected “I don’t have this data.”"
                    "</div>",
                    unsafe_allow_html=True,
                )
            render_container_if(bud_has, bud_chart)

    # ======================================================
    # TECH & AI
    # ======================================================
    with tab_tech:
        create_section_header("Use of technology / automation")
        if COL_USE_TECH and COL_USE_TECH in flt.columns:
            ut_pct = value_counts_pct(flt[COL_USE_TECH])
            ut_has = not ut_pct.empty
            def ut_chart():
                donut_chart_with_labels(
                    ut_pct, "category", "pct",
                    "Currently using partner tech/automation"
                )
            render_container_if(ut_has, ut_chart)

        create_section_header("Use of AI in the partner organization")
        if COL_USE_AI and COL_USE_AI in flt.columns:
            ai_pct = value_counts_pct(flt[COL_USE_AI])
            ai_has = not ai_pct.empty
            def ai_chart():
                donut_chart_with_labels(
                    ai_pct, "category", "pct",
                    "Currently using AI",
                    exclude_label_categories=["Not sure"]  # <-- remove slice text overlay for Not sure
                )
            render_container_if(ai_has, ai_chart)

        create_section_header("Common tools used to manage partnerships (multi-select)")
        tools_substr = "What tools do you currently use to manage your partnerships?"
        tools_pct = multi_select_pct(flt, contains_substring=tools_substr)
        tools_has = not tools_pct.empty
        def tools_chart():
            bar_chart_from_pct(
                tools_pct, "option", "pct",
                "Tools used to manage partnerships (categories)",
                horizontal=True
            )
            st.markdown(
                '<div class="chart-caption">'
                "Tool names are shown as generic categories only."
                "</div>",
                unsafe_allow_html=True,
            )
        render_container_if(tools_has, tools_chart)

    # ======================================================
    # MARKETPLACES
    # ======================================================
    with tab_market:
        create_section_header("Listed in marketplaces")

        if COL_MARKETPLACE_LISTED and COL_MARKETPLACE_LISTED in flt.columns:
            mpl_series = normalize_yes_no(flt[COL_MARKETPLACE_LISTED])
            mpl_pct = value_counts_pct(mpl_series)
            mpl_has = not mpl_pct.empty

            def mpl_chart():
                donut_chart_with_labels(
                    mpl_pct, "category", "pct",
                    "Company listed in marketplaces"
                )
            render_container_if(mpl_has, mpl_chart)

        create_section_header("Revenue from marketplaces")
        if COL_MARKETPLACE_REV and COL_MARKETPLACE_REV in flt.columns:
            mp_rev = flt[COL_MARKETPLACE_REV].dropna()
            mp_has = not mp_rev.empty

            def mp_chart():
                as_num = pd.to_numeric(mp_rev, errors="coerce")
                if as_num.notna().any():
                    bins = [0, 5, 15, 30, 50, 9999]
                    labels = ["Less than 5%", "5–15%", "15–30%", "30–50%", "More than 50%"]
                    binned = pd.cut(as_num, bins=bins, labels=labels, include_lowest=True, right=False)
                    mp_rev_pct = value_counts_pct(binned).rename(columns={"category": "bin"})
                    if not mp_rev_pct.empty:
                        bar_chart_from_pct(mp_rev_pct, "bin", "pct", "Marketplace revenue share", horizontal=False)
                else:
                    mp_rev_pct = value_counts_pct(mp_rev.astype(str))
                    if not mp_rev_pct.empty:
                        bar_chart_from_pct(mp_rev_pct, "category", "pct", "Marketplace revenue share", horizontal=True)

                st.markdown(
                    '<div class="chart-caption">'
                    "No specific marketplace names are displayed."
                    "</div>",
                    unsafe_allow_html=True,
                )
            render_container_if(mp_has, mp_chart)

    # ======================================================
    # PARTNER IMPACT
    # ======================================================
    with tab_impact:
        create_section_header("Partner influence and ecosystem impact")
        influence_substr = "Besides Sourced Revenue, how else does your company measure partner influence impact?"
        infl_pct = multi_select_pct(flt, contains_substring=influence_substr)
        infl_has = not infl_pct.empty
        def infl_chart():
            bar_chart_from_pct(
                infl_pct, "option", "pct",
                "Partner influence measurement methods",
                horizontal=True
            )
        render_container_if(infl_has, infl_chart)

        create_section_header("Partnership ecosystem (types)")
        types_substr = "Which of the following Partnership types does your company have?"
        types_pct2 = multi_select_pct(flt, contains_substring=types_substr)
        types_has2 = not types_pct2.empty
        def types2_chart():
            bar_chart_from_pct(
                types_pct2, "option", "pct",
                "Partnership types in place today",
                horizontal=True
            )
        render_container_if(types_has2, types2_chart)

    # ---- Footer ----
    st.markdown(
        """
        <div class="footer">
            <strong>SOPL 2025 Insights Platform</strong> • Partnership analytics and strategic insights<br>
            <span style="color: #94a3b8; font-size: 0.8rem;">
                Data sourced from State of Partnership Leaders Survey
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
