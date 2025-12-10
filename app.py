import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import re
import base64
from pathlib import Path

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SOPL 2025 - Partnership Analytics",
    page_icon="PL_transparent_1080.ico",
    layout="wide",
)

# ==================== BRAND COLORS ====================
PL_CORE = {
    "amaranth": "#EC3D72",
    "casablanca": "#F9A644",
    "minsk": "#3B308F",
}
PL_TINTS = {
    "amaranth_light": "#F25A8A",
    "casablanca_light": "#FBB85F",
    "minsk_light": "#5146A1",
}

PL_COLORS = [
    PL_CORE["minsk"],
    PL_CORE["amaranth"],
    PL_CORE["casablanca"],
    PL_TINTS["minsk_light"],
    PL_TINTS["amaranth_light"],
    PL_TINTS["casablanca_light"],
]

TOP_N_DEFAULT = 4  # default max categories per chart


# ==================== CSS / THEME ====================
st.markdown(
    """
<style>
html, body, .stApp {
    background-color: #f8fafc !important;
    color: #020617;
}
[data-testid="stAppViewContainer"] {
    background-color: #f8fafc !important;
}
main.block-container {
    background-color: #f8fafc !important;
    padding-top: 1rem;
}

/* Design tokens */
:root {
    --bg: #f8fafc;
    --card-bg: #ffffff;
    --muted: #64748b;
    --text: #020617;
    --accent: #3b308f;
}

/* App wrapper */
.app-wrapper {
    background: var(--bg);
    padding: 18px 24px 40px 24px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    max-width: 1400px;
    margin: 0 auto;
}

/* Header */
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

/* Shared card style – used by welcome, about, filters, ALL charts */
.card {
    background: var(--card-bg);
    border-radius: 24px;
    padding: 1.75rem 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 30px rgba(15,23,42,0.06);
    margin-bottom: 1.5rem;
}

/* Charts: SAME card, plus hover + subtle entrance */
.chart-card {
    background: var(--card-bg);
    border-radius: 24px;
    padding: 1.75rem 1.5rem 1.5rem 1.5rem;
    border: 1px solid #e2e8f0;
    box-shadow: 0 10px 30px rgba(15,23,42,0.06);
    margin-bottom: 1.5rem;
    opacity: 0;
    animation: fadeInUp 0.30s ease-out forwards;
    transition: box-shadow 0.18s ease, transform 0.18s ease, border-color 0.18s ease, background-color 0.18s ease;
}
.chart-card:hover {
    box-shadow: 0 20px 45px rgba(15,23,42,0.16);
    transform: translateY(-2px);
    border-color: #cbd5f5;
    background-color: #ffffff;
}

/* Filter card heading */
.filter-title-row {
    display:flex;
    align-items:center;
    gap:8px;
    margin-bottom:0.75rem;
}
.filter-title-row span {
    font-weight:800;
    font-size:1.05rem;
}
.filter-title-icon {
    width:20px;
    height:20px;
    border-radius:999px;
    border:2px solid #EC3D72;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:0.8rem;
    color:#EC3D72;
}

/* Section headers */
.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
    color: #1e293b !important;
}

/* Filter widgets in main page */
.stMultiSelect > div > div,
.stSelectbox > div > div {
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    background-color: #ffffff;
    color: #020617 !important;
    transition: all 0.18s ease;
}
.stMultiSelect > div > div:hover,
.stSelectbox > div > div:hover {
    border-color: #3b308f;
    box-shadow: 0 0 0 2px rgba(59,48,143,0.18);
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
    transition: all 0.18s ease;
    border: none;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background-color: #3b308f;
    color: #ffffff !important;
    box-shadow: 0 0 0 1px #3b308f, 0 10px 18px rgba(0,0,0,0.35);
}
.stTabs [data-baseweb="tab"][aria-selected="false"] {
    background-color: transparent;
    color: #e5e7eb !important;
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

/* Altair / Vega */
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
.vega-embed text {
    font-size: 11px;
}

/* Filter pills */
.filter-pill-row {
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin-top:0.25rem;
    margin-bottom:1.5rem;
}
.filter-pill {
    padding:4px 10px;
    border-radius:999px;
    background: #e2e8f0;
    color:#0f172a;
    font-size:0.8rem;
    font-weight:600;
}
.filter-pill span {
    font-weight:400;
    opacity:0.8;
}

/* Assistant header */
.assistant-header {
    border-radius: 24px;
    padding: 1.25rem 1.5rem;
    margin: 1.5rem 0 1rem 0;
    border: 1px solid #e2e8f0;
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
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

/* Small screens */
@media (max-width: 768px) {
    .main-header {
        font-size: 2.2rem;
    }
}

/* Fade-in animation for charts */
@keyframes fadeInUp {
    from { opacity:0; transform: translateY(4px); }
    to   { opacity:1; transform: translateY(0); }
}

/* Remove any truly empty chart wrappers */
.chart-card:empty {
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
            "range": {"category": PL_COLORS},
            "axis": {
                "labelColor": "#475569",
                "titleColor": "#020617",
                "titleFontWeight": 600,
                "labelFontWeight": 600,
                "gridColor": "#f1f5f9",
                "domainColor": "#d4d4d8",
                "labelLimit": 0,
                "labelFontSize": 11,
                "titleFontSize": 12,
            },
            "legend": {
                "labelColor": "#475569",
                "titleColor": "#020617",
                "titleFontWeight": 700,
                "labelFontWeight": 600,
                "labelFontSize": 14,
                "titleFontSize": 14,
                "symbolSize": 200,
                "symbolType": "circle",
            },
            "title": {
                "color": "#020617",
                "fontSize": 16,
                "fontWeight": 700,
                "anchor": "start",
                "offset": 12,
            },
        }
    }

alt.themes.register("atlas_light", atlas_light_theme)
alt.themes.enable("atlas_light")

alt.data_transformers.disable_max_rows()
alt.renderers.set_embed_options(
    actions={"export": True, "source": False, "compiled": False, "editor": False}
)

# ==================== DATA / UTILS ====================
@st.cache_data(show_spinner=True)
def load_data() -> pd.DataFrame:
    url = st.secrets.get("gsheet_url", None)
    if not url:
        st.error(
            "❌ Missing gsheet_url in Streamlit secrets. Add it in your app settings as `gsheet_url = \"...\"`."
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


def img_to_base64(path: str) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        data = p.read_bytes()
        return base64.b64encode(data).decode("utf-8")
    except Exception:
        return None


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


def binned_pct_custom(series: pd.Series, edges: list[float], labels: list[str]) -> pd.DataFrame:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return pd.DataFrame(columns=["bin", "pct"])
    binned = pd.cut(s, bins=edges, labels=labels, include_lowest=True, right=False)
    pct_df = value_counts_pct(binned).rename(columns={"category": "bin"})
    return pct_df


def _default_label_from_col(col_name: str) -> str:
    if '"' in col_name:
        parts = col_name.split('"')
        if len(parts) >= 3:
            return parts[1].strip()
    if " – " in col_name:
        return col_name.split(" – ", 1)[0].split("?")[-1].strip()
    if "? " in col_name:
        return col_name.split("? ", 1)[1].strip()
    return col_name.strip()


def multi_select_to_pct(
    df: pd.DataFrame, cols: list[str], label_parser=_default_label_from_col
) -> pd.DataFrame:
    if not cols:
        return pd.DataFrame(columns=["category", "pct"])
    sub = df[cols].apply(pd.to_numeric, errors="coerce")
    n_resp = sub.notna().any(axis=1).sum()
    if n_resp == 0:
        return pd.DataFrame(columns=["category", "pct"])
    counts = sub.sum(skipna=True)
    out = counts.reset_index()
    out.columns = ["col", "count"]
    out["category"] = out["col"].apply(label_parser)
    out["pct"] = (out["count"] / n_resp) * 100.0
    return out[["category", "pct"]].sort_values("pct", ascending=False)


def create_section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def donut_chart_clean(df_pct: pd.DataFrame, cat_field: str, pct_field: str, title: str):
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
        height=320,
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

    if horizontal:
        base = alt.Chart(data).encode(
            x=alt.X(
                "Percent:Q",
                title="Share of respondents (%)",
                axis=alt.Axis(format=".0f", grid=True, gridColor="#f1f5f9"),
            ),
            y=alt.Y(
                f"{cat_field}:N",
                sort="-x",
                title=None,
                axis=alt.Axis(labelOverlap=False),
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
                axis=alt.Axis(labelOverlap=False, labelAngle=0),
            ),
            y=alt.Y(
                "Percent:Q",
                title="Share of respondents (%)",
                axis=alt.Axis(format=".0f", grid=True, gridColor="#f1f5f9"),
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
            height=320,
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


def render_chart_card(chart_fn):
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    chart_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def two_up_grid(left_has: bool, left_fn, right_has: bool, right_fn):
    if not left_has and not right_has:
        return
    col1, col2 = st.columns(2)
    with col1:
        if left_has:
            render_chart_card(left_fn)
    with col2:
        if right_has:
            render_chart_card(right_fn)


def clean_question_title(col_name: str) -> str:
    title = re.sub(r"_Column\d+", "", col_name)
    title = title.replace("_", " ")
    title = re.sub(r"\s+", " ", title).strip()
    return title


def extract_platform_tool(col_name: str) -> str | None:
    if "Which platforms do you plan to use more, less, or steady?" not in col_name:
        return None
    parts = col_name.split("?", 1)
    if len(parts) != 2:
        return None
    tail = parts[1]
    tail = re.sub(r"_Column\d+", "", tail)
    tail = tail.strip(" _-")
    if not tail:
        return None
    tail = tail.replace("_", " ")
    tail = re.sub(r"\s+", " ", tail)
    return tail.strip()


def render_filter_pills(selected_regions, selected_revenue, selected_employees):
    pills = []
    if selected_regions is None:
        pills.append("Region: <span>All</span>")
    else:
        pills.append(f"Region: <span>{', '.join(selected_regions)}</span>")

    if selected_revenue is None:
        pills.append("Revenue: <span>All bands</span>")
    else:
        pills.append(f"Revenue: <span>{', '.join(selected_revenue)}</span>")

    if selected_employees is None:
        pills.append("Employees: <span>All sizes</span>")
    else:
        pills.append(f"Employees: <span>{', '.join(selected_employees)}</span>")

    html = "<div class='filter-pill-row'>" + "".join(
        f"<div class='filter-pill'>{p}</div>" for p in pills
    ) + "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ==================== MAIN APP ====================
def main():
    st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)

    # ----- Header with logos -----
    col_head_left, col_head_right = st.columns([4, 1.5])

    with col_head_left:
        st.markdown(
            """
            <div>
              <div class="main-header">STATE OF PARTNERSHIP LEADERS 2025</div>
              <div class="sub-header">Strategic Insights Dashboard • Partnership Performance Analytics</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_head_right:
        pl_b64 = img_to_base64("PL Logo.png")
        eu_b64 = img_to_base64("Euler logo.png")

        html_parts = []
        html_parts.append(
            "<div style='text-align:right; font-size:0.85rem; color:#64748b; margin-bottom:0.35rem;'>Sponsored by</div>"
        )
        if eu_b64:
            html_parts.append(
                f"""
                <a href="https://eulerapp.com/" target="_blank" style="text-decoration:none;">
                    <img src="data:image/png;base64,{eu_b64}" alt="Euler" style="height:40px; border-radius:8px; border:1px solid #e2e8f0; padding:4px; background:#ffffff;" />
                </a>
                """
            )
        if pl_b64:
            html_parts.append(
                f"""
                <div style="margin-top:0.3rem;">
                    <img src="data:image/png;base64,{pl_b64}" alt="Partnership Leaders" style="height:32px;" />
                </div>
                """
            )
        st.markdown("".join(html_parts), unsafe_allow_html=True)

    # ----- Intro card -----
    st.markdown(
        """
        <div class="card">
          <p><strong>Welcome to the State of Partnership Leaders 2025 Dashboard.</strong></p>
          <p>
          In prior years, we have released a 40+ page document with all of the data but with the advancements in AI adoption,
          we are trying something new.
          </p>
          <p><strong>Below you will find:</strong></p>
          <ul>
            <li>
              <strong>PartnerOps Agent</strong> – An AI agent trained on the SOPL dataset – think of it as your Partner Operations collaborator as you review the data.
              You can ask it questions about the data or about your own strategy, we will not collect any of your inputed data.
            </li>
            <li>
              <strong>SOPL Data Dashboard</strong> – You will find all of the data from the report in an interactive dashboard below.
              Use the filters to customize the data to your interests and the Performance and Partner Impact related tabs to navigate the main themes.
            </li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ----- Assistant -----
    st.markdown(
        """
        <div class="assistant-header">
            <h2 style='color:#020617; margin:0;'>PartnerOps Agent (SOPL Q&amp;A)</h2>
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

    # ----- Data -----
    df = load_data()
    if df.empty:
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

    # ----- Column mappings -----
    COL_REGION = "Please select the region where your company is headquartered."
    COL_INDUSTRY = "What industry sector does your company operate in?"
    COL_REVENUE = find_col(
        df,
        exact="What is your companys estimated annual revenue?",
        substrings=[
            "company’s estimated annual revenue",
            "company's estimated annual revenue",
            "estimated annual revenue",
        ],
    )
    COL_EMPLOYEES = find_col(
        df,
        exact="What is your companys total number of employees?",
        substrings=[
            "total number of employees",
            "company’s total number of employees",
            "company's total number of employees",
        ],
    )
    COL_DEAL_SIZE = "How does your average deal size involving partners compare to direct or non-partner deals?"
    COL_CAC = "How does your customer acquisition cost (CAC) from partners compared to direct sales and marketing?"
    COL_SALES_CYCLE = "How does your partner-led sales cycle compare to your direct sales cycle?"
    COL_WIN_RATE = "What’s your win rate for deals where partners are involved?"

    COL_PRIMARY_GOAL = find_col(df, substrings=["main goal for partnerships in the next 12 months"])
    COL_EXEC_EXPECT = find_col(df, substrings=["executive teams expectations of partnerships", "executive team’s expectations of partnerships"])
    COL_EXPECTED_REV = find_col(df, substrings=["expected to come from partnerships in the next 12 months"])
    COL_RETENTION = find_col(df, substrings=["retention rate for partner-referred customers"])
    COL_MOST_IMPACTFUL_TYPE = find_col(df, substrings=["most impact", "most impactful type"])
    COL_BIGGEST_CHALLENGE = find_col(df, substrings=["biggest challenge in scaling your partner program"])
    COL_MISS_GOALS_REASON = find_col(df, substrings=["most likely reason your Partnerships team could miss its goals"])
    COL_TEAM_SIZE = find_col(df, substrings=["people are on your Partnerships team"])
    COL_BUDGET = find_col(df, substrings=["annual budget", "Partnerships teams annual budget"])
    COL_USE_TECH = find_col(df, substrings=["technology or automation tools to manage your partner ecosystem"])
    COL_USE_AI = find_col(df, substrings=["using AI in your partner organization"])
    COL_MARKETPLACE_LISTED = find_col(df, substrings=["company listed in", "listed in marketplaces"])
    COL_MARKETPLACE_REV = find_col(df, substrings=["total revenue comes through cloud marketplaces", "revenue comes through cloud marketplaces"])
    COL_PARTNER_FOCUS = find_col(df, substrings=["focus next 12 months"])
    COL_STRATEGIC_BET = find_col(df, substrings=["Strategic bet", "strategic bet next 12 months"])
    COL_FORECAST_PERF = find_col(df, substrings=["Forecasted performance", "forecasting your performance"])
    COL_REPORTING = find_col(df, substrings=["report to", "majority of your partner organization report"])
    COL_TRAINING = find_col(df, substrings=["level of training", "training or enablement"])

    COL_TOTAL_PARTNERS = "How many total partners do you have?"
    COL_ACTIVE_PARTNERS = "How many active partners generated revenue in the last 12 months?"

    INFLUENCE_PREFIX = "Besides Sourced Revenue, how else does your company measure"
    PARTNERSHIP_HAVE_PREFIX = "Which of the following Partnership types does your company have?"
    PARTNERSHIP_EXPAND_PREFIX = "Which partnership types are you planning to expand into"
    ROLES_PREFIX = "What roles exist on your Partner Team?"
    COL_TOP3_BUDGET_PREFIX = "What are the top 3 budget line items for your Partnerships organization, excluding headcount?"
    SAT_PREFIX = "How do you measure partner satisfaction?"

    # RegionStd column
    if COL_REGION in df.columns:
        df = df.copy()
        df["RegionStd"] = df[COL_REGION].map(normalize_region_label)
    else:
        df["RegionStd"] = None

    # ----- Filters card -----
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="filter-title-row">
          <div class="filter-title-icon">⧉</div>
          <span>Filters</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    f1, f2, f3 = st.columns(3)

    # Region
    with f1:
        if "RegionStd" in df.columns:
            region_options = sorted(df["RegionStd"].dropna().unique().tolist())
            sentinel_region = "All Regions"
            region_display_options = [sentinel_region] + region_options
            selected_regions_raw = st.multiselect(
                "Region",
                region_display_options,
                [sentinel_region],
            )
            if sentinel_region in selected_regions_raw or not selected_regions_raw:
                selected_regions = None
            else:
                selected_regions = selected_regions_raw
        else:
            selected_regions = None

    # Revenue
    with f2:
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
            sentinel_rev = "All Revenue Bands"
            revenue_display_options = [sentinel_rev] + ordered_revenue
            selected_revenue_raw = st.multiselect(
                "Annual Revenue",
                revenue_display_options,
                [sentinel_rev],
            )
            if sentinel_rev in selected_revenue_raw or not selected_revenue_raw:
                selected_revenue = None
            else:
                selected_revenue = selected_revenue_raw
        else:
            selected_revenue = None

    # Employees
    with f3:
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
            sentinel_emp = "All Sizes"
            emp_display_options = [sentinel_emp] + ordered_emp
            selected_employees_raw = st.multiselect(
                "Total Employees",
                emp_display_options,
                [sentinel_emp],
            )
            if sentinel_emp in selected_employees_raw or not selected_employees_raw:
                selected_employees = None
            else:
                selected_employees = selected_employees_raw
        else:
            selected_employees = None

    st.markdown("</div>", unsafe_allow_html=True)

    # Apply filters
    flt = df.copy()
    if selected_regions:
        flt = flt[flt["RegionStd"].isin(selected_regions)]
    if selected_revenue and COL_REVENUE in flt.columns:
        flt = flt[flt[COL_REVENUE].isin(selected_revenue)]
    if selected_employees and COL_EMPLOYEES in flt.columns:
        flt = flt[flt[COL_EMPLOYEES].isin(selected_employees)]

    render_filter_pills(selected_regions, selected_revenue, selected_employees)

    # ----- About this dataset -----
    create_section_header("About this dashboard and dataset")
    st.markdown(
        """
        <div class="card">
          <p>
          Respondents represent organizations from four key regions, namely North America (NA),
          Europe the Middle East and Africa (EMEA), Asia Pacific (APAC), and Latin America (LATAM),
          and include companies of varying sizes and revenue levels ranging from less than 50 million
          dollars to over 10 billion dollars in annual revenue. All survey waves ensure a minimum of
          100 qualified respondents each year to provide consistent and data-driven insights across regions
          and industries.
          </p>
          <p style="margin-top:0.5rem;">
          Use the filters above (Region, Annual Revenue, Total Employees) to narrow the view;
          the charts in every tab update automatically to reflect the current selection.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Track columns used to avoid duplicates in Additional Insights
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
            COL_REPORTING,
            COL_TRAINING,
            COL_TOTAL_PARTNERS,
            COL_ACTIVE_PARTNERS,
            "RegionStd",
        ]
        if c is not None
    }
    for col in df.columns:
        if (
            INFLUENCE_PREFIX in col
            or PARTNERSHIP_HAVE_PREFIX in col
            or PARTNERSHIP_EXPAND_PREFIX in col
            or ROLES_PREFIX in col
            or COL_TOP3_BUDGET_PREFIX in col
            or SAT_PREFIX in col
        ):
            used_cols.add(col)

    # ----- Tabs -----
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
    # Firmographics
    # ======================================================
    with tab_firmo:
        create_section_header("Company profile")

        # HQ region + revenue
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

        two_up_grid(reg_has, reg_chart, rev_has, rev_chart)

        # Employees + industry
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

        two_up_grid(emp_has, emp_chart, ind_has, ind_chart)

    # ======================================================
    # Performance
    # ======================================================
    with tab_perf:
        create_section_header("Partner impact & performance")

        ds_has = COL_DEAL_SIZE in flt.columns and not flt[COL_DEAL_SIZE].dropna().empty

        def ds_chart():
            ds_pct = value_counts_pct(flt[COL_DEAL_SIZE])
            donut_chart_clean(ds_pct, "category", "pct", "Deal size vs direct")

        cac_has = COL_CAC in flt.columns and not flt[COL_CAC].dropna().empty

        def cac_chart():
            cac_pct = value_counts_pct(flt[COL_CAC])
            donut_chart_clean(cac_pct, "category", "pct", "CAC vs direct")

        two_up_grid(ds_has, ds_chart, cac_has, cac_chart)

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
                "Win rate with partners",
                horizontal=False,
                max_categories=TOP_N_DEFAULT,
            )

        ret_has = COL_RETENTION and COL_RETENTION in flt.columns and not flt[COL_RETENTION].dropna().empty

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
                "Partner-referred customer retention",
                horizontal=False,
                max_categories=5,
            )

        two_up_grid(wr_has, wr_chart, ret_has, ret_chart)

        # Influence measures
        create_section_header("Measuring partner influence beyond sourced revenue")
        influence_cols = [c for c in flt.columns if INFLUENCE_PREFIX in c]
        inf_pct = multi_select_to_pct(flt, influence_cols) if influence_cols else pd.DataFrame()

        if not inf_pct.empty:
            render_chart_card(
                lambda: bar_chart_from_pct(
                    inf_pct,
                    "category",
                    "pct",
                    "Partner influence impact measures",
                    horizontal=True,
                    max_categories=None,
                )
            )

    # ======================================================
    # Strategic Direction
    # ======================================================
    with tab_strategy:
        create_section_header("Strategic direction")

        pg_has = COL_PRIMARY_GOAL and COL_PRIMARY_GOAL in flt.columns and not flt[COL_PRIMARY_GOAL].dropna().empty

        def pg_chart():
            pg_pct = value_counts_pct(flt[COL_PRIMARY_GOAL])
            bar_chart_from_pct(pg_pct, "category", "pct", "Primary goal for partnerships", horizontal=True)

        ex_has = COL_EXEC_EXPECT and COL_EXEC_EXPECT in flt.columns and not flt[COL_EXEC_EXPECT].dropna().empty

        def ex_chart():
            s = flt[COL_EXEC_EXPECT].dropna().astype(str)
            short = s.str.split(" - ", n=1).str[0]
            ex_pct = value_counts_pct(short)
            bar_chart_from_pct(ex_pct, "category", "pct", "Executive expectations", horizontal=True)

        two_up_grid(pg_has, pg_chart, ex_has, ex_chart)

        er_has = COL_EXPECTED_REV and COL_EXPECTED_REV in flt.columns and not flt[COL_EXPECTED_REV].dropna().empty

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

        pf_has = COL_PARTNER_FOCUS and COL_PARTNER_FOCUS in flt.columns and not flt[COL_PARTNER_FOCUS].dropna().empty

        def pf_chart():
            pf_pct = value_counts_pct(flt[COL_PARTNER_FOCUS])
            bar_chart_from_pct(
                pf_pct,
                "category",
                "pct",
                "Partnership focus in the next 12 months",
                horizontal=True,
            )

        two_up_grid(er_has, er_chart, pf_has, pf_chart)

        sb_has = COL_STRATEGIC_BET and COL_STRATEGIC_BET in flt.columns and not flt[COL_STRATEGIC_BET].dropna().empty

        def sb_chart():
            sb_pct = value_counts_pct(flt[COL_STRATEGIC_BET])
            bar_chart_from_pct(
                sb_pct,
                "category",
                "pct",
                "Strategic bet for the next 12 months",
                horizontal=True,
            )

        fp_has = COL_FORECAST_PERF and COL_FORECAST_PERF in flt.columns and not flt[COL_FORECAST_PERF].dropna().empty

        def fp_chart():
            fp_pct = value_counts_pct(flt[COL_FORECAST_PERF])
            bar_chart_from_pct(
                fp_pct,
                "category",
                "pct",
                "Forecasted performance vs goals",
                horizontal=True,
            )

        two_up_grid(sb_has, sb_chart, fp_has, fp_chart)

    # ======================================================
    # Partnership Portfolio
    # ======================================================
    with tab_portfolio:
        create_section_header("Partnership portfolio")

        mi_has = COL_MOST_IMPACTFUL_TYPE and COL_MOST_IMPACTFUL_TYPE in flt.columns and not flt[COL_MOST_IMPACTFUL_TYPE].dropna().empty

        def mi_chart():
            mi_pct = value_counts_pct(flt[COL_MOST_IMPACTFUL_TYPE])
            donut_chart_clean(mi_pct, "category", "pct", "Most impactful partnership type")

        part_cols = [c for c in flt.columns if PARTNERSHIP_HAVE_PREFIX in c]
        df_part = multi_select_to_pct(flt, part_cols) if part_cols else pd.DataFrame()

        def part_chart():
            bar_chart_from_pct(
                df_part,
                "category",
                "pct",
                "Current partnership types",
                horizontal=True,
                max_categories=None,
            )

        two_up_grid(mi_has, mi_chart, not df_part.empty, part_chart)

        expand_cols = [c for c in flt.columns if PARTNERSHIP_EXPAND_PREFIX in c]
        df_expand = multi_select_to_pct(flt, expand_cols) if expand_cols else pd.DataFrame()

        def expand_chart():
            bar_chart_from_pct(
                df_expand,
                "category",
                "pct",
                "Partnership types planned for expansion",
                horizontal=True,
                max_categories=None,
            )

        total_has = COL_TOTAL_PARTNERS and COL_TOTAL_PARTNERS in flt.columns and not flt[COL_TOTAL_PARTNERS].dropna().empty

        def total_chart():
            total_pct = value_counts_pct(flt[COL_TOTAL_PARTNERS])
            bar_chart_from_pct(
                total_pct,
                "category",
                "pct",
                "Number of total partners",
                horizontal=False,
                max_categories=TOP_N_DEFAULT,
            )

        two_up_grid(not df_expand.empty, expand_chart, total_has, total_chart)

        active_has = COL_ACTIVE_PARTNERS and COL_ACTIVE_PARTNERS in flt.columns and not flt[COL_ACTIVE_PARTNERS].dropna().empty

        def active_chart():
            active_pct = value_counts_pct(flt[COL_ACTIVE_PARTNERS])
            bar_chart_from_pct(
                active_pct,
                "category",
                "pct",
                "Active partners generating revenue (last 12 months)",
                horizontal=False,
                max_categories=TOP_N_DEFAULT,
            )

        two_up_grid(active_has, active_chart, False, lambda: None)

    # ======================================================
    # Challenges & Risks
    # ======================================================
    with tab_ops:
        create_section_header("Challenges & risks")

        bc_has = COL_BIGGEST_CHALLENGE and COL_BIGGEST_CHALLENGE in flt.columns and not flt[COL_BIGGEST_CHALLENGE].dropna().empty

        def bc_chart():
            bc_pct = value_counts_pct(flt[COL_BIGGEST_CHALLENGE])
            bar_chart_from_pct(
                bc_pct,
                "category",
                "pct",
                "Biggest challenge in scaling the program",
                horizontal=True,
            )

        mg_has = COL_MISS_GOALS_REASON and COL_MISS_GOALS_REASON in flt.columns and not flt[COL_MISS_GOALS_REASON].dropna().empty

        def mg_chart():
            mg_pct = value_counts_pct(flt[COL_MISS_GOALS_REASON])
            bar_chart_from_pct(
                mg_pct,
                "category",
                "pct",
                "Most likely reason goals may be missed",
                horizontal=True,
            )

        two_up_grid(bc_has, bc_chart, mg_has, mg_chart)

        sat_cols = [c for c in flt.columns if SAT_PREFIX in c]
        df_sat = multi_select_to_pct(flt, sat_cols) if sat_cols else pd.DataFrame()

        if not df_sat.empty:
            render_chart_card(
                lambda: bar_chart_from_pct(
                    df_sat,
                    "category",
                    "pct",
                    "How partner satisfaction is measured",
                    horizontal=True,
                    max_categories=None,
                )
            )

    # ======================================================
    # Team & Investment
    # ======================================================
    with tab_team:
        create_section_header("Team & investment")

        ts_has = COL_TEAM_SIZE and COL_TEAM_SIZE in flt.columns and not flt[COL_TEAM_SIZE].dropna().empty

        def ts_chart():
            ts_pct = value_counts_pct(flt[COL_TEAM_SIZE])
            donut_chart_clean(ts_pct, "category", "pct", "Partnerships team size")

        if COL_BUDGET and COL_BUDGET in flt.columns:
            bud_series = flt[COL_BUDGET].dropna().astype(str)
            bud_series = bud_series[
                ~bud_series.str.contains("I don’t have this data|I don't have this data", case=False, na=False)
            ]
            bud_pct = value_counts_pct(bud_series)
        else:
            bud_pct = pd.DataFrame()
        bud_has = not bud_pct.empty

        def bud_chart():
            bar_chart_from_pct(
                bud_pct,
                "category",
                "pct",
                "Annual partnerships budget",
                horizontal=True,
            )

        two_up_grid(ts_has, ts_chart, bud_has, bud_chart)

        rep_has = COL_REPORTING and COL_REPORTING in flt.columns and not flt[COL_REPORTING].dropna().empty

        def rep_chart():
            rep_series = flt[COL_REPORTING].dropna().astype(str)
            rep_pct = value_counts_pct(rep_series)
            bar_chart_from_pct(
                rep_pct,
                "category",
                "pct",
                "Where the Partnerships team reports",
                horizontal=True,
                max_categories=8,
            )

        budget_item_cols = [c for c in flt.columns if COL_TOP3_BUDGET_PREFIX in c]
        df_bud = multi_select_to_pct(flt, budget_item_cols) if budget_item_cols else pd.DataFrame()

        def budget_items_chart():
            bar_chart_from_pct(
                df_bud,
                "category",
                "pct",
                "Top 3 budget line items (excluding headcount)",
                horizontal=True,
                max_categories=None,
            )

        two_up_grid(rep_has, rep_chart, not df_bud.empty, budget_items_chart)

        tr_has = COL_TRAINING and COL_TRAINING in flt.columns and not flt[COL_TRAINING].dropna().empty

        def tr_chart():
            tr_series = flt[COL_TRAINING].dropna().astype(str)
            tr_pct = value_counts_pct(tr_series)
            bar_chart_from_pct(
                tr_pct,
                "category",
                "pct",
                "Partner training & enablement level",
                horizontal=True,
                max_categories=8,
            )

        roles_cols = [c for c in flt.columns if ROLES_PREFIX in c]
        df_roles = multi_select_to_pct(flt, roles_cols) if roles_cols else pd.DataFrame()

        def roles_chart():
            bar_chart_from_pct(
                df_roles,
                "category",
                "pct",
                "Roles that exist on the Partner Team",
                horizontal=True,
                max_categories=None,
            )

        two_up_grid(tr_has, tr_chart, not df_roles.empty, roles_chart)

    # ======================================================
    # Technology & AI
    # ======================================================
    with tab_tech:
        create_section_header("Technology & AI")

        ut_has = COL_USE_TECH and COL_USE_TECH in flt.columns

        def ut_chart():
            ut_pct = value_counts_pct(flt[COL_USE_TECH])
            donut_chart_clean(
                ut_pct,
                "category",
                "pct",
                "Currently using partner tech/automation",
            )

        ai_has = COL_USE_AI and COL_USE_AI in flt.columns

        def ai_chart():
            ai_pct = value_counts_pct(flt[COL_USE_AI])
            donut_chart_clean(
                ai_pct,
                "category",
                "pct",
                "Currently using AI in the partner organization",
            )

        two_up_grid(ut_has, ut_chart, ai_has, ai_chart)

    # ======================================================
    # Marketplaces
    # ======================================================
    with tab_market:
        create_section_header("Marketplaces")

        mpl_has = COL_MARKETPLACE_LISTED and COL_MARKETPLACE_LISTED in flt.columns

        def mpl_chart():
            mpl_series = normalize_yes_no(flt[COL_MARKETPLACE_LISTED])
            mpl_pct = value_counts_pct(mpl_series)
            donut_chart_clean(
                mpl_pct,
                "category",
                "pct",
                "Company listed in marketplaces",
            )

        mp_has_any = COL_MARKETPLACE_REV and COL_MARKETPLACE_REV in flt.columns and not flt[COL_MARKETPLACE_REV].dropna().empty

        def mp_chart():
            mp_rev = flt[COL_MARKETPLACE_REV].dropna()
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

        two_up_grid(mpl_has, mpl_chart, mp_has_any, mp_chart)

    # ======================================================
    # Additional Insights (2x2 grid)
    # ======================================================
    with tab_extra:
        create_section_header("Additional insights across remaining questions")

        st.markdown(
            """
            <div class="card">
              <p style="margin-bottom:0.5rem;">
                This section surfaces additional multiple-choice questions that are not already covered in the main tabs.
                Vendor-specific, numeric-only, and free-text style questions are excluded to keep the view focused on
                interpretable categorical insights.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

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
        vendor_pattern = re.compile("|".join(vendor_keywords), re.IGNORECASE)

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
            numeric_coerced = pd.to_numeric(s_nonnull, errors="coerce")
            if numeric_coerced.notna().mean() > 0.9:
                continue
            n_unique = s_nonnull.astype(str).nunique()
            if n_unique <= 1 or n_unique > 12:
                continue
            if s_nonnull.astype(str).str.contains(vendor_pattern, na=False).any():
                continue
            cat_pct = value_counts_pct(series)
            if cat_pct.empty:
                continue
            extra_questions.append({"col": col, "pct": cat_pct})

        extra_questions = extra_questions[:10]

        if extra_questions:
            # 2x2 (or 2xN) grid: each row has 2 cards
            for i in range(0, len(extra_questions), 2):
                row = extra_questions[i : i + 2]
                c1, c2 = st.columns(2)
                for item, col_streamlit in zip(row, [c1, c2]):
                    with col_streamlit:
                        col_name = item["col"]
                        pct_df = item["pct"]
                        n_cat = len(pct_df)
                        tool_name = extract_platform_tool(col_name)
                        if tool_name:
                            title = f"{tool_name} – Which platforms do you plan to use more, less, or steady?"
                        else:
                            title = clean_question_title(col_name)

                        def chart_fn(pct_df=pct_df, title=title, n_cat=n_cat):
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

                        render_chart_card(chart_fn)
        else:
            st.info(
                "No additional summarized categorical questions detected beyond the main dashboard sections."
            )

    # ----- Footer -----
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
