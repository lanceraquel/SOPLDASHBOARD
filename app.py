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
    --accent: #3b308f;
    --success: #16a34a;
    --warning: #f59e0b;
    --danger: #ef4444;
    --glass: rgba(15,23,42,0.04);
}

/* All text dark and visible */
html, body, .stApp, .stApp * {
    color: #020617 !important;
}

/* Layout + typography */
.app-wrapper {
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
    font-size: 3.5rem;               /* Bigger, executive look */
    font-weight: 900;
    margin: 0;
    color: #ec3d72 !important;       /* Amaranth */
    letter-spacing: -0.5px;
}

.sub-header {
    font-size: 1.15rem;              /* Slightly bigger & more premium */
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

/* Altair/ Vega menu (fullscreen, export) — light theme */
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
.vega-embed details[open] > summary {
    box-shadow:0 2px 6px rgba(15,23,42,0.2);
}
.vega-embed details > summary {
    background-color:#ffffff !important;
    border-radius:50% !important;
    border:1px solid #e2e8f0 !important;
}

/* Improve axis label visibility */
.vega-embed text {
    font-size: 11px;
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

alt.data_transformers.disable_max_rows()
alt.renderers.set_embed_options(actions={"export": True, "source": False})

# ==================== GOOGLE SHEETS LOADER ====================
@st.cache_data(show_spinner=True)
def load_data() -> pd.DataFrame:
    """
    Load SOPL data directly from Google Sheets using st.secrets["gsheet_url"].
    """
    url = st.secrets.get("gsheet_url", None)
    if not url:
        st.error("❌ Missing gsheet_url in Streamlit secrets.")
        return pd.DataFrame()

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]

    for enc in encodings:
        try:
            df = pd.read_csv(url, encoding=enc)
            return df
        except Exception:
            continue

    st.error("❌ Failed to read data from Google Sheets. Check CSV export link.")
    return pd.DataFrame()

# ==================== HELPERS ====================
def value_counts_pct(series: pd.Series) -> pd.DataFrame:
    """Return categories + % based on non-null responses."""
    s = series.dropna()
    if s.empty:
        return pd.DataFrame(columns=["category", "pct"])
    pct = (s.value_counts() / s.value_counts().sum()) * 100
    df = pct.reset_index()
    df.columns = ["category", "pct"]
    return df

def create_section_header(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def donut_chart_with_labels(df_pct, cat_field, pct_field, title):
    if df_pct.empty:
        st.info("No data to display.")
        return
    data = df_pct.copy()
    data[cat_field] = data[cat_field].astype(str)
    base = alt.Chart(data).encode(
        theta=alt.Theta(f"{pct_field}:Q", stack=True),
        color=alt.Color(f"{cat_field}:N", legend=alt.Legend(title=None)),
    )
    donut = base.mark_arc(innerRadius=70)
    text = base.mark_text(
        radius=110, size=13, color="#020617"
    ).encode(text=alt.Text(f"{pct_field}:Q", format=".1f"))

    chart = (donut + text).properties(
        width=380, height=380, title=title
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

def bar_chart_from_pct(df_pct, cat_field, pct_field, title, horizontal=True):
    if df_pct.empty:
        st.info("No data to display.")
        return

    df = df_pct.copy()
    df[cat_field] = df[cat_field].astype(str)

    if horizontal:
        base = alt.Chart(df).encode(
            x=alt.X(f"{pct_field}:Q", title="Percent (%)", axis=alt.Axis(format=".0f")),
            y=alt.Y(f"{cat_field}:N", sort="-x", title=None),
        )
        bars = base.mark_bar(color="#3b308f")
        labels = base.mark_text(
            align="left", baseline="middle", dx=4, color="#020617"
        ).encode(text=alt.Text(f"{pct_field}:Q", format=".1f"))
        chart = (bars + labels).properties(
            height=max(260, len(df) * 26),
            title=title
        ).interactive()
    else:
        base = alt.Chart(df).encode(
            x=alt.X(f"{cat_field}:N", sort="-y", title=None),
            y=alt.Y(f"{pct_field}:Q", title="Percent (%)", axis=alt.Axis(format=".0f"))
        )
        bars = base.mark_bar(color="#3b308f")
        labels = base.mark_text(
            align="center", baseline="bottom", dy=-4, color="#020617"
        ).encode(text=alt.Text(f"{pct_field}:Q", format=".1f"))
        chart = (bars + labels).properties(height=380, title=title).interactive()

    st.altair_chart(chart, use_container_width=True)

def win_rate_distribution_pct(df, col):
    series = df[col].dropna()
    if series.empty:
        st.info("No win-rate data.")
        return
    bins = list(range(0, 101, 10))
    labels = [f"{b}-{b+10}%" for b in bins[:-1]]
    binned = pd.cut(series, bins=bins, labels=labels, include_lowest=True, right=False)
    pct = value_counts_pct(binned)
    pct = pct.rename(columns={"category": "bin"})
    bar_chart_from_pct(
        pct, "bin", "pct", "Win rate distribution (10-pt bands)", horizontal=False
    )

def normalize_region_label(x):
    if pd.isna(x):
        return None
    s = str(x)
    if "North America" in s:
        return "North America"
    if "Latin America" in s:
        return "Latin America"
    if "Asia-Pacific" in s or "APAC" in s or "Asia Pacific" in s:
        return "Asia Pacific"
    if "Europe" in s or "EMEA" in s:
        return "Europe"
    return s

# ==================== MAIN APP ====================
def main():

    st.markdown('<div class="app-wrapper">', unsafe_allow_html=True)

    # Header
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

    # Column names
    COL_REGION = "Please select the region where your company is headquartered."
    COL_INDUSTRY = "What industry sector does your company operate in?"
    COL_REVENUE = "What is your company’s estimated annual revenue?"
    COL_EMPLOYEES = "What is your company’s total number of employees?"
    COL_DEAL = "How does your average deal size involving partners compare to direct or non-partner deals?"
    COL_CAC = "How does your customer acquisition cost (CAC) from partners compared to direct sales and marketing?"
    COL_SALES = "How does your partner-led sales cycle compare to your direct sales cycle?"
    COL_WIN = "What’s your win rate for deals where partners are involved?"

    # Region normalization
    df["RegionStd"] = df[COL_REGION].map(normalize_region_label)

    # Sidebar Filters
    st.sidebar.header("Filters")

    regions = sorted(df["RegionStd"].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

    revenue_opts = sorted(df[COL_REVENUE].dropna().unique().tolist())
    selected_revenue = st.sidebar.multiselect("Revenue", revenue_opts, default=revenue_opts)

    emp_opts = sorted(df[COL_EMPLOYEES].dropna().unique().tolist())
    selected_emp = st.sidebar.multiselect("Employees", emp_opts, default=emp_opts)

    # Apply filters
    flt = df.copy()
    flt = flt[flt["RegionStd"].isin(selected_regions)]
    flt = flt[flt[COL_REVENUE].isin(selected_revenue)]
    flt = flt[flt[COL_EMPLOYEES].isin(selected_emp)]

    st.caption(f"Responses in view: {len(flt)}")

    # Tabs
    tab_overview, tab_perf, tab_geo, tab_multi, tab_data = st.tabs(
        ["Overview", "Performance", "Geography", "Partner & Impact", "Data"]
    )

    # ---------------- TAB 1: OVERVIEW ----------------
    with tab_overview:
        create_section_header("Company profile")

        c1, c2 = st.columns(2)
        with c1:
            donut_chart_with_labels(
                value_counts_pct(flt["RegionStd"]),
                "category",
                "pct",
                "Region distribution (%)"
            )
        with c2:
            bar_chart_from_pct(
                value_counts_pct(flt[COL_REVENUE]),
                "category",
                "pct",
                "Revenue bands (%)"
            )

        c3, c4 = st.columns(2)
        with c3:
            bar_chart_from_pct(
                value_counts_pct(flt[COL_EMPLOYEES]),
                "category",
                "pct",
                "Company size (%)"
            )
        with c4:
            bar_chart_from_pct(
                value_counts_pct(flt[COL_INDUSTRY]),
                "category",
                "pct",
                "Industry distribution (%)"
            )

    # ---------------- TAB 2: PERFORMANCE ----------------
    with tab_perf:
        create_section_header("Performance vs direct motion")

        p1, p2 = st.columns(2)
        with p1:
            bar_chart_from_pct(value_counts_pct(flt[COL_DEAL]), "category", "pct", "Deal size vs direct (%)")
        with p2:
            bar_chart_from_pct(value_counts_pct(flt[COL_CAC]), "category", "pct", "CAC vs direct (%)")

        create_section_header("Sales cycle & win rate")

        p3, p4 = st.columns(2)
        with p3:
            bar_chart_from_pct(value_counts_pct(flt[COL_SALES]), "category", "pct", "Sales cycle vs direct (%)")
        with p4:
            win_rate_distribution_pct(flt, COL_WIN)

    # ---------------- TAB 3: GEOGRAPHY ----------------
    with tab_geo:
        create_section_header("Regional distribution")

        region_pct = value_counts_pct(flt["RegionStd"])

        g1, g2 = st.columns(2)
        with g1:
            donut_chart_with_labels(region_pct, "category", "pct", "Region share (%)")
        with g2:
            bar_chart_from_pct(region_pct, "category", "pct", "Region share (%)")

        create_section_header("World map — bubble size = % of respondents")

        coords = {
            "North America": (40, -100),
            "Latin America": (-20, -60),
            "Europe": (50, 10),
            "Asia Pacific": (20, 100),
        }

        map_df = region_pct.copy()
        map_df["lat"] = map_df["category"].map(lambda r: coords.get(r, (None, None))[0])
        map_df["lon"] = map_df["category"].map(lambda r: coords.get(r, (None, None))[1])
        map_df = map_df.dropna(subset=["lat", "lon"])

        if len(map_df) > 0:
            layer = pdk.Layer(
                "ScatterplotLayer",
                map_df,
                get_position=["lon", "lat"],
                get_radius="pct * 120000",
                get_fill_color=[59, 48, 143, 200],
                pickable=True,
            )
            view = pdk.ViewState(latitude=20, longitude=0, zoom=1)
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view,
                tooltip={"text": "{category}: {pct}%"}
            )
            st.pydeck_chart(deck)

    # ---------------- TAB 4: MULTI-SELECT ----------------
    with tab_multi:
        create_section_header("Partner & Impact metrics")
        st.info("Send exact column patterns for multi-select questions if you want these auto-visualized.")

    # ---------------- TAB 5: DATA ----------------
    with tab_data:
        create_section_header("Filtered data")
        st.dataframe(flt, use_container_width=True)

        csv = flt.to_csv(index=False).encode("utf-8")
        st.download_button("Download filtered CSV", csv, "sopl_filtered.csv", "text/csv")

    # ---------------- ASSISTANT ----------------
    st.markdown("<h2>Assistant (SOPL Q&A)</h2>", unsafe_allow_html=True)
    components.html(
        """
        <div id="deployment-5870ff7d-8fcf-4395-976b-9e9fdefbb0ff"></div>
        <script src="https://studio.pickaxe.co/api/embed/bundle.js" defer></script>
        """,
        height=650,
        scrolling=True
    )

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
