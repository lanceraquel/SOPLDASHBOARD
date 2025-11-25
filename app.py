import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SOPL 2025 - Partnership Analytics",
    page_icon="PL_transparent_1080.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== GLOBAL BRAND COLORS ====================
PL_COLORS = {
    "amaranth": "#EC3D72",
    "casablanca": "#F9A644",
    "minsk": "#3B308F",
    "cerulean": "#00CCFD",
}

PL_CATEGORY_RANGE = [
    PL_COLORS["minsk"],
    PL_COLORS["amaranth"],
    PL_COLORS["casablanca"],
    PL_COLORS["cerulean"],
    "#291F6A",  # darker minsk
    "#F5276D",  # darker amaranth
    "#F7B86A",  # lighter casablanca
    "#4AD6FF",  # lighter cerulean
]

BANNED_VENDOR_TERMS = [
    "salesforce",
    "google",
    "microsoft",
    "hubspot",
    "partnerstack",
    "crossbeam",
    "impartner",
    "zendesk",
    "workspan",
    "asana",
    "slack",
]


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
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e2e8f0;
}

/* Main title */
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
    font-weight: 800;
    margin-top: 1.8rem;
    margin-bottom: 0.9rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #f1f5f9;
    color: #1e293b !important;
}

/* Chart card */
.chart-container {
    background: white;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(15,23,42,0.03);
    margin-bottom: 1.25rem;
}

/* KPI grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.2rem;
    margin: 1.2rem 0;
}

/* Filters styling */
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

/* Tabs */
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

/* Vega/Altair actions */
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
.vega-embed text {
    font-size: 11px;
}

/* Footer */
.footer {
    text-align: center;
    color: #64748b !important;
    font-size: 0.9rem;
    margin-top: 2.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid #e2e8f0;
}

