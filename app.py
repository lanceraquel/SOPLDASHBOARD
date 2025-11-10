# app.py — SOPL 2024 Professional Dashboard
import os
import io
import re
import unicodedata
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from difflib import SequenceMatcher

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SOPL 2025 Insights Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* Main styles */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: white;
    }
    
    /* Header styles */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Card styles */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* Chart containers */
    .chart-container {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: rgba(30, 41, 59, 0.7);
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        color: #94a3b8;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: white !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        background: rgba(30, 41, 59, 0.7) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== COLOR SCHEME ====================
HOUSE_COLORS = ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe", "#00f2fe", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]

def dark_theme():
    return {
        "config": {
            "view": {"stroke": "transparent"},
            "background": "rgba(30, 41, 59, 0)",
            "range": {"category": HOUSE_COLORS},
            "axis": {
                "labelColor": "#94a3b8",
                "titleColor": "#f1f5f9",
                "titleFontWeight": 600,
                "gridColor": "#334155",
                "gridWidth": 0.5,
                "domainColor": "#475569",
                "tickColor": "#475569"
            },
            "legend": {
                "labelColor": "#94a3b8",
                "titleColor": "#f1f5f9",
                "titleFontWeight": 600,
                "background": "rgba(30, 41, 59, 0.8)",
                "strokeColor": "#475569"
            },
            "title": {
                "color": "#f1f5f9",
                "fontSize": 16,
                "fontWeight": 700,
                "anchor": "start"
            }
        }
    }

alt.themes.register("dark", dark_theme)
alt.themes.enable("dark")

# ==================== DATA PROCESSING FUNCTIONS ====================
LOCAL_FALLBACK = "data/SOPL 1002 Results - Raw.csv"

def normalize(txt: str) -> str:
    if txt is None: return ""
    t = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode("ascii")
    t = t.replace("'", "'").replace("–", "-").replace("—", "-")
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def best_match(candidates, cols_norm, cols_raw):
    for cand in candidates:
        nc = normalize(cand)
        if nc in cols_norm:
            return cols_norm[nc]
    cand_tokens = [set(normalize(c).split()) for c in candidates]
    best = (0.0, None)
    for raw in cols_raw:
        nr = normalize(raw)
        for toks in cand_tokens:
            if not toks: continue
            overlap = len(toks & set(nr.split())) / max(1, len(toks))
            if overlap > best[0]:
                best = (overlap, raw)
    if best[1] is None or best[0] < 0.5:
        for cand in candidates:
            nc = normalize(cand)
            for raw in cols_raw:
                sim = SequenceMatcher(a=nc, b=normalize(raw)).ratio()
                if sim > best[0]:
                    best = (sim, raw)
    return best[1] if best[0] >= 0.5 else None

@st.cache_data(show_spinner=False)
def load_raw(uploaded):
    if uploaded is not None:
        name = (uploaded.name or "").lower()
        if name.endswith((".xlsx", ".xls")):
            try: return pd.read_excel(uploaded)
            except Exception as e: st.warning(f"Excel read failed: {e}")
        try:
            data = uploaded.getvalue()
        except Exception:
            uploaded.seek(0); data = uploaded.read()
        encs = ["utf-8-sig","utf-8","cp1252","latin-1"]
        seps = [None, ",", "\t", ";", "|"]
        for enc in encs:
            for sep in seps:
                try:
                    buf = io.BytesIO(data)
                    df = pd.read_csv(buf, encoding=enc, sep=sep, engine="python", on_bad_lines="skip", encoding_errors="replace")
                    if df.shape[1] >= 2:
                        return df
                except Exception:
                    pass
        st.error("Could not decode upload. Try XLSX or re-save CSV as UTF-8.")
    
    if os.path.exists(LOCAL_FALLBACK):
        if LOCAL_FALLBACK.lower().endswith((".xlsx",".xls")):
            try: return pd.read_excel(LOCAL_FALLBACK)
            except Exception as e: st.warning(f"Local Excel fallback failed: {e}")
        try:
            return pd.read_csv(LOCAL_FALLBACK, sep=None, engine="python")
        except Exception:
            for enc in ["utf-8-sig","utf-8","cp1252","latin-1"]:
                try:
                    return pd.read_csv(LOCAL_FALLBACK, encoding=enc, sep=None, engine="python", on_bad_lines="skip", encoding_errors="replace")
                except Exception:
                    pass
            st.error("Local fallback exists but could not be decoded.")
    return pd.DataFrame()

SYN = {
    "company_name": ["Company name", "Company", "Your company name"],
    "region": ["Please select the region where your company is headquartered.", "Region", "Company region", "HQ region"],
    "industry": ["What industry sector does your company operate in?", "Industry", "Industry sector", "Company industry"],
    "revenue_band": ["What is your company's estimated annual revenue?", "Estimated annual revenue", "Annual revenue band", "Revenue band"],
    "employee_count_bin": ["What is your company's total number of employees?", "Total number of employees", "Employee count", "Company size"],
    "partner_team_size_bin": ["How many people are on your Partnerships team?", "Partnerships team size", "Partner team size"],
    "total_partners_bin": ["How many total partners do you have?", "Total partners"],
    "active_partners_bin": ["How many active partners generated revenue in the last 12 months?", "Active partners generated revenue in last 12 months", "Active partners"],
    "time_to_first_revenue_bin": ["How long does it typically take for a partnership to generate revenue after the first meeting?", "Time to first partner revenue", "Time to first revenue"],
    "program_years_bin": ["How long has your company had a partnership program?", "Program tenure", "Years running partner program"],
    "expected_partner_revenue_pct": ["On average, what percentage of your company's revenue is expected to come from partnerships in the next 12 months?", "Expected revenue from partnerships (next 12 months)", "Expected partner revenue percent", "Expected partner revenue %"],
    "marketplace_revenue_pct": ["What percentage of your total revenue comes through cloud marketplaces?", "Revenue through cloud marketplaces", "Cloud marketplace revenue %"],
    "top_challenge": ["What's your biggest challenge in scaling your partner program?", "What is your biggest challenge in scaling your partner program?", "Biggest challenge", "Top challenge"],
}

EMPLOYEES_MAP = {"Less than 100 employees": 50.0, "100 – 500 employees": 300.0, "100 - 500 employees": 300.0, "501 – 5,000 employees": 2500.0, "501 - 5,000 employees": 2500.0, "More than 5,000 employees": 8000.0}
TEAM_SIZE_MAP = {"Less than 10": 5.0, "10–50": 30.0, "10-50": 30.0, "51–200": 125.0, "51-200": 125.0, "More than 200": 300.0}
TOTAL_PARTNERS_MAP = {"Less than 50": 25.0, "50 – 499": 275.0, "50 - 499": 275.0, "500 – 999": 750.0, "500 - 999": 750.0, "1,000 – 4,999": 3000.0, "1,000 - 4,999": 3000.0, "5,000+": 6000.0}
ACTIVE_PARTNERS_MAP = {"Less than 10": 5.0, "10 – 99": 55.0, "10 - 99": 55.0, "100 – 499": 300.0, "100 - 499": 300.0, "500 – 999": 750.0, "500 - 999": 750.0, "1,000+": 1200.0, "Not currently monitored": np.nan}
TTF_REVENUE_MAP = {"Less than 1 year": 0.5, "1–2 years": 1.5, "1-2 years": 1.5, "2–3 years": 2.5, "2-3 years": 2.5, "3–5 years": 4.0, "3-5 years": 4.0, "6–10 years": 8.0, "6-10 years": 8.0, "More than 10 years": 12.0, "I don't have this data": np.nan}

def to_pct_numeric(x):
    if pd.isna(x): return np.nan
    s = str(x).strip().replace("%","")
    try: return float(s)
    except: return np.nan

def map_region_short(x: str) -> str:
    if pd.isna(x): return x
    s = str(x)
    if "North America" in s: return "NA"
    if "Latin America" in s: return "LATAM"
    if "Asia-Pacific" in s or "APAC" in s: return "APAC"
    if "Europe" in s or "EMEA" in s: return "EMEA"
    return s

def maturity_from_years(x: str) -> str:
    if pd.isna(x): return "Unknown"
    s = str(x)
    if "Less than 1 year" in s: return "Early"
    if "1-2" in s or "1–2" in s: return "Early"
    if "2-3" in s or "2–3" in s: return "Developing"
    if "3-5" in s or "3–5" in s: return "Developing"
    if "6-10" in s or "6–10" in s: return "Mature"
    if "More than 10 years" in s: return "Mature"
    return "Unknown"

def mid_from_bins(label: str, mapping: dict) -> float | None:
    if pd.isna(label): return None
    val = mapping.get(str(label).strip())
    if val is None:
        alt_label = str(label).replace("–","-")
        val = mapping.get(alt_label.strip())
    return val

def resolve_headers(df_raw: pd.DataFrame) -> dict:
    cols = list(df_raw.columns)
    cols_norm = {normalize(c): c for c in cols}
    found = {}
    for key, variants in SYN.items():
        col = best_match(variants, cols_norm, cols)
        found[key] = col
    return found

def standardize(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict, list]:
    mapping = resolve_headers(df_raw)
    missing_keys = [k for k, v in mapping.items() if v is None]
    missing_readable = []
    for k in missing_keys:
        missing_readable.append(SYN[k][0])

    if missing_readable:
        st.error("Missing expected columns in CSV:\n- " + "\n- ".join(missing_readable))

    def col(k): return mapping.get(k)

    d = pd.DataFrame()
    if col("company_name") in df_raw: d["company_name"] = df_raw[col("company_name")]
    if col("region") in df_raw: d["region"] = df_raw[col("region")].map(map_region_short)
    if col("industry") in df_raw: d["industry"] = df_raw[col("industry")]
    if col("revenue_band") in df_raw: d["revenue_band"] = df_raw[col("revenue_band")]
    if col("employee_count_bin") in df_raw: d["employee_count_bin"] = df_raw[col("employee_count_bin")]
    if col("partner_team_size_bin") in df_raw: d["partner_team_size_bin"] = df_raw[col("partner_team_size_bin")]
    if col("total_partners_bin") in df_raw: d["total_partners_bin"] = df_raw[col("total_partners_bin")]
    if col("active_partners_bin") in df_raw: d["active_partners_bin"] = df_raw[col("active_partners_bin")]
    if col("time_to_first_revenue_bin") in df_raw: d["time_to_first_revenue_bin"] = df_raw[col("time_to_first_revenue_bin")]
    if col("program_years_bin") in df_raw: d["program_years_bin"] = df_raw[col("program_years_bin")]
    if col("expected_partner_revenue_pct") in df_raw:
        d["expected_partner_revenue_pct"] = df_raw[col("expected_partner_revenue_pct")].apply(to_pct_numeric)
    if col("marketplace_revenue_pct") in df_raw:
        d["marketplace_revenue_pct"] = df_raw[col("marketplace_revenue_pct")].apply(to_pct_numeric)
    if col("top_challenge") in df_raw: d["top_challenge"] = df_raw[col("top_challenge")]

    if "employee_count_bin" in d: d["employee_count_est"] = d["employee_count_bin"].apply(lambda x: mid_from_bins(x, EMPLOYEES_MAP))
    if "partner_team_size_bin" in d: d["partner_team_size_est"] = d["partner_team_size_bin"].apply(lambda x: mid_from_bins(x, TEAM_SIZE_MAP))
    if "total_partners_bin" in d: d["total_partners_est"] = d["total_partners_bin"].apply(lambda x: mid_from_bins(x, TOTAL_PARTNERS_MAP))
    if "active_partners_bin" in d: d["active_partners_est"] = d["active_partners_bin"].apply(lambda x: mid_from_bins(x, ACTIVE_PARTNERS_MAP))
    if "time_to_first_revenue_bin" in d: d["time_to_first_revenue_years"] = d["time_to_first_revenue_bin"].apply(lambda x: mid_from_bins(x, TTF_REVENUE_MAP))
    if "program_years_bin" in d: d["program_maturity"] = d["program_years_bin"].apply(maturity_from_years)

    if {"active_partners_est","total_partners_est"}.issubset(d.columns):
        d["partners_active_ratio"] = d["active_partners_est"] / d["total_partners_est"]
    if {"expected_partner_revenue_pct","partner_team_size_est"}.issubset(d.columns):
        d["expected_partner_revenue_per_partner"] = d["expected_partner_revenue_pct"] / d["partner_team_size_est"]

    return d, mapping, missing_readable

# ==================== ENHANCED UI COMPONENTS ====================
def create_metric_card(value, label, change=None, format_str="{:.1f}", help_text=None):
    """Create a beautiful metric card"""
    with st.container():
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_str.format(value) if value != '—' else '—'}</div>
            <div class="metric-label">{label}</div>
            {f'<div style="font-size: 0.8rem; color: #10B981; font-weight: 600; margin-top: 0.5rem;">{change}</div>' if change else ''}
        </div>
        """, unsafe_allow_html=True)
        if help_text:
            st.caption(help_text)

def create_section_header(title, description=None, icon="📊"):
    """Create a beautiful section header"""
    st.markdown(f"""
    <div class="section-header">
        {icon} {title}
    </div>
    """, unsafe_allow_html=True)
    if description:
        st.markdown(f'<p style="color: #94a3b8; margin-bottom: 1.5rem;">{description}</p>', unsafe_allow_html=True)

def render_chart(chart: alt.Chart, name: str, height=300):
    """Render chart with download button"""
    chart = chart.properties(height=height)
    with st.container():
        st.altair_chart(chart, use_container_width=True)
        try:
            import vl_convert as vlc
            png = vlc.vegalite_to_png(chart.to_dict(), scale=2)
            st.download_button(f"📥 Download {name}", png, file_name=f"{name}.png", mime="image/png")
        except Exception:
            pass

# ==================== MAIN APP ====================
def main():
    # Header Section
    col_header1, col_header2 = st.columns([3, 1])
    
    with col_header1:
        st.markdown('<div class="main-header">SOPL 2024 Insights Platform</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Advanced analytics for partnership program performance and industry benchmarks</div>', unsafe_allow_html=True)
    
    with col_header2:
        st.markdown("")
        with st.expander("⚙️ Data Source", expanded=False):
            uploaded = st.file_uploader("Upload SOPL Data", type=["csv","xlsx","xls"], label_visibility="collapsed")

    # Load Data
    with st.spinner("🚀 Loading and processing data..."):
        raw = load_raw(uploaded)
    
    if raw.empty:
        st.error("""
        ## 📊 No Data Loaded
        
        Please upload a SOPL data file to begin analysis.
        Supported formats: CSV, Excel (.xlsx, .xls)
        """)
        return

    # Process Data
    df, mapping, missing = standardize(raw)
    if df.empty:
        st.error("Unable to process the uploaded file. Please check the format and try again.")
        return

    # Quick Stats Bar
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("Total Companies", f"{len(df):,}")
    with col_stat2:
        industries_count = df['industry'].nunique() if 'industry' in df.columns else 0
        st.metric("Industries", f"{industries_count}")
    with col_stat3:
        regions_count = df['region'].nunique() if 'region' in df.columns else 0
        st.metric("Regions", f"{regions_count}")
    with col_stat4:
        st.metric("Data Quality", f"{(1 - len(missing)/len(SYN)) * 100:.1f}%")

    st.markdown("---")

    # Initialize filter variables
    industries = []
    regions = []
    maturity_levels = []
    revenue_bands = []

    # Filters in Sidebar
    with st.sidebar:
        st.markdown("### 🔍 Filters")
        
        # Quick Filters - with safe column existence checks
        if 'industry' in df.columns:
            industry_options = sorted(df['industry'].dropna().unique())
            industries = st.multiselect("Industries", options=industry_options, 
                                      default=industry_options[:5] if len(industry_options) > 5 else industry_options)
        
        if 'region' in df.columns:
            region_options = sorted(df['region'].dropna().unique())
            regions = st.multiselect("Regions", options=region_options, 
                                   default=region_options)
        
        if 'program_maturity' in df.columns:
            maturity_options = sorted(df['program_maturity'].dropna().unique())
            maturity_levels = st.multiselect("Program Maturity", options=maturity_options,
                                           default=maturity_options)
        
        if 'revenue_band' in df.columns:
            revenue_options = sorted(df['revenue_band'].dropna().unique())
            revenue_bands = st.multiselect("Revenue Bands", options=revenue_options,
                                         default=revenue_options)

    # Apply Filters safely
    flt = df.copy()
    if 'industry' in flt and industries:
        flt = flt[flt['industry'].isin(industries)]
    if 'region' in flt and regions:
        flt = flt[flt['region'].isin(regions)]
    if 'program_maturity' in flt and maturity_levels:
        flt = flt[flt['program_maturity'].isin(maturity_levels)]
    if 'revenue_band' in flt and revenue_bands:
        flt = flt[flt['revenue_band'].isin(revenue_bands)]

    # Main Dashboard Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🤝 Partnerships", "🚀 Performance", "📊 Explore Data"])
    
    with tab1:
        create_section_header("Key Performance Indicators", "Core metrics across your partnership portfolio")
        
        # KPI Grid
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if "expected_partner_revenue_pct" in flt.columns and not flt["expected_partner_revenue_pct"].isna().all():
                median_val = flt["expected_partner_revenue_pct"].median()
                create_metric_card(median_val, "Expected Partner Revenue", f"{median_val:.1f}%", help_text="Median expected revenue from partnerships")
            else:
                create_metric_card("—", "Expected Partner Revenue", help_text="No data available")
        
        with col2:
            if "marketplace_revenue_pct" in flt.columns and not flt["marketplace_revenue_pct"].isna().all():
                median_val = flt["marketplace_revenue_pct"].median()
                create_metric_card(median_val, "Marketplace Revenue", f"{median_val:.1f}%", help_text="Revenue through cloud marketplaces")
            else:
                create_metric_card("—", "Marketplace Revenue", help_text="No data available")
        
        with col3:
            if "partner_team_size_est" in flt.columns and not flt["partner_team_size_est"].isna().all():
                median_val = flt["partner_team_size_est"].median()
                create_metric_card(median_val, "Team Size", f"{median_val:.0f} people", "{:.0f}", help_text="Median partner team size")
            else:
                create_metric_card("—", "Team Size", help_text="No data available")
        
        with col4:
            if "time_to_first_revenue_years" in flt.columns and not flt["time_to_first_revenue_years"].isna().all():
                median_val = flt["time_to_first_revenue_years"].median()
                create_metric_card(median_val, "Time to Revenue", f"{median_val:.1f} yrs", help_text="Years to first partnership revenue")
            else:
                create_metric_card("—", "Time to Revenue", help_text="No data available")

        st.markdown("---")
        
        # Charts Row 1
        create_section_header("Revenue Analysis", "Distribution and trends in partnership revenue")
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if {"expected_partner_revenue_pct","program_maturity"}.issubset(flt.columns):
                d = flt[["program_maturity", "expected_partner_revenue_pct"]].dropna()
                if not d.empty:
                    chart = alt.Chart(d).mark_boxplot(size=30).encode(
                        x=alt.X("program_maturity:N", title="Program Maturity", sort=["Early", "Developing", "Mature"]),
                        y=alt.Y("expected_partner_revenue_pct:Q", title="Expected Partner Revenue (%)"),
                        color=alt.Color("program_maturity:N", scale=alt.Scale(range=HOUSE_COLORS), legend=None)
                    ).properties(title="Revenue Distribution by Program Maturity", height=300)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No data available for revenue distribution")
            else:
                st.info("Revenue distribution data not available")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_chart2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if {"region","expected_partner_revenue_pct"}.issubset(flt.columns):
                d = flt[["region","expected_partner_revenue_pct"]].dropna()
                if not d.empty:
                    chart = alt.Chart(d).mark_bar(size=35).encode(
                        x=alt.X("region:N", title="Region", sort=["NA", "EMEA", "APAC", "LATAM"]),
                        y=alt.Y("mean(expected_partner_revenue_pct):Q", title="Average Expected Revenue (%)"),
                        color=alt.Color("region:N", scale=alt.Scale(range=HOUSE_COLORS), legend=None),
                        tooltip=["region", "mean(expected_partner_revenue_pct)"]
                    ).properties(title="Average Revenue by Region", height=300)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No data available for regional analysis")
            else:
                st.info("Regional revenue data not available")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        create_section_header("Partnership Analytics", "Deep dive into partner relationships and performance")
        
        col_part1, col_part2 = st.columns(2)
        
        with col_part1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if {"total_partners_est", "active_partners_est"}.issubset(flt.columns):
                if not flt["total_partners_est"].isna().all() and not flt["active_partners_est"].isna().all():
                    summary_data = pd.DataFrame({
                        'Type': ['Total Partners', 'Active Partners'],
                        'Count': [flt['total_partners_est'].median(), flt['active_partners_est'].median()]
                    })
                    
                    chart = alt.Chart(summary_data).mark_bar(size=50).encode(
                        x=alt.X('Type:N', title=''),
                        y=alt.Y('Count:Q', title='Median Count'),
                        color=alt.Color('Type:N', scale=alt.Scale(range=HOUSE_COLORS[:2]), legend=None)
                    ).properties(title="Partner Portfolio Size", height=300)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No partner count data available")
            else:
                st.info("Partner portfolio data not available")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_part2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if {"top_challenge","program_maturity"}.issubset(flt.columns):
                d = flt[["top_challenge","program_maturity"]].dropna()
                if not d.empty:
                    counts = d.groupby(["program_maturity","top_challenge"]).size().reset_index(name='count')
                    top_challenges = counts.groupby('top_challenge')['count'].sum().nlargest(8).index
                    counts = counts[counts['top_challenge'].isin(top_challenges)]
                    
                    chart = alt.Chart(counts).mark_bar().encode(
                        x=alt.X('sum(count):Q', title='Number of Responses'),
                        y=alt.Y('top_challenge:N', title='Challenge', sort='-x'),
                        color=alt.Color('program_maturity:N', scale=alt.Scale(range=HOUSE_COLORS), title='Maturity'),
                        tooltip=['top_challenge', 'program_maturity', 'count']
                    ).properties(title="Top Challenges by Program Maturity", height=400)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No challenge data available")
            else:
                st.info("Challenge analysis data not available")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        create_section_header("Performance Benchmarks", "Compare your performance against industry standards")
        
        # Performance Metrics
        col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)
        
        with col_perf1:
            if "partners_active_ratio" in flt.columns and not flt["partners_active_ratio"].isna().all():
                activation_median = flt["partners_active_ratio"].median()
                create_metric_card(activation_median, "Activation Rate", f"{activation_median:.1%}", "{:.2f}")
            else:
                create_metric_card("—", "Activation Rate")
        
        with col_perf2:
            if "expected_partner_revenue_per_partner" in flt.columns and not flt["expected_partner_revenue_per_partner"].isna().all():
                revenue_per_partner = flt["expected_partner_revenue_per_partner"].median()
                create_metric_card(revenue_per_partner, "Revenue per Partner", f"${revenue_per_partner:.0f}", "{:.0f}")
            else:
                create_metric_card("—", "Revenue per Partner")
        
        with col_perf3:
            if {"partner_team_size_est", "employee_count_est"}.issubset(flt.columns):
                if not flt["partner_team_size_est"].isna().all() and not flt["employee_count_est"].isna().all():
                    team_per_1k = (flt["partner_team_size_est"] / (flt["employee_count_est"] / 1000)).median()
                    create_metric_card(team_per_1k, "Team per 1K Employees", f"{team_per_1k:.1f}", "{:.1f}")
                else:
                    create_metric_card("—", "Team per 1K Employees")
            else:
                create_metric_card("—", "Team per 1K Employees")
        
        with col_perf4:
            if "total_partners_est" in flt.columns and "active_partners_est" in flt.columns:
                if not flt["total_partners_est"].isna().all() and not flt["active_partners_est"].isna().all():
                    total_active_ratio = flt["active_partners_est"].sum() / flt["total_partners_est"].sum()
                    create_metric_card(total_active_ratio, "Overall Activation", f"{total_active_ratio:.1%}", "{:.2f}")
                else:
                    create_metric_card("—", "Overall Activation")
            else:
                create_metric_card("—", "Overall Activation")

        st.markdown("---")
        
        # Performance Charts
        col_perf_chart1, col_perf_chart2 = st.columns(2)
        
        with col_perf_chart1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if {"industry","partners_active_ratio"}.issubset(flt.columns):
                d2 = flt[["industry","partners_active_ratio"]].dropna()
                if not d2.empty:
                    topN = d2["industry"].value_counts().head(10).index.tolist()
                    d2 = d2[d2["industry"].isin(topN)]
                    agg2 = d2.groupby("industry")["partners_active_ratio"].median().sort_values(ascending=False).reset_index()
                    bars2 = alt.Chart(agg2).mark_bar(size=25).encode(
                        x=alt.X("partners_active_ratio:Q", title="Median Activation Ratio"),
                        y=alt.Y("industry:N", sort="-x", title="Industry"),
                        color=alt.Color("industry:N", legend=None, scale=alt.Scale(range=HOUSE_COLORS)),
                        tooltip=["industry", alt.Tooltip("partners_active_ratio:Q", format=".2f")]
                    ).properties(title="Activation Ratio by Industry (Top 10)", height=400)
                    st.altair_chart(bars2, use_container_width=True)
                else:
                    st.info("No activation ratio data available by industry")
            else:
                st.info("Industry activation data not available")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_perf_chart2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            if {"program_maturity","industry","time_to_first_revenue_years"}.issubset(flt.columns):
                d = flt[["program_maturity","industry","time_to_first_revenue_years"]].dropna()
                if not d.empty:
                    top_ind = d["industry"].value_counts().head(8).index.tolist()
                    d = d[d["industry"].isin(top_ind)]
                    chart = alt.Chart(d).mark_rect().encode(
                        x=alt.X("program_maturity:N", title="Program Maturity"),
                        y=alt.Y("industry:N", title="Industry"),
                        color=alt.Color("mean(time_to_first_revenue_years):Q", title="Mean Years"),
                        tooltip=["industry","program_maturity", alt.Tooltip("mean(time_to_first_revenue_years):Q", format=".2f")]
                    ).properties(title="Time to Revenue by Maturity × Industry", height=400)
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("No time to revenue data available")
            else:
                st.info("Time to revenue data not available")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        create_section_header("Data Explorer", "Interactive data exploration and export")
        
        # Data Table with Filters
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            show_columns = st.multiselect("Select Columns", 
                                        options=flt.columns.tolist(), 
                                        default=flt.columns.tolist()[:6])
        
        with col_filter2:
            rows_to_show = st.slider("Rows to display", 10, 100, 20)
        
        with col_filter3:
            st.markdown("")
            st.markdown("")
            csv = flt[show_columns].to_csv(index=False)
            st.download_button(
                "📥 Export Filtered Data",
                csv,
                "sopl_2024_data.csv",
                "text/csv",
                use_container_width=True
            )
        
        # Data Table
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.dataframe(flt[show_columns].head(rows_to_show), use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #94a3b8; font-size: 0.9rem; padding: 2rem;'>"
        "SOPL 2024 Insights Platform • Built with Streamlit • Professional Analytics Dashboard"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
