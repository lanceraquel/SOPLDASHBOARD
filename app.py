import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components
import re

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SOPL 2025 - Partnership Analytics",
    page_icon="PL_transparent_1080.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== BRAND COLORS ====================
PL_CORE = {
    "amaranth": "#EC3D72",
    "casablanca": "#F9A644",
    "minsk": "#3B308F",
    "cerulean": "#00CCFD",
}
PL_TINTS = {
    "amaranth_light": "#F25A8A",
    "casablanca_light": "#FBB85F",
    "minsk_light": "#5146A1",
    "cerulean_light": "#33D6FF",
}

PL_COLORS = [
    PL_CORE["minsk"],
    PL_CORE["amaranth"],
    PL_CORE["casablanca"],
    PL_CORE["cerulean"],
    PL_TINTS["minsk_light"],
    PL_TINTS["amaranth_light"],
    PL_TINTS["casablanca_light"],
    PL_TINTS["cerulean_light"],
]

TOP_N_DEFAULT = 4  # default max categories per chart


# ==================== ENHANCED CSS / LIGHT THEME ====================
st.markdown(
    """
<style>
html, body, .stApp {
    background-color: #ffffff !important;
    color: #020617;
}
[data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
}
main.block-container {
    background-color: #ffffff !important;
    padding-top: 1rem;
}
[data-testid="stSidebar"] {
    background-color: #0b1120 !important;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] .stMultiSelect {
    margin-bottom: 1rem;
}
:root {
    --bg: #ffffff;
    --panel: #ffffff;
    --card: #ffffff;
    --muted: #64748b;
    --text: #020617;
    --accent: #3b308f;
    --success: #16a34a;
    --warning: #f59e0b;
    --danger: #ef4444;
    --glass: rgba(15,23,42,0.04);
}
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
.sub-header {
    font-size: 1.25rem;
    color: #64748b !important;
    margin-top: 8px;
    font-weight: 400;
}
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
.chart-container {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(15,23,42,0.03);
    margin-bottom: 1.5rem;
}
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.5rem;
    margin: 1.5rem 0;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    border-radius: 10px;
    border-color: #ec3d72;
    transition: all 0.2s ease;
    background-color: #020617;
    color: #f9fafb !important;
}
.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: #f97373;
    box-shadow: 0 0 0 3px rgba(236, 61, 114, 0.4);
}
.stMultiSelect [data-baseweb="tag"] {
    background-color: #ec3d72 !important;
    color: #ffffff !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #020617;
    padding: 4px;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.95rem;
    font-weight: 600;
    border-radius: 999px;
    padding: 8px 18px;
    transition: all 0.2s ease;
    border: none;
}
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
.stTabs [data-baseweb="tab"][aria-selected="true"] * {
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab"][aria-selected="false"] {
    background-color: transparent;
    color: #e5e7eb !important;
}
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
.vega-embed details > summary svg {
    stroke: #020617 !important;
    fill: #020617 !important;
}
.vega-embed details > summary {
    background-color:#ffffff !important;
    border-radius:50% !important;
    border:1px solid #e2e8f0 !important;
}
.vega-embed details[open] > summary {
    box-shadow:0 2px 6px rgba(15,23,42,0.2);
}
.vega-embed text {
    font-size: 11px;
}
.footer {
    text-align: center;
    color: #64748b !important;
    font-size: 0.9rem;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
}
.assistant-header {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1.5rem 0 1rem 0;
    border: 1px solid #e2e8f0;
}
@media (max-width: 768px) {
    .main-header {
        font-size: 2.2rem;
    }
    .kpi-grid {
        grid-template-columns: 1fr;
    }
}
/* Kill empty rectangles */
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

# ==================== ALTAIR THEME ====================
def atlas_light_theme():
    return {
        "config": {
            "view": {"stroke": "transparent"},
            "background": "#ffffff",
            "range": {
                "category": PL_COLORS,
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
            "header": {"labelFontSize": 12, "titleFontSize": 14},
        }
    }

alt.themes.register("atlas_light", atlas_light_theme)
alt.themes.enable("atlas_light")

alt.data_transformers.disable_max_rows()
alt.renderers.set_embed_options(
    actions={"export": True, "source": False, "compiled": False, "editor": False}
)

# ==================== DATA LOADER ====================
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
    """Percentages based only on non-blank responses."""
    s = series.dropna()
    if s.empty:
        return pd.DataFrame(columns=["category", "pct"])
    counts = s.value_counts()
    total_non_null = len(s)
    pct = (counts / total_non_null) * 100.0
    out = pct.reset_index()
    out.columns = ["category", "pct"]
    return out


def binned_pct_custom(series: pd.Series, edges: list[float], labels: list[str]) -> pd.DataFrame:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return pd.DataFrame(columns=["bin", "pct"])
    binned = pd.cut(s, bins=edges, labels=labels, include_lowest=True, right=False)
    pct_df = value_counts_pct(binned).rename(columns={"category": "bin"})
    return pct_df


def create_section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def donut_chart_clean(df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str):
    """Donut chart without % overlays."""
    if df_pct.empty:
        return
    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)

    base = alt.Chart(data).encode(
        theta=alt.Theta("Percent:Q", stack=True),
        color=alt.Color(
            f"{cat_field}:N",
            legend=alt.Legend(title=None, orient="right"),
            scale=alt.Scale(range=PL_COLORS),
        ),
        tooltip=[f"{cat_field}:N", alt.Tooltip("Percent:Q", format=".1f")],
    )

    donut = base.mark_arc(innerRadius=70, stroke="#fff", strokeWidth=2)

    chart = donut.properties(
        width=400,
        height=400,
        title=alt.TitleParams(title, fontSize=16, fontWeight=700, anchor="start"),
    ).configure_view(strokeWidth=0)

    st.altair_chart(chart, use_container_width=True)


def bar_chart_from_pct(
    df_pct: pd.DataFrame,
    cat_field: str,
    pct_field: str,
    title: str,
    horizontal: bool = True,
    max_categories: int | None = TOP_N_DEFAULT,
    min_pct: float | None = None,
):
    """
    Branded bar chart with multi-color bars and % labels.
    """
    if df_pct.empty:
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)

    data = data.sort_values("Percent", ascending=False)
    if min_pct is not None:
        data = data[data["Percent"] >= min_pct]
    if max_categories is not None and len(data) > max_categories:
        data = data.iloc[:max_categories]

    if data.empty:
        return

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
                axis=alt.Axis(labelLimit=320, labelOverlap=False, labelFontSize=11),
            ),
            color=alt.Color(
                f"{cat_field}:N",
                legend=None,
                scale=alt.Scale(range=PL_COLORS),
            ),
            tooltip=[
                f"{cat_field}:N",
                alt.Tooltip("Percent:Q", format=".1f", title="Percentage"),
            ],
        )

        bars = base.mark_bar(cornerRadius=4)
        labels = base.mark_text(
            align="left",
            baseline="middle",
            dx=4,
            color="#020617",
            fontWeight=600,
        ).encode(text=alt.Text("PercentLabel:N"))

        chart = (bars + labels).properties(
            height=max(260, 32 * len(data)),
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
            color=alt.Color(
                f"{cat_field}:N",
                legend=None,
                scale=alt.Scale(range=PL_COLORS),
            ),
            tooltip=[
                f"{cat_field}:N",
                alt.Tooltip("Percent:Q", format=".1f", title="Percentage"),
            ],
        )

        bars = base.mark_bar(cornerRadius=4)
        labels = base.mark_text(
            align="center",
            baseline="bottom",
            dy=-6,
            color="#020617",
            fontWeight=600,
        ).encode(text=alt.Text("PercentLabel:N"))

        chart = (bars + labels).properties(
            height=400,
            title=alt.TitleParams(title, fontSize=16, fontWeight=700, anchor="start"),
        )

    st.altair_chart(chart, use_container_width=True)


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


def find_col(df: pd.DataFrame, exact: str | None = None, substrings: list[str] | None = None):
    if exact and exact in df.columns:
        return exact
    if substrings:
        for s in substrings:
            matches = [c for c in df.columns if s in c]
            if matches:
                return matches[0]
    return None


def normalize_yes_no(series: pd.Series) -> pd.Series:
    s = series.dropna()
    if s.empty:
        return series

    coerced = pd.to_numeric(series, errors="coerce")
    if coerced.notna().any() and coerced.dropna().isin([0, 1]).all():
        return coerced.map({1: "Yes", 0: "No"})

    lower = series.astype(str).str.strip().str.lower()
    mapping = {
        "1": "Yes",
        "1.0": "Yes",
        "true": "Yes",
        "yes": "Yes",
        "y": "Yes",
        "0": "No",
        "0.0": "No",
        "false": "No",
        "no": "No",
        "n": "No",
    }
    mapped = lower.map(mapping)
    return mapped.where(mapped.notna(), series.astype(str))


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


def clean_question_title(col_name: str) -> str:
    """Remove _Column2 etc and stray underscores in question labels."""
    title = re.sub(r"_Column\\d+", "", col_name)
    title = title.replace("_", " ")
    title = re.sub(r"\\s+", " ", title).strip()
    return title


def extract_platform_tool(col_name: str) -> str | None:
    """
    For columns like:
    'Which platforms do you plan to use more, less, or steady? _Amplify_Column2'
    return 'Amplify'.
    """
    if "Which platforms do you plan to use more, less, or steady?" not in col_name:
        return None
    # Split at '?'
    parts = col_name.split("?", 1)
    if len(parts) != 2:
        return None
    tail = parts[1]
    # Remove Column suffix
    tail = re.sub(r"_Column\\d+", "", tail)
    # Strip underscores and spaces
    tail = tail.strip(" _-")
    if not tail:
        return None
    # Clean remaining underscores/brackets
    tail = tail.replace("_", " ")
    tail = re.sub(r"\\s+", " ", tail)
    return tail.strip()


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

    # ---- Welcome text (Tai copy) ----
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

    # ---- Assistant widget ----
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
    COL_PARTNER_FOCUS = find_col(df, substrings=["focus next 12 months"])
    COL_STRATEGIC_BET = find_col(df, substrings=["Strategic bet", "strategic bet next 12 months"])
    COL_FORECAST_PERF = find_col(df, substrings=["Forecasted performance", "forecasted performance"])

    # RegionStd helper
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
            "Less than $50 million",
            "$50M – $250M",
            "$250M – $1B",
            "$1B – $10B",
            "More than $10B",
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
            "Less than 100 employees",
            "100 – 500 employees",
            "501 – 5,000 employees",
            "More than 5,000 employees",
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

    # ---- About section ----
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
  the charts in every tab update automatically to reflect the current selection.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    # Columns already wired to specific visuals
    used_cols = {
        c
        for c in [
            COL_REGION,
            COL_INDUSTRY,
            COL_REVENUE,
            COL_EMPLOYEES,
            COL_DEAL_SIZE,
            COL_CAC,
            COL_SALES_CYCLE,
            COL_WIN_RATE,
            COL_PRIMARY_GOAL,
            COL_EXEC_EXPECT,
            COL_EXPECTED_REV,
            COL_RETENTION,
            COL_MOST_IMPACTFUL_TYPE,
            COL_BIGGEST_CHALLENGE,
            COL_MISS_GOALS_REASON,
            COL_TEAM_SIZE,
            COL_BUDGET,
            COL_USE_TECH,
            COL_USE_AI,
            COL_MARKETPLACE_LISTED,
            COL_MARKETPLACE_REV,
            COL_PARTNER_FOCUS,
            COL_STRATEGIC_BET,
            COL_FORECAST_PERF,
            "RegionStd",
        ]
        if c is not None
    }

    # ---- Tabs ----
    tab_firmo, tab_perf, tab_strategy, tab_portfolio, tab_ops, tab_team, tab_tech, tab_market, tab_extra = st.tabs(
        [
            "Firmographics",
            "Performance",
            "Strategic Direction",
            "Partnership Portfolio",
            "Challenges & Risks",
            "Team & Investment",
            "Technology & AI",
            "Marketplaces",
            "Additional Insights",
        ]
    )

    # ======================================================
    # FIRMOGRAPHICS
    # ======================================================
    with tab_firmo:
        create_section_header("Company profile")

        reg_has = "RegionStd" in flt.columns and not flt["RegionStd"].dropna().empty

        def reg_chart():
            reg_pct = value_counts_pct(flt["RegionStd"])
            donut_chart_clean(reg_pct, "category", "pct", "HQ region")

        rev_has = COL_REVENUE in flt.columns and not flt[COL_REVENUE].dropna().empty

        def rev_chart():
            rev_pct = value_counts_pct(flt[COL_REVENUE])
            order = [
                "Less than $50 million",
                "$50M – $250M",
                "$250M – $1B",
                "$1B – $10B",
                "More than $10B",
            ]
            rev_pct["category"] = pd.Categorical(rev_pct["category"], categories=order, ordered=True)
            rev_pct_sorted = rev_pct.sort_values("category")
            donut_chart_clean(rev_pct_sorted, "category", "pct", "Company annual revenue")

        two_up_or_full(reg_has, reg_chart, rev_has, rev_chart)

        emp_has = COL_EMPLOYEES in flt.columns and not flt[COL_EMPLOYEES].dropna().empty

        def emp_chart():
            emp_pct = value_counts_pct(flt[COL_EMPLOYEES])
            emp_order = [
                "Less than 100 employees",
                "100 – 500 employees",
                "501 – 5,000 employees",
                "More than 5,000 employees",
            ]
            emp_pct["category"] = pd.Categorical(emp_pct["category"], categories=emp_order, ordered=True)
            emp_pct_sorted = emp_pct.sort_values("category")
            donut_chart_clean(emp_pct_sorted, "category", "pct", "Total employee count")

        ind_has = COL_INDUSTRY in flt.columns and not flt[COL_INDUSTRY].dropna().empty

        def ind_chart():
            ind_pct = value_counts_pct(flt[COL_INDUSTRY])
            donut_chart_clean(ind_pct, "category", "pct", "Industry sector")

        two_up_or_full(emp_has, emp_chart, ind_has, ind_chart)

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
            edges = [0, 25, 50, 75, 101]
            labels = ["0–25%", "26–50%", "51–75%", "76–100%"]
            pct_df = binned_pct_custom(flt[COL_WIN_RATE], edges, labels)
            if pct_df.empty:
                return
            bar_chart_from_pct(
                pct_df,
                "bin",
                "pct",
                "Win rate on partner-involved deals",
                horizontal=False,
                max_categories=TOP_N_DEFAULT,
            )
            st.markdown(
                '<div class="chart-caption" style="text-align:center;">'
                "Percentages are based on respondents who provided a win-rate estimate."
                "</div>",
                unsafe_allow_html=True,
            )

        two_up_or_full(sc_has, sc_chart, wr_has, wr_chart)

        create_section_header("Retention of partner-referred customers")
        if COL_RETENTION and COL_RETENTION in flt.columns:
            ret_has = not flt[COL_RETENTION].dropna().empty

            def ret_chart():
                edges = [0, 50, 75, 95, 100, 201]
                labels = ["0–50%", "51–75%", "76–95%", "96–100%", "More than 100%"]
                pct_df = binned_pct_custom(flt[COL_RETENTION], edges, labels)
                if pct_df.empty:
                    return
                bar_chart_from_pct(
                    pct_df,
                    "bin",
                    "pct",
                    "Retention of partner-referred customers",
                    horizontal=False,
                    max_categories=5,
                )
                st.markdown(
                    '<div class="chart-caption" style="text-align:center;">'
                    "Percentages are based on respondents who provided a retention estimate."
                    "</div>",
                    unsafe_allow_html=True,
                )

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
                edges = [0, 50, 75, 100, 201]
                labels = ["Less than 50%", "50–75%", "75–100%", "More than 100%"]
                pct_df = binned_pct_custom(flt[COL_EXPECTED_REV], edges, labels)
                if pct_df.empty:
                    return
                bar_chart_from_pct(
                    pct_df,
                    "bin",
                    "pct",
                    "Expected share of revenue from partnerships",
                    horizontal=False,
                    max_categories=4,
                )

            render_container_if(er_has, er_chart)

        create_section_header("Forward-looking strategy")

        if COL_PARTNER_FOCUS and COL_PARTNER_FOCUS in flt.columns:
            pf_has = not flt[COL_PARTNER_FOCUS].dropna().empty

            def pf_chart():
                pf_pct = value_counts_pct(flt[COL_PARTNER_FOCUS])
                bar_chart_from_pct(
                    pf_pct,
                    "category",
                    "pct",
                    "Partnership focus in the next 12 months",
                    horizontal=True,
                )

            render_container_if(pf_has, pf_chart)

        if COL_STRATEGIC_BET and COL_STRATEGIC_BET in flt.columns:
            sb_has = not flt[COL_STRATEGIC_BET].dropna().empty

            def sb_chart():
                sb_pct = value_counts_pct(flt[COL_STRATEGIC_BET])
                bar_chart_from_pct(
                    sb_pct,
                    "category",
                    "pct",
                    "Strategic bet for the next 12 months",
                    horizontal=True,
                )

            render_container_if(sb_has, sb_chart)

        if COL_FORECAST_PERF and COL_FORECAST_PERF in flt.columns:
            fp_has = not flt[COL_FORECAST_PERF].dropna().empty

            def fp_chart():
                fp_pct = value_counts_pct(flt[COL_FORECAST_PERF])
                bar_chart_from_pct(
                    fp_pct,
                    "category",
                    "pct",
                    "Forecasted performance vs goals",
                    horizontal=True,
                )

            render_container_if(fp_has, fp_chart)

    # ======================================================
    # PARTNERSHIP PORTFOLIO
    # ======================================================
    with tab_portfolio:
        create_section_header("Most impactful partnership type")
        if COL_MOST_IMPACTFUL_TYPE and COL_MOST_IMPACTFUL_TYPE in flt.columns:
            mi_has = not flt[COL_MOST_IMPACTFUL_TYPE].dropna().empty

            def mi_chart():
                mi_pct = value_counts_pct(flt[COL_MOST_IMPACTFUL_TYPE])
                donut_chart_clean(mi_pct, "category", "pct", "Most impactful partnership type")

            render_container_if(mi_has, mi_chart)

    # ======================================================
    # CHALLENGES & RISKS
    # ======================================================
    with tab_ops:
        create_section_header("Biggest challenge in scaling the partner program")
        if COL_BIGGEST_CHALLENGE and COL_BIGGEST_CHALLENGE in flt.columns:
            bc_has = not flt[COL_BIGGEST_CHALLENGE].dropna().empty

            def bc_chart():
                bc_pct = value_counts_pct(flt[COL_BIGGEST_CHALLENGE])
                bar_chart_from_pct(
                    bc_pct,
                    "category",
                    "pct",
                    "Biggest challenge in scaling the program",
                    horizontal=True,
                )

            render_container_if(bc_has, bc_chart)

        create_section_header("Most likely reason for missing goals (next 12 months)")
        if COL_MISS_GOALS_REASON and COL_MISS_GOALS_REASON in flt.columns:
            mg_has = not flt[COL_MISS_GOALS_REASON].dropna().empty

            def mg_chart():
                mg_pct = value_counts_pct(flt[COL_MISS_GOALS_REASON])
                bar_chart_from_pct(
                    mg_pct,
                    "category",
                    "pct",
                    "Reason goals may be missed",
                    horizontal=True,
                )

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
                donut_chart_clean(ts_pct, "category", "pct", "Partnerships team size")

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
                bar_chart_from_pct(
                    bud_pct,
                    "category",
                    "pct",
                    "Annual partnerships budget",
                    horizontal=True,
                )
                st.markdown(
                    '<div class="chart-caption">'
                    "Percentages exclude respondents who selected “I don’t have this data.”"
                    "</div>",
                    unsafe_allow_html=True,
                )

            render_container_if(bud_has, bud_chart)

    # ======================================================
    # TECHNOLOGY & AI
    # ======================================================
    with tab_tech:
        create_section_header("Use of technology / automation")
        if COL_USE_TECH and COL_USE_TECH in flt.columns:
            ut_pct = value_counts_pct(flt[COL_USE_TECH])
            ut_has = not ut_pct.empty

            def ut_chart():
                donut_chart_clean(
                    ut_pct,
                    "category",
                    "pct",
                    "Currently using partner tech/automation",
                )

            render_container_if(ut_has, ut_chart)

        create_section_header("Use of AI in the partner organization")
        if COL_USE_AI and COL_USE_AI in flt.columns:
            ai_pct = value_counts_pct(flt[COL_USE_AI])
            ai_has = not ai_pct.empty

            def ai_chart():
                donut_chart_clean(
                    ai_pct,
                    "category",
                    "pct",
                    "Currently using AI in the partner organization",
                )

            render_container_if(ai_has, ai_chart)

        create_section_header("Common tools used to manage partnerships (if present)")
        tools_substr = "What tools do you currently use to manage your partnerships?"
        tools_col = find_col(df, substrings=[tools_substr])
        if tools_col and tools_col in flt.columns:
            tools_series = flt[tools_col]
            tools_pct = value_counts_pct(tools_series)
            tools_has = not tools_pct.empty

            def tools_chart():
                bar_chart_from_pct(
                    tools_pct,
                    "category",
                    "pct",
                    "Tools used to manage partnerships (categories)",
                    horizontal=True,
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
                donut_chart_clean(
                    mpl_pct,
                    "category",
                    "pct",
                    "Company listed in marketplaces",
                )

            render_container_if(mpl_has, mpl_chart)

        create_section_header("Revenue from marketplaces")
        if COL_MARKETPLACE_REV and COL_MARKETPLACE_REV in flt.columns:
            mp_rev = flt[COL_MARKETPLACE_REV].dropna()
            mp_has_any = not mp_rev.empty

            def mp_chart():
                mp_num = pd.to_numeric(mp_rev, errors="coerce")
                if mp_num.notna().sum() > 0 and mp_num.notna().mean() > 0.7:
                    edges = [0, 5, 15, 30, 50, 101]
                    labels = [
                        "Less than 5%",
                        "5–15%",
                        "15–30%",
                        "30–50%",
                        "More than 50%",
                    ]
                    pct_df = binned_pct_custom(mp_num, edges, labels)
                    if pct_df.empty:
                        return
                    bar_chart_from_pct(
                        pct_df,
                        "bin",
                        "pct",
                        "Share of revenue from marketplaces",
                        horizontal=False,
                        max_categories=5,
                    )
                else:
                    cat_pct = value_counts_pct(mp_rev.astype(str))
                    if cat_pct.empty:
                        return
                    bar_chart_from_pct(
                        cat_pct,
                        "category",
                        "pct",
                        "Share of revenue from marketplaces",
                        horizontal=False,
                    )
                st.markdown(
                    '<div class="chart-caption">'
                    "No specific marketplace names are displayed."
                    "</div>",
                    unsafe_allow_html=True,
                )

            render_container_if(mp_has_any, mp_chart)

    # ======================================================
    # ADDITIONAL INSIGHTS
    # ======================================================
    with tab_extra:
        create_section_header("Additional insights across remaining questions")

        skip_substrings = [
            "StartDate",
            "EndDate",
            "Status",
            "IPAddress",
            "Progress",
            "Duration",
            "Finished",
            "RecordedDate",
            "ResponseId",
            "Recipient",
            "LocationLatitude",
            "LocationLongitude",
            "UserLanguage",
            "Close Rates",
            "_Close Rates",
            "close rate",
            "close rates",
            "Other – please specify",
            "Other - please specify",
            "additional feedback or comments you'd like to share",
        ]

        vendor_keywords = [
            "google",
            "salesforce",
            "crossbeam",
            "hubspot",
            "microsoft",
            "aws",
            "azure",
            "gcp",
            "partnerstack",
            "zendesk",
            "slack",
            "oracle",
            "sap",
            "workday",
        ]

        extra_questions: list[dict] = []

        for col in flt.columns:
            if col in used_cols:
                continue
            if any(sub in col for sub in skip_substrings):
                continue
            if col == "RegionStd":
                continue

            series = flt[col]
            s_nonnull = series.dropna()
            if s_nonnull.empty:
                continue

            # skip numeric-only derived % metrics
            numeric_coerced = pd.to_numeric(s_nonnull, errors="coerce")
            if numeric_coerced.notna().mean() > 0.9:
                continue

            # skip questions with too many categories
            n_unique = s_nonnull.astype(str).nunique()
            if n_unique <= 1 or n_unique > 12:
                continue

            lower_vals = s_nonnull.astype(str).str.lower()
            if any(lower_vals.str.contains(kw, na=False).any() for kw in vendor_keywords):
                continue

            cat_pct = value_counts_pct(series)
            if cat_pct.empty:
                continue

            extra_questions.append({"col": col, "pct": cat_pct})

        # limit to first 10 to avoid long scrolling
        extra_questions = extra_questions[:10]

        for item in extra_questions:
            col = item["col"]
            pct_df = item["pct"]
            n_cat = len(pct_df)

            tool_name = extract_platform_tool(col)
            if tool_name:
                title = f"{tool_name} – Which platforms do you plan to use more, less, or steady?"
            else:
                title = clean_question_title(col)

            def make_chart(pct_df=pct_df, title=title, tool_name=tool_name, n_cat=n_cat):
                # mix donut vs bar depending on categories
                if n_cat <= 5:
                    donut_chart_clean(pct_df, "category", "pct", title)
                else:
                    bar_chart_from_pct(
                        pct_df,
                        "category",
                        "pct",
                        title,
                        horizontal=True,
                        max_categories=min(n_cat, TOP_N_DEFAULT),
                    )
                if tool_name:
                    st.markdown(
                        f"<div style='text-align:center;font-weight:600;margin-top:-6px;'>"
                        f"{tool_name}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            render_container_if(True, make_chart)

        if not extra_questions:
            st.info("No additional summarized categorical questions detected beyond the main dashboard sections.")

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