/* Assistant header */
.assistant-header {
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1.2rem 0 0.8rem 0;
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
            "range": {"category": PL_CATEGORY_RANGE},
            "axis": {
                "labelColor": "#475569",
                "titleColor": "#020617",
                "titleFontWeight": 700,
                "labelFontWeight": 700,
                "gridColor": "#f1f5f9",
                "domainColor": "#d4d4d8",
                "labelLimit": 0,  # no ellipsis; allow full labels
                "labelFontSize": 11,
                "titleFontSize": 12,
            },
            "legend": {
                "labelColor": "#475569",
                "titleColor": "#020617",
                "titleFontWeight": 700,
                "labelFontSize": 11,
                "titleFontSize": 12,
            },
            "title": {
                "color": "#020617",
                "fontSize": 16,
                "fontWeight": 800,
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

# ==================== GOOGLE SHEETS LOADER ====================
@st.cache_data(show_spinner=True)
def load_data() -> pd.DataFrame:
    url = st.secrets.get("gsheet_url", None)
    if not url:
        st.error(
            "❌ Missing gsheet_url in Streamlit secrets. "
            "Add it as `gsheet_url = \"...\"` in your app settings."
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
    Return category + percentage (0–100) for non-null responses.
    % = count(category) / total_non_null * 100.
    """
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
    df: pd.DataFrame,
    contains_substring: str | None = None,
    col_prefix: str | None = None,
    exclude_terms: list[str] | None = None,
) -> pd.DataFrame:
    """
    For Qualtrics-style multi-select (one column per option with 1/0/NaN),
    compute percentage distribution of selections across options.
    Percentages sum to 100 across options.
    """
    if contains_substring:
        cols = [c for c in df.columns if contains_substring.lower() in c.lower()]
    elif col_prefix:
        cols = [c for c in df.columns if c.startswith(col_prefix)]
    else:
        return pd.DataFrame(columns=["option", "pct"])

    if exclude_terms:
        cols = [
            c
            for c in cols
            if all(term.lower() not in c.lower() for term in exclude_terms)
        ]

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
        label = c.split(" - ", 1)[-1]
        label = label.split("::")[-1]
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


def find_first_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Find the first column whose name contains any of the candidate substrings.
    Case-insensitive; returns None if nothing matches.
    """
    for cand in candidates:
        cand_low = cand.lower()
        for col in df.columns:
            if cand_low in col.lower():
                return col
    return None


def create_section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def donut_chart(df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str, top_n: int | None = None):
    """Brand-styled donut chart (no value overlays, only tooltip)."""
    if df_pct.empty:
        st.info("No responses for this question in the current filter.")
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)

    if top_n is not None and len(data) > top_n:
        data = data.sort_values("Percent", ascending=False).head(top_n)

    chart = (
        alt.Chart(data)
        .mark_arc(innerRadius=70, stroke="#ffffff", strokeWidth=2)
        .encode(
            theta=alt.Theta("Percent:Q", stack=True),
            color=alt.Color(
                f"{cat_field}:N",
                scale=alt.Scale(range=PL_CATEGORY_RANGE),
                legend=alt.Legend(title=None),
            ),
            tooltip=[f"{cat_field}:N", alt.Tooltip("Percent:Q", format=".1f")],
        )
        .properties(width=380, height=380, title=title)
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(chart, use_container_width=True)


def bar_chart_from_pct(
    df_pct: pd.DataFrame,
    cat_field: str,
    pct_field: str,
    title: str,
    horizontal: bool = True,
    top_n: int | None = None,
    show_legend: bool = False,
):
    """
    Brand-styled bar chart with bold % labels.
    Only percentages (no counts).
    """
    if df_pct.empty:
        st.info("No responses for this question in the current filter.")
        return

    data = df_pct.copy().rename(columns={pct_field: "Percent"})
    data[cat_field] = data[cat_field].astype(str)

    data = data.sort_values("Percent", ascending=False)
    if top_n is not None and len(data) > top_n:
        data = data.head(top_n)

    max_percent = data["Percent"].max()
    domain_max = 100 if max_percent <= 100 else None

    color_encoding = alt.Color(
        f"{cat_field}:N",
        scale=alt.Scale(range=PL_CATEGORY_RANGE),
        legend=alt.Legend(title=None) if not show_legend else alt.Legend(title=None),
    )

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
                axis=alt.Axis(labelLimit=0, labelOverlap=False, labelFontSize=11),
            ),
            color=color_encoding,
            tooltip=[
                f"{cat_field}:N",
                alt.Tooltip("Percent:Q", format=".1f", title="Percentage"),
            ],
        )

        bars = base.mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        labels = (
            base.mark_text(
                align="left",
                baseline="middle",
                dx=4,
                fontWeight="bold",
                color="#111827",
            )
            .encode(text=alt.Text("Percent:Q", format=".1f"))
        )

        chart = (
            (bars + labels)
            .properties(
                height=max(260, 30 * len(data)),
                title=title,
            )
            .configure_axisY(labelPadding=8)
        )
    else:
        base = alt.Chart(data).encode(
            x=alt.X(
                f"{cat_field}:N",
                sort="-y",
                title=None,
                axis=alt.Axis(labelLimit=0, labelOverlap=False, labelAngle=0),
            ),
            y=alt.Y(
                "Percent:Q",
                title="Share of respondents (%)",
                axis=alt.Axis(format=".0f", grid=True, gridColor="#f1f5f9"),
                scale=alt.Scale(domain=[0, domain_max] if domain_max else None),
            ),
            color=color_encoding,
            tooltip=[
                f"{cat_field}:N",
                alt.Tooltip("Percent:Q", format=".1f", title="Percentage"),
            ],
        )

        bars = base.mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        labels = (
            base.mark_text(
                align="center",
                baseline="bottom",
                dy=-6,
                fontWeight="bold",
                color="#111827",
            )
            .encode(text=alt.Text("Percent:Q", format=".1f"))
        )

        chart = (bars + labels).properties(height=360, title=title)

    st.altair_chart(chart, use_container_width=True)


def win_rate_distribution_pct(df: pd.DataFrame, col: str, title: str):
    """Win-rate / retention style distribution using 0–25 / 26–50 / 51–75 / 76–100 bins."""
    series = pd.to_numeric(df[col], errors="coerce").dropna()
    if series.empty:
        st.info("No responses for this question in the current filter.")
        return

    bins = [0, 26, 51, 76, 101]
    labels = ["0–25%", "26–50%", "51–75%", "76–100%"]
    binned = pd.cut(series, bins=bins, labels=labels, include_lowest=True, right=False)
    pct_df = value_counts_pct(binned)
    pct_df = pct_df.rename(columns={"category": "Range", "pct": "pct"})

    bar_chart_from_pct(
        pct_df,
        "Range",
        "pct",
        title,
        horizontal=False,
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
    border_color = PL_COLORS["amaranth"] if accent else PL_COLORS["minsk"]
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
              color:#64748b; font-weight:700; margin-bottom:8px; position: relative;">
    {title}
  </div>
  <div style="font-size:2.2rem; font-weight:900; color:#020617; margin-bottom:4px; 
              line-height:1.1; position: relative;">
    {value}
  </div>
  {f'<div style="font-size:0.9rem; color:#64748b; position: relative;">{subtitle}</div>' if subtitle else ''}
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def compute_marketplace_listing(df: pd.DataFrame) -> pd.Series | None:
    """Derive boolean 'Listed in marketplace' from any marketplace columns."""
    market_cols = [c for c in df.columns if "marketplace" in c.lower()]
    if not market_cols:
        return None
    sub = df[market_cols]
    if sub.empty:
        return None
    listed = (sub == 1).any(axis=1)
    return listed


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
  <p style="margin-bottom:0.5rem;">
    <strong>Welcome to the State of Partnership Leaders 2025 dashboard.</strong> 
    In prior years, we have released a 40+ page document with all of the data but with the
    advancements in AI adoption, we are trying something new.
  </p>
  <p style="margin-bottom:0.5rem;">
    <strong>PartnerOps Agent</strong> – An AI agent trained on the SOPL dataset, designed to act as your
    Partner Operations collaborator as you review the data. You can ask it questions about the data or 
    about your own strategy; we do not collect any of your inputted data.
  </p>
  <p style="margin-bottom:0;">
    <strong>SOPL Data Dashboard</strong> – All of the data from the report is available in the interactive 
    dashboard below. Use the filters on the left to customize the data to your interests and the
    <em>Performance</em>, <em>Strategic Direction</em>, and <em>Partner Impact</em> related tabs to navigate
    the main themes.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    # ---- Assistant (Pickaxe) ----
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

    # Column we already know exactly from the sheet
    COL_REGION = "Please select the region where your company is headquartered."
    COL_INDUSTRY = "What industry sector does your company operate in?"
    COL_REVENUE = "What is your company’s estimated annual revenue?"
    COL_EMPLOYEES = "What is your company’s total number of employees?"
    COL_DEAL_SIZE = "How does your average deal size involving partners compare to direct or non-partner deals?"
    COL_CAC = "How does your customer acquisition cost (CAC) from partners compared to direct sales and marketing?"
    COL_SALES_CYCLE = "How does your partner-led sales cycle compare to your direct sales cycle?"
    COL_WIN_RATE = "What’s your win rate for deals where partners are involved?"

    # Columns we will infer via substring search
    col_primary_goal = find_first_column(
        df,
        ["main goal for partnerships in the next 12 months"],
    )
    col_exec_expect = find_first_column(
        df,
        ["best describes your executive team", "executive team’s expectations of partnerships"],
    )
    col_expected_partner_rev = find_first_column(
        df,
        ["percentage of your company’s revenue is expected to come from partnerships", "expected to come from partnerships"],
    )
    col_retention = find_first_column(
        df,
        ["retention rate for partner-referred customers"],
    )
    col_biggest_challenge = find_first_column(
        df,
        ["biggest challenge in scaling your partner program"],
    )
    col_miss_goals = find_first_column(
        df,
        ["most likely reason your Partnerships team could miss its goals in the next 12 months"],
    )
    col_team_size = find_first_column(
        df,
        ["How many people are on your Partnerships team"],
    )
    col_budget = find_first_column(
        df,
        ["size of your Partnerships team’s annual budget", "annual budget (including headcount)"],
    )
    col_tech_use = find_first_column(
        df,
        ["use any technology or automation tools to manage your partner ecosystem"],
    )
    col_ai_use = find_first_column(
        df,
        ["currently using AI in your partner organization"],
    )

    # Normalized region (for filters & some charts)
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
            "Less than $50M",  # in case this wording is used
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

    # ---- About this dashboard (kept, per Tai) ----
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
  <p style="margin-top:0.4rem;">
  Use the filters on the left (Region, Annual revenue band, Total employees) to narrow the view;
  the KPIs and charts on all tabs update automatically to reflect the current selection. All
  values shown here are percentages based only on respondents who answered each question.
  </p>
</div>
""",
        unsafe_allow_html=True,
    )

    # ---- Tabs ----
    (
        tab_firm,
        tab_perf,
        tab_strat,
        tab_portfolio,
        tab_challenges,
        tab_team,
        tab_tech,
        tab_market,
        tab_additional,
    ) = st.tabs(
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
    # FIRMOGRAPHICS TAB
    # ======================================================
    with tab_firm:
        create_section_header("Executive snapshot")

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
                large_emp_pct = (large_count / len(emp_series)) * 100.0 if len(
                    emp_series
                ) > 0 else None

        # Median win rate
        median_win_rate = None
        if COL_WIN_RATE in flt.columns:
            wr = pd.to_numeric(flt[COL_WIN_RATE], errors="coerce").dropna()
            if not wr.empty:
                median_win_rate = float(wr.median())

        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            kpi_card(
                "Top industry by respondents",
                top_industry_name or "—",
                subtitle=(f"Share of respondents: {top_industry_pct:.1f}%"
                          if top_industry_pct is not None
                          else None),
                accent=True,
            )
        with col2:
            kpi_card(
                "Top HQ region",
                top_region_name or "—",
                subtitle=(f"Share of respondents: {top_region_pct:.1f}%"
                          if top_region_pct is not None
                          else None),
            )
        with col3:
            kpi_card(
                "Larger companies (≈500+ employees)",
                kpi_value_str(large_emp_pct),
                subtitle="Based on 501–5,000 and 5,000+ employee bins.",
            )
        with col4:
            kpi_card(
                "Median partner-involved win rate",
                f"{median_win_rate:.1f}%" if median_win_rate is not None else "—",
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Firmographic distributions
        create_section_header("Company profile (percentage breakdown)")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if "RegionStd" in flt.columns:
                region_pct = value_counts_pct(flt["RegionStd"])
                donut_chart(region_pct, "category", "pct", "HQ region (share of respondents)")
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_INDUSTRY in flt.columns:
                ind_pct = value_counts_pct(flt[COL_INDUSTRY])
                bar_chart_from_pct(
                    ind_pct,
                    "category",
                    "pct",
                    "Industry sector (share of respondents)",
                    horizontal=True,
                    top_n=8,
                )
            st.markdown("</div>", unsafe_allow_html=True)

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
                donut_chart(
                    emp_pct,
                    "category",
                    "pct",
                    "Company size (employees)",
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with c4:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_REVENUE in flt.columns:
                rev_pct = value_counts_pct(flt[COL_REVENUE])
                order = [
                    "Less than $50 million",
                    "$50M – $250M",
                    "$250M – $1B",
                    "$1B – $10B",
                    "More than $10B",
                    "Less than $50M",
                ]
                rev_pct["category"] = pd.Categorical(
                    rev_pct["category"], categories=order, ordered=True
                )
                rev_pct = rev_pct.sort_values("category")
                donut_chart(
                    rev_pct,
                    "category",
                    "pct",
                    "Annual revenue band (share of respondents)",
                )
            st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # PERFORMANCE TAB
    # ======================================================
    with tab_perf:
        create_section_header("Partner performance metrics")

        p1, p2 = st.columns(2)
        with p1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_DEAL_SIZE in flt.columns:
                ds_pct = value_counts_pct(flt[COL_DEAL_SIZE])
                bar_chart_from_pct(
                    ds_pct,
                    "category",
                    "pct",
                    "Average deal size: partner vs direct",
                    horizontal=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with p2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_CAC in flt.columns:
                cac_pct = value_counts_pct(flt[COL_CAC])
                bar_chart_from_pct(
                    cac_pct,
                    "category",
                    "pct",
                    "Partner-sourced CAC vs direct",
                    horizontal=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        create_section_header("Sales cycle and win rate")

        p3, p4 = st.columns(2)
        with p3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_SALES_CYCLE in flt.columns:
                sc_pct = value_counts_pct(flt[COL_SALES_CYCLE])
                bar_chart_from_pct(
                    sc_pct,
                    "category",
                    "pct",
                    "Partner-led sales cycle vs direct",
                    horizontal=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with p4:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if COL_WIN_RATE in flt.columns:
                win_rate_distribution_pct(flt, COL_WIN_RATE, "Win rate on partner-involved deals")
            st.markdown("</div>", unsafe_allow_html=True)

        create_section_header("Customer outcomes")

        c5, c6 = st.columns(2)
        with c5:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_retention:
                win_rate_distribution_pct(
                    flt, col_retention, "Retention rate for partner-referred customers"
                )
            else:
                st.info("Retention-rate question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        with c6:
            # Placeholder for any future performance metric; keep structure symmetrical.
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_expected_partner_rev:
                win_rate_distribution_pct(
                    flt,
                    col_expected_partner_rev,
                    "Expected revenue share from partnerships (next 12 months)",
                )
            else:
                st.info("Expected partner-revenue percentage question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # STRATEGIC DIRECTION TAB
    # ======================================================
    with tab_strat:
        create_section_header("Strategic goals for partnerships")

        s1, s2 = st.columns(2)
        with s1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_primary_goal:
                goal_pct = value_counts_pct(flt[col_primary_goal])
                bar_chart_from_pct(
                    goal_pct,
                    "category",
                    "pct",
                    "Main goal for partnerships (next 12 months)",
                    horizontal=True,
                    top_n=5,
                )
            else:
                st.info("Primary-goal question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        with s2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_exec_expect:
                exec_pct = value_counts_pct(flt[col_exec_expect])
                bar_chart_from_pct(
                    exec_pct,
                    "category",
                    "pct",
                    "Executive expectations of partnerships",
                    horizontal=True,
                )
            else:
                st.info("Executive-expectations question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        create_section_header("Risk of missing goals")

        s3, s4 = st.columns(2)
        with s3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_biggest_challenge:
                challenge_pct = value_counts_pct(flt[col_biggest_challenge])
                bar_chart_from_pct(
                    challenge_pct,
                    "category",
                    "pct",
                    "Biggest challenge in scaling the partner program",
                    horizontal=True,
                    top_n=7,
                )
            else:
                st.info("Scaling-challenge question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        with s4:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_miss_goals:
                miss_pct = value_counts_pct(flt[col_miss_goals])
                bar_chart_from_pct(
                    miss_pct,
                    "category",
                    "pct",
                    "Most likely reason partnership goals may be missed",
                    horizontal=True,
                    top_n=7,
                )
            else:
                st.info("Question on reasons goals may be missed not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # PARTNERSHIP PORTFOLIO TAB
    # ======================================================
    with tab_portfolio:
        create_section_header("Partnership types and impact")

        # Multi-select: Partnership types
        types_substr = "Which of the following Partnership types does your company have?"
        types_pct = multi_select_pct(flt, contains_substring=types_substr)
        p1, p2 = st.columns(2)

        with p1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if not types_pct.empty:
                bar_chart_from_pct(
                    types_pct,
                    "option",
                    "pct",
                    "Partnership types in place today",
                    horizontal=True,
                )
            else:
                st.info("No partnership-type multi-select columns detected for the current dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        with p2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            col_most_impact = find_first_column(
                flt, ["Which of the partnership types you selected above has the most impact"]
            )
            if col_most_impact:
                impact_pct = value_counts_pct(flt[col_most_impact])
                donut_chart(
                    impact_pct,
                    "category",
                    "pct",
                    "Most impactful partnership type",
                )
            else:
                st.info("Most-impactful partnership type question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        create_section_header("Partner influence measurement")

        influence_substr = (
            "Besides Sourced Revenue, how else does your company measure partner influence impact?"
        )
        infl_pct = multi_select_pct(flt, contains_substring=influence_substr)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        if not infl_pct.empty:
            bar_chart_from_pct(
                infl_pct,
                "option",
                "pct",
                "Partner influence measurement methods",
                horizontal=True,
            )
        else:
            st.info(
                "No influence-impact multi-select columns detected for the current dataset."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # CHALLENGES & RISKS TAB
    # ======================================================
    with tab_challenges:
        create_section_header("Scaling challenges and risk factors")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_biggest_challenge:
                challenge_pct = value_counts_pct(flt[col_biggest_challenge])
                bar_chart_from_pct(
                    challenge_pct,
                    "category",
                    "pct",
                    "Biggest challenge in scaling the partner program",
                    horizontal=True,
                    top_n=8,
                )
            else:
                st.info("Scaling-challenge question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_miss_goals:
                miss_pct = value_counts_pct(flt[col_miss_goals])
                bar_chart_from_pct(
                    miss_pct,
                    "category",
                    "pct",
                    "Most likely reasons partnership goals may be missed",
                    horizontal=True,
                    top_n=8,
                )
            else:
                st.info("Question on reasons goals may be missed not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # TEAM & INVESTMENT TAB
    # ======================================================
    with tab_team:
        create_section_header("Team structure and budget")

        t1, t2 = st.columns(2)
        with t1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_team_size:
                team_pct = value_counts_pct(flt[col_team_size])
                bar_chart_from_pct(
                    team_pct,
                    "category",
                    "pct",
                    "Partnerships team size",
                    horizontal=True,
                )
            else:
                st.info("Team-size question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        with t2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_budget:
                budget_pct = value_counts_pct(flt[col_budget])
                bar_chart_from_pct(
                    budget_pct,
                    "category",
                    "pct",
                    "Annual partnerships budget (including headcount)",
                    horizontal=True,
                )
            else:
                st.info("Budget-size question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        # Simple derived split: small vs larger teams (if team-size question is ordinal)
        create_section_header("Team scale snapshot")

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        if col_team_size:
            s = flt[col_team_size].dropna().astype(str)
            if not s.empty:
                mask_small = s.str.contains("Less than 10", case=False) | s.str.contains(
                    "Less than 10 people", case=False
                ) | s.str.contains("Less than 10", case=False)
                small = mask_small.sum()
                large = len(s) - small
                split_df = pd.DataFrame(
                    {
                        "category": ["Small team (<10)", "Larger team (10+)"],
                        "pct": [
                            small / len(s) * 100.0 if len(s) > 0 else 0,
                            large / len(s) * 100.0 if len(s) > 0 else 0,
                        ],
                    }
                )
                donut_chart(split_df, "category", "pct", "Partnerships team scale overview")
            else:
                st.info("No responses available for team size.")
        else:
            st.info("Team-size question not found in the dataset.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # TECHNOLOGY & AI TAB
    # ======================================================
    with tab_tech:
        create_section_header("Technology and AI adoption")

        tech1, tech2 = st.columns(2)
        with tech1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_tech_use:
                tech_pct = value_counts_pct(flt[col_tech_use])
                donut_chart(
                    tech_pct,
                    "category",
                    "pct",
                    "Use of technology / automation for partnerships",
                )
            else:
                st.info("Technology-usage question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        with tech2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if col_ai_use:
                ai_pct = value_counts_pct(flt[col_ai_use])
                donut_chart(
                    ai_pct,
                    "category",
                    "pct",
                    "Use of AI in the partner organization",
                )
            else:
                st.info("AI-usage question not found in the dataset.")
            st.markdown("</div>", unsafe_allow_html=True)

        create_section_header("Common tools used to manage partnerships")

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        tools_pct = multi_select_pct(
            flt,
            contains_substring="What tools do you currently use to manage your partnerships?",
            exclude_terms=BANNED_VENDOR_TERMS,
        )
        if not tools_pct.empty:
            bar_chart_from_pct(
                tools_pct,
                "option",
                "pct",
                "Tools currently used to manage partnerships (categories)",
                horizontal=True,
                top_n=8,
            )
        else:
            st.info(
                "No generic tool-category multi-select columns detected (or all contained vendor names)."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # MARKETPLACES TAB
    # ======================================================
    with tab_market:
        create_section_header("Marketplace partnerships")

        m1, m2 = st.columns(2)
        with m1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            listed_series = compute_marketplace_listing(flt)
            if listed_series is not None:
                map_df = value_counts_pct(
                    listed_series.map(
                        lambda x: "Listed in at least one marketplace" if x else "Not listed in marketplaces"
                    )
                )
                donut_chart(
                    map_df,
                    "category",
                    "pct",
                    "Company listed in third-party marketplaces",
                )
            else:
                st.info(
                    "No marketplace checkbox columns detected to derive listing status."
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with m2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            col_market_rev = find_first_column(
                flt,
                ["percentage of your total revenue comes through cloud marketplaces"],
            )
            if col_market_rev:
                win_rate_distribution_pct(
                    flt,
                    col_market_rev,
                    "Revenue share coming through cloud marketplaces",
                )
            else:
                st.info(
                    "Marketplace-revenue percentage question not found in the dataset."
                )
            st.markdown("</div>", unsafe_allow_html=True)

    # ======================================================
    # ADDITIONAL INSIGHTS TAB
    # ======================================================
    with tab_additional:
        create_section_header("Technology & AI by revenue band")

        # Example cross-cut: share using AI by revenue band (all percentages, no counts)
        col_ai_band = col_ai_use
        if col_ai_band and COL_REVENUE in flt.columns:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            sub = flt[[COL_REVENUE, col_ai_band]].dropna()
            if not sub.empty:
                # Compute % of "Yes" within each revenue band
                band_yes = (
                    sub.assign(
                        is_yes=sub[col_ai_band].astype(str).str.contains("Yes", case=False)
                    )
                    .groupby(COL_REVENUE)["is_yes"]
                    .mean()
                    * 100.0
                )
                ai_rev_df = (
                    band_yes.reset_index()
                    .rename(columns={COL_REVENUE: "Revenue band", "is_yes": "pct"})
                )
                bar_chart_from_pct(
                    ai_rev_df,
                    "Revenue band",
                    "pct",
                    "Share using AI in partner organization by revenue band",
                    horizontal=False,
                )
            else:
                st.info("No overlapping responses for revenue band and AI usage.")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info(
                "AI-usage and revenue-band questions were not both found; cross-cut not available."
            )

        create_section_header("Region-level technology adoption")

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        if col_tech_use and "RegionStd" in flt.columns:
            sub = flt[["RegionStd", col_tech_use]].dropna()
            if not sub.empty:
                tech_by_region = (
                    sub.assign(
                        is_yes=sub[col_tech_use]
                        .astype(str)
                        .str.contains("Yes", case=False)
                    )
                    .groupby("RegionStd")["is_yes"]
                    .mean()
                    * 100.0
                )
                tech_region_df = (
                    tech_by_region.reset_index()
                    .rename(columns={"RegionStd": "Region", "is_yes": "pct"})
                )
                bar_chart_from_pct(
                    tech_region_df,
                    "Region",
                    "pct",
                    "Share using technology / automation by HQ region",
                    horizontal=False,
                )
            else:
                st.info("No overlapping responses for region and technology usage.")
        else:
            st.info(
                "Region and technology-usage questions were not both found; cross-cut not available."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ---- Footer ----
    st.markdown(
        """
        <div class="footer">
            <strong>SOPL 2025 Insights Platform</strong> • Partnership analytics and strategic insights<br>
            <span style="color: #94a3b8; font-size: 0.8rem;">
                Data sourced from State of Partnership Leaders Survey. All figures shown are percentages only.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
