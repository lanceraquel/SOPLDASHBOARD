import altair as alt
import pandas as pd
import pydeck as pdk  # still safe to keep even if not used
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

    rows = []
    for c in cols:
        selected = selection_counts[c]
        pct = (selected / total_selections * 100.0) if total_selections > 0 else 0.0

        label = c.split("_", 1)[1] if "_" in c else c
        rows.append(
            {
                "option": label,
                "pct": pct,
                "count": selected,
                "total_selections": total_selections,
            }
        )

    out = pd.DataFrame(rows)
    out = out.sort_values("pct", ascending=False)
    return out


def create_section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def donut_chart_with_labels(df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str):
    if df_pct.empty:
        st.info("No responses for this question in the current filter.")
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)
    data["PercentLabel"] = data["Percent"].map(lambda v: f"{v:.1f}%")

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
    text = base.mark_text(
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
        st.info("No responses for this question in the current filter.")
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
        st.info("No win-rate responses in the current filter.")
        return

    bins = list(range(0, 101, 10))
    labels = [f"{b}–{b+10}%" for b in bins[:-1]]
    binned = pd.cut(series, bins=bins, labels=labels, include_lowest=True, right=False)
    pct_df = value_counts_pct(binned).rename(columns={"category": "bin", "pct": "pct"})

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


def kpi_value_str(pct: float | None) -> str:
    if pct is None:
        return "—"
    return f"{pct:.1f}%"


def kpi_card(title: str, value: str, subtitle: str | None = None, accent: bool = False):
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


def find_col(df: pd.DataFrame, exact: str | None = None, substrings: list[str] | None = None):
    """Find a single column by exact name or by containing any substring."""
    if exact and exact in df.columns:
        return exact
    if substrings:
        for s in substrings:
            matches = [c for c in df.columns if s in c]
            if matches:
                return matches[0]
    return None


def render_chart_container(fn):
    """Render a chart inside a container ONLY if the chart function returns something."""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fn()
    st.markdown("</div>", unsafe_allow_html=True)

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

    # ---- Boss welcome paragraph (persistent) ----
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

    # ---- Assistant at top (smaller) ----
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

    # Column names used in the dashboard (keep curly apostrophes – match sheet where possible)
    COL_REGION = "Please select the region where your company is headquartered."
    COL_INDUSTRY = "What industry sector does your company operate in?"
    COL_REVENUE = "What is your company’s estimated annual revenue?"
    COL_EMPLOYEES = "What is your company’s total number of employees?"
    COL_DEAL_SIZE = "How does your average deal size involving partners compare to direct or non-partner deals?"
    COL_CAC = "How does your customer acquisition cost (CAC) from partners compared to direct sales and marketing?"
    COL_SALES_CYCLE = "How does your partner-led sales cycle compare to your direct sales cycle?"
    COL_WIN_RATE = "What’s your win rate for deals where partners are involved?"

    # New question columns (exact if present; otherwise substring search)
    COL_PRIMARY_GOAL = find_col(
        df,
        exact="What is your team’s main goal for partnerships in the next 12 months?",
        substrings=["main goal for partnerships in the next 12 months"]
    )
    COL_EXEC_EXPECT = find_col(
        df,
        exact="Which of the following best describes your executive team’s expectations of partnerships?",
        substrings=["executive team’s expectations of partnerships"]
    )
    COL_EXPECTED_REV = find_col(
        df,
        exact="On average, what percentage of your company’s revenue is expected to come from partnerships in the next 12 months?",
        substrings=["expected to come from partnerships in the next 12 months"]
    )
    COL_RETENTION = find_col(
        df,
        exact="What is your retention rate for partner-referred customers?",
        substrings=["retention rate for partner-referred customers"]
    )
    COL_MOST_IMPACTFUL_TYPE = find_col(
        df,
        exact="Which of the partnership types you selected above has the most impact on your organization?",
        substrings=["most impact on your organization", "most impactful"]
    )
    COL_BIGGEST_CHALLENGE = find_col(
        df,
        exact="What’s your biggest challenge in scaling your partner program?",
        substrings=["biggest challenge in scaling your partner program"]
    )
    COL_MISS_GOALS_REASON = find_col(
        df,
        exact="What is the most likely reason your Partnerships team could miss its goals in the next 12 months?",
        substrings=["most likely reason your Partnerships team could miss its goals"]
    )
    COL_TEAM_SIZE = find_col(
        df,
        exact="How many people are on your Partnerships team?",
        substrings=["people are on your Partnerships team"]
    )
    COL_BUDGET = find_col(
        df,
        exact="What is the size of your Partnerships team’s annual budget (including headcount)?",
        substrings=["annual budget", "Partnerships team’s annual budget"]
    )
    COL_USE_TECH = find_col(
        df,
        exact="Do you currently use any technology or automation tools to manage your partner ecosystem?",
        substrings=["technology or automation tools to manage your partner ecosystem"]
    )
    COL_USE_AI = find_col(
        df,
        exact="Are you currently using AI in your partner organization?",
        substrings=["using AI in your partner organization"]
    )
    COL_MARKETPLACE_LISTED = find_col(
        df,
        substrings=["marketplace", "listed in at least one third-party marketplace"]
    )
    COL_MARKETPLACE_REV = find_col(
        df,
        exact="What percentage of your total revenue comes through cloud marketplaces?",
        substrings=["revenue comes through cloud marketplaces"]
    )

    # Normalized region
    if COL_REGION in df.columns:
        df = df.copy()
        df["RegionStd"] = df[COL_REGION].map(normalize_region_label)
    else:
        df["RegionStd"] = None

    # ---- Sidebar filters ----
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

    # ---- About section (persistent, per Tai) ----
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

    # ---- Tabs (Overview + Geography removed) ----
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
    # PERFORMANCE TAB
    # ======================================================
    with tab_perf:
        create_section_header("Partner performance metrics")

        p1, p2 = st.columns(2)
        with p1:
            if COL_DEAL_SIZE in flt.columns:
                def _chart():
                    ds_pct = value_counts_pct(flt[COL_DEAL_SIZE])
                    bar_chart_from_pct(ds_pct, "category", "pct", "Average deal size: partner vs direct", horizontal=True)
                render_chart_container(_chart)

        with p2:
            if COL_CAC in flt.columns:
                def _chart():
                    cac_pct = value_counts_pct(flt[COL_CAC])
                    bar_chart_from_pct(cac_pct, "category", "pct", "Partner-sourced CAC vs direct", horizontal=True)
                render_chart_container(_chart)

        create_section_header("Sales cycle and win rate")

        p3, p4 = st.columns(2)
        with p3:
            if COL_SALES_CYCLE in flt.columns:
                def _chart():
                    sc_pct = value_counts_pct(flt[COL_SALES_CYCLE])
                    bar_chart_from_pct(sc_pct, "category", "pct", "Partner-led sales cycle vs direct", horizontal=True)
                render_chart_container(_chart)

        with p4:
            if COL_WIN_RATE in flt.columns:
                def _chart():
                    win_rate_distribution_pct(flt, COL_WIN_RATE)
                render_chart_container(_chart)

        create_section_header("Retention of partner-referred customers")
        if COL_RETENTION and COL_RETENTION in flt.columns:
            def _chart():
                ret_series = pd.to_numeric(flt[COL_RETENTION], errors="coerce")
                if ret_series.notna().any():
                    bins = [0, 51, 76, 96, 101, 9999]
                    labels = ["0–50%", "51–75%", "76–95%", "96–100%", "More than 100%"]
                    binned = pd.cut(ret_series, bins=bins, labels=labels, include_lowest=True, right=False)
                    ret_pct = value_counts_pct(binned).rename(columns={"category": "bin"})
                    bar_chart_from_pct(ret_pct, "bin", "pct", "Retention rate distribution", horizontal=False)
                else:
                    ret_pct = value_counts_pct(flt[COL_RETENTION].astype(str))
                    bar_chart_from_pct(ret_pct, "category", "pct", "Retention rate distribution", horizontal=True)
            render_chart_container(_chart)

    # ======================================================
    # STRATEGIC DIRECTION TAB
    # ======================================================
    with tab_strategy:
        create_section_header("Primary goal for partnerships (next 12 months)")
        if COL_PRIMARY_GOAL and COL_PRIMARY_GOAL in flt.columns:
            def _chart():
                pg_pct = value_counts_pct(flt[COL_PRIMARY_GOAL])
                bar_chart_from_pct(pg_pct, "category", "pct", "Primary goal for partnerships", horizontal=True)
            render_chart_container(_chart)
        else:
            st.info("Primary goal question not detected in the current dataset.")

        create_section_header("Executive expectations of partnerships")
        if COL_EXEC_EXPECT and COL_EXEC_EXPECT in flt.columns:
            def _chart():
                ex_pct = value_counts_pct(flt[COL_EXEC_EXPECT])
                bar_chart_from_pct(ex_pct, "category", "pct", "Executive expectations", horizontal=True)
            render_chart_container(_chart)
        else:
            st.info("Executive expectations question not detected in the current dataset.")

        create_section_header("Expected revenue from partnerships (next 12 months)")
        if COL_EXPECTED_REV and COL_EXPECTED_REV in flt.columns:
            def _chart():
                exp = flt[COL_EXPECTED_REV].dropna()
                as_num = pd.to_numeric(exp, errors="coerce")
                if as_num.notna().any():
                    bins = [0, 50, 75, 100, 9999]
                    labels = ["Less than 50%", "50–75%", "75–100%", "More than 100%"]
                    binned = pd.cut(as_num, bins=bins, labels=labels, include_lowest=True, right=False)
                    exp_pct = value_counts_pct(binned).rename(columns={"category": "bin"})
                    bar_chart_from_pct(exp_pct, "bin", "pct", "Expected revenue share from partnerships", horizontal=False)
                else:
                    exp_pct = value_counts_pct(exp.astype(str))
                    bar_chart_from_pct(exp_pct, "category", "pct", "Expected revenue share from partnerships", horizontal=True)
            render_chart_container(_chart)
        else:
            st.info("Expected revenue share question not detected in the current dataset.")

    # ======================================================
    # PORTFOLIO TAB
    # ======================================================
    with tab_portfolio:
        create_section_header("Partnership types currently in use")
        types_substr = "Which of the following Partnership types does your company have?"
        types_pct = multi_select_pct(flt, contains_substring=types_substr)
        if not types_pct.empty:
            def _chart():
                bar_chart_from_pct(types_pct, "option", "pct", "Partnership types in place today", horizontal=True)
            render_chart_container(_chart)
        else:
            st.info("No partnership-type multi-select columns detected for the current dataset.")

        create_section_header("Most impactful partnership type")
        if COL_MOST_IMPACTFUL_TYPE and COL_MOST_IMPACTFUL_TYPE in flt.columns:
            def _chart():
                mi_pct = value_counts_pct(flt[COL_MOST_IMPACTFUL_TYPE])
                bar_chart_from_pct(mi_pct, "category", "pct", "Most impactful partnership type", horizontal=True)
            render_chart_container(_chart)
        else:
            st.info("Most impactful partnership type question not detected in the current dataset.")

    # ======================================================
    # OPERATIONAL CHALLENGES TAB
    # ======================================================
    with tab_ops:
        create_section_header("Biggest challenge in scaling the partner program")
        if COL_BIGGEST_CHALLENGE and COL_BIGGEST_CHALLENGE in flt.columns:
            def _chart():
                bc_pct = value_counts_pct(flt[COL_BIGGEST_CHALLENGE])
                bar_chart_from_pct(bc_pct, "category", "pct", "Biggest scaling challenge", horizontal=True)
            render_chart_container(_chart)
        else:
            st.info("Biggest challenge question not detected in the current dataset.")

        create_section_header("Most likely reason for missing goals (next 12 months)")
        if COL_MISS_GOALS_REASON and COL_MISS_GOALS_REASON in flt.columns:
            def _chart():
                mg_pct = value_counts_pct(flt[COL_MISS_GOALS_REASON])
                bar_chart_from_pct(mg_pct, "category", "pct", "Reason goals may be missed", horizontal=True)
            render_chart_container(_chart)
        else:
            st.info("Missing-goals reason question not detected in the current dataset.")

    # ======================================================
    # TEAM & INVESTMENT TAB
    # ======================================================
    with tab_team:
        create_section_header("Partnerships team size")
        if COL_TEAM_SIZE and COL_TEAM_SIZE in flt.columns:
            def _chart():
                ts_pct = value_counts_pct(flt[COL_TEAM_SIZE])
                bar_chart_from_pct(ts_pct, "category", "pct", "Team size (people)", horizontal=True)
            render_chart_container(_chart)
        else:
            st.info("Team size question not detected in the current dataset.")

        create_section_header("Annual partnerships budget (including headcount)")
        if COL_BUDGET and COL_BUDGET in flt.columns:
            def _chart():
                bud_series = flt[COL_BUDGET].dropna().astype(str)
                bud_series = bud_series[~bud_series.str.contains("I don’t have this data|I don't have this data", case=False, na=False)]
                bud_pct = value_counts_pct(bud_series)
                bar_chart_from_pct(bud_pct, "category", "pct", "Annual partnerships budget", horizontal=True)
                st.markdown(
                    '<div class="chart-caption">'
                    "Percentages exclude respondents who selected “I don’t have this data.”"
                    "</div>",
                    unsafe_allow_html=True,
                )
            render_chart_container(_chart)
        else:
            st.info("Budget size question not detected in the current dataset.")

    # ======================================================
    # TECHNOLOGY & AI TAB
    # ======================================================
    with tab_tech:
        create_section_header("Use of technology / automation")
        if COL_USE_TECH and COL_USE_TECH in flt.columns:
            def _chart():
                ut_pct = value_counts_pct(flt[COL_USE_TECH])
                donut_chart_with_labels(ut_pct, "category", "pct", "Currently using partner tech/automation")
            render_chart_container(_chart)
        else:
            st.info("Technology/automation usage question not detected in the current dataset.")

        create_section_header("Use of AI in the partner organization")
        if COL_USE_AI and COL_USE_AI in flt.columns:
            def _chart():
                ai_pct = value_counts_pct(flt[COL_USE_AI])
                donut_chart_with_labels(ai_pct, "category", "pct", "Currently using AI")
            render_chart_container(_chart)
        else:
            st.info("AI usage question not detected in the current dataset.")

        create_section_header("Common tools used to manage partnerships (multi-select)")
        tools_substr = "What tools do you currently use to manage your partnerships?"
        tools_pct = multi_select_pct(flt, contains_substring=tools_substr)
        if not tools_pct.empty:
            def _chart():
                bar_chart_from_pct(tools_pct, "option", "pct", "Tools used to manage partnerships (categories)", horizontal=True)
                st.markdown(
                    '<div class="chart-caption">'
                    "Tool names are shown as generic categories only."
                    "</div>",
                    unsafe_allow_html=True,
                )
            render_chart_container(_chart)
        else:
            st.info("No tools multi-select columns detected for the current dataset.")

    # ======================================================
    # MARKETPLACES TAB
    # ======================================================
    with tab_market:
        create_section_header("Listed in marketplaces")
        if COL_MARKETPLACE_LISTED and COL_MARKETPLACE_LISTED in flt.columns:
            def _chart():
                mp_listed_pct = value_counts_pct(flt[COL_MARKETPLACE_LISTED])
                donut_chart_with_labels(mp_listed_pct, "category", "pct", "Company listed in marketplaces")
            render_chart_container(_chart)
        else:
            st.info("Marketplace listing question not detected in the current dataset.")

        create_section_header("Revenue from marketplaces")
        if COL_MARKETPLACE_REV and COL_MARKETPLACE_REV in flt.columns:
            def _chart():
                mp_rev = flt[COL_MARKETPLACE_REV].dropna()
                as_num = pd.to_numeric(mp_rev, errors="coerce")
                if as_num.notna().any():
                    bins = [0, 5, 15, 30, 50, 9999]
                    labels = ["Less than 5%", "5–15%", "15–30%", "30–50%", "More than 50%"]
                    binned = pd.cut(as_num, bins=bins, labels=labels, include_lowest=True, right=False)
                    mp_rev_pct = value_counts_pct(binned).rename(columns={"category": "bin"})
                    bar_chart_from_pct(mp_rev_pct, "bin", "pct", "Marketplace revenue share", horizontal=False)
                else:
                    mp_rev_pct = value_counts_pct(mp_rev.astype(str))
                    bar_chart_from_pct(mp_rev_pct, "category", "pct", "Marketplace revenue share", horizontal=True)
                st.markdown(
                    '<div class="chart-caption">'
                    "No specific marketplace names are displayed."
                    "</div>",
                    unsafe_allow_html=True,
                )
            render_chart_container(_chart)
        else:
            st.info("Marketplace revenue question not detected in the current dataset.")

    # ======================================================
    # PARTNER IMPACT TAB (kept & expanded)
    # ======================================================
    with tab_impact:
        create_section_header("Partner influence and ecosystem impact")

        influence_substr = (
            "Besides Sourced Revenue, how else does your company measure partner influence impact?"
        )
        infl_pct = multi_select_pct(flt, contains_substring=influence_substr)
        if not infl_pct.empty:
            def _chart():
                bar_chart_from_pct(
                    infl_pct, "option", "pct", "Partner influence measurement methods", horizontal=True
                )
            render_chart_container(_chart)
        else:
            st.info("No influence-impact multi-select columns detected for the current dataset.")

        create_section_header("Partnership ecosystem (types)")
        types_substr = "Which of the following Partnership types does your company have?"
        types_pct = multi_select_pct(flt, contains_substring=types_substr)
        if not types_pct.empty:
            def _chart():
                bar_chart_from_pct(
                    types_pct, "option", "pct", "Partnership types in place today", horizontal=True
                )
            render_chart_container(_chart)
        else:
            st.info("No partnership-type multi-select columns detected for the current dataset.")

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
