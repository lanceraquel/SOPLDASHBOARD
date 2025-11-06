# app.py — SOPL 2024 Dashboard - Professional Edition

import os, io, re, unicodedata
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from difflib import SequenceMatcher

st.set_page_config(page_title="SOPL 2024 – Interactive", page_icon="📊", layout="wide")

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main {
        padding: 0rem 1rem 2rem 1rem;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2rem 2.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .dashboard-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .dashboard-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #e1e8ed;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 2rem 0 1.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    .section-header h2 {
        color: white;
        margin: 0;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    h2, h3 {
        color: #1a1a2e;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-right: 1px solid #e1e8ed;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #1a1a2e;
        font-weight: 600;
    }
    
    /* Filter chips */
    .stMultiSelect [data-baseweb="tag"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 6px;
        font-weight: 500;
    }
    
    /* Buttons */
    .stDownloadButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 8px;
        font-weight: 600;
        color: #1a1a2e;
    }
    
    /* Dividers */
    hr {
        margin: 2.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #e1e8ed 50%, transparent 100%);
    }
    
    /* Data tables */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e1e8ed;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-bottom: 1.5rem;
    }
    
    /* Cohort comparison cards */
    .cohort-card {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e1e8ed;
        margin-bottom: 1rem;
    }
    
    /* Stats badge */
    .stats-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

HOUSE_COLORS = ["#667eea", "#764ba2", "#f093fb", "#4facfe", "#43e97b", "#fa709a", "#fee140"]
def house_theme():
    return {
        "config": {
            "range": {"category": HOUSE_COLORS, "heatmap": {"scheme": "purples"}},
            "axis": {"labelColor": "#64748b", "titleColor": "#1a1a2e", "gridColor": "#e1e8ed", 
                     "domainColor": "#e1e8ed", "tickColor": "#e1e8ed"},
            "legend": {"labelColor": "#64748b", "titleColor": "#1a1a2e"},
            "title": {"color": "#1a1a2e", "fontSize": 16, "fontWeight": 600, "anchor": "start"},
            "background": None,
            "view": {"strokeWidth": 0},
        }
    }
alt.themes.register("house", house_theme)
alt.themes.enable("house")

LOCAL_FALLBACK = "data/SOPL 1002 Results - Raw.csv"

# -------------------- Normalization & fuzzy header mapping --------------------
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

# -------------------- Robust loader (CSV/Excel, any encoding) --------------------
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
                    df = pd.read_csv(buf, encoding=enc, sep=sep, engine="python",
                                     on_bad_lines="skip", encoding_errors="replace")
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
                    return pd.read_csv(LOCAL_FALLBACK, encoding=enc, sep=None, engine="python",
                                       on_bad_lines="skip", encoding_errors="replace")
                except Exception:
                    pass
            st.error("Local fallback exists but could not be decoded.")
    return pd.DataFrame()

# -------------------- Expected survey fields & synonyms --------------------
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

# -------------------- Numeric mappings for bins --------------------
EMPLOYEES_MAP = {"Less than 100 employees": 50.0, "100 – 500 employees": 300.0, "100 - 500 employees": 300.0, "501 – 5,000 employees": 2500.0, "501 - 5,000 employees": 2500.0, "More than 5,000 employees": 8000.0}
TEAM_SIZE_MAP = {"Less than 10": 5.0, "10–50": 30.0, "10-50": 30.0, "51–200": 125.0, "51-200": 125.0, "More than 200": 300.0}
TOTAL_PARTNERS_MAP = {"Less than 50": 25.0, "50 – 499": 275.0, "50 - 499": 275.0, "500 – 999": 750.0, "500 - 999": 750.0, "1,000 – 4,999": 3000.0, "1,000 - 4,999": 3000.0, "5,000+": 6000.0}
ACTIVE_PARTNERS_MAP = {"Less than 10": 5.0, "10 – 99": 55.0, "10 - 99": 55.0, "100 – 499": 300.0, "100 - 499": 300.0, "500 – 999": 750.0, "500 - 999": 750.0, "1,000+": 1200.0, "Not currently monitored": np.nan}
TTF_REVENUE_MAP = {"Less than 1 year": 0.5, "1–2 years": 1.5, "1-2 years": 1.5, "2–3 years": 2.5, "2-3 years": 2.5, "3–5 years": 4.0, "3-5 years": 4.0, "6–10 years": 8.0, "6-10 years": 8.0, "More than 10 years": 12.0, "I don't have this data": np.nan}

# -------------------- Helpers for metrics/derived --------------------
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

def render_chart(chart: alt.Chart, name: str, height=None):
    if height is not None: chart = chart.properties(height=height)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    try:
        import vl_convert as vlc
        png = vlc.vegalite_to_png(chart.to_dict(), scale=2)
        st.download_button(f"📥 Download {name}", png, file_name=f"{name}.png", mime="image/png")
    except Exception:
        pass

# -------------------- Standardize using auto-mapped headers --------------------
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
        st.error("⚠️ Missing expected columns in CSV:\n- " + "\n- ".join(missing_readable))

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

# -------------------- MAIN --------------------
with st.sidebar:
    st.markdown("### 📁 Data Source")
    uploaded = st.file_uploader("Upload SOPL raw CSV or Excel", type=["csv","xlsx","xls"])
    st.markdown("---")

raw = load_raw(uploaded)
if raw.empty:
    st.info("📂 No data loaded. Upload a CSV/XLSX or commit a fallback at:\n" f"**{LOCAL_FALLBACK}**")
    st.stop()

df, mapping, missing = standardize(raw)
if df.empty:
    st.stop()

# Show mapping
with st.sidebar.expander("🔍 View Header Mapping"):
    mdf = pd.DataFrame({
        "Logical Field": list(mapping.keys()),
        "Matched Column": [mapping[k] if mapping[k] else "❌ Not found" for k in mapping.keys()]
    })
    st.dataframe(mdf, use_container_width=True)

# -------------------- Filters --------------------
with st.sidebar:
    st.markdown("### 🎯 Filters")
    def opts(col):
        return sorted(df[col].dropna().astype(str).unique().tolist()) if col in df else []

    rev_sel = st.multiselect("💰 Revenue Band", options=opts("revenue_band"), default=opts("revenue_band"))
    ind_sel = st.multiselect("🏢 Industry", options=opts("industry"), default=opts("industry"))
    reg_order = ["APAC","EMEA","LATAM","NA"]
    reg_all = opts("region")
    reg_sorted = [r for r in reg_order if r in reg_all] + [r for r in reg_all if r not in reg_order]
    reg_sel = st.multiselect("🌍 Region", options=reg_sorted, default=reg_sorted)
    mat_order = ["Early","Developing","Mature","Unknown"]
    mat_all = opts("program_maturity")
    mat_sorted = [m for m in mat_order if m in mat_all]
    mat_sel = st.multiselect("📈 Program Maturity", options=mat_sorted, default=mat_sorted)
    emp_sel = st.multiselect("👥 Employee Count", options=opts("employee_count_bin"), default=opts("employee_count_bin"))
    team_sel = st.multiselect("🤝 Partner Team Size", options=opts("partner_team_size_bin"), default=opts("partner_team_size_bin"))

flt = df.copy()
if "revenue_band" in flt and rev_sel: flt = flt[flt["revenue_band"].isin(rev_sel)]
if "industry" in flt and ind_sel: flt = flt[flt["industry"].isin(ind_sel)]
if "region" in flt and reg_sel: flt = flt[flt["region"].isin(reg_sel)]
if "program_maturity" in flt and mat_sel: flt = flt[flt["program_maturity"].isin(mat_sel)]
if "employee_count_bin" in flt and emp_sel: flt = flt[flt["employee_count_bin"].isin(emp_sel)]
if "partner_team_size_bin" in flt and team_sel: flt = flt[flt["partner_team_size_bin"].isin(team_sel)]

# -------------------- Header --------------------
st.markdown("""
<div class="dashboard-header">
    <h1 class="dashboard-title">📊 SOPL 2024 Partnership Insights</h1>
    <p class="dashboard-subtitle">Interactive Dashboard for Partnership Benchmarking & Analysis</p>
</div>
""", unsafe_allow_html=True)

# Sample size indicator
col_a, col_b, col_c = st.columns([2, 1, 1])
with col_a:
    st.markdown(f'<span class="stats-badge">📋 {len(flt):,} Responses (Filtered)</span> <span class="stats-badge">🌐 {len(df):,} Total</span>', unsafe_allow_html=True)

# -------------------- KPIs --------------------
def kpi(series, title, fmt="{:.1f}", icon="📊"):
    x = pd.to_numeric(series, errors="coerce") if series is not None else pd.Series(dtype=float)
    if x.dropna().empty:
        st.metric(f"{icon} {title}", "—", "—"); return
    m = np.median(x.dropna()); q1, q3 = np.percentile(x.dropna(), [25, 75]); n = x.dropna().shape[0]
    st.metric(f"{icon} {title}", fmt.format(m), f"IQR: {fmt.format(q1)}–{fmt.format(q3)} • N={n}")

st.markdown("#### 🎯 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi(flt.get("expected_partner_revenue_pct"), "Expected Partner Revenue (%)", icon="💰")
with col2:
    kpi(flt.get("marketplace_revenue_pct"), "Marketplace Revenue (%)", icon="☁️")
with col3:
    kpi(flt.get("partner_team_size_est"), "Partner Team Size", "{:.0f}", icon="👥")
with col4:
    kpi(flt.get("time_to_first_revenue_years"), "Time to Revenue (yrs)", icon="⏱️")

col5, col6, col7, col8 = st.columns(4)
with col5:
    kpi(flt.get("total_partners_est"), "Total Partners", "{:.0f}", icon="🤝")
with col6:
    kpi(flt.get("active_partners_est"), "Active Partners", "{:.0f}", icon="✅")
with col7:
    kpi(flt.get("partners_active_ratio"), "Activation Ratio", "{:.2f}", icon="📈")
with col8:
    if {"partner_team_size_est","employee_count_est"}.issubset(flt.columns):
        tpe = (flt["partner_team_size_est"] / (flt["employee_count_est"] / 1000)).replace([np.inf,-np.inf], np.nan)
        kpi(tpe, "Team per 1k FTE", "{:.2f}", icon="👨‍💼")
    else:
        st.metric("👨‍💼 Team per 1k FTE", "—", "—")

st.divider()

# -------------------- Expected partner revenue --------------------
if {"expected_partner_revenue_pct","program_maturity"}.issubset(flt.columns):
    st.markdown('<div class="section-header"><h2>💰 Expected Partner Revenue Analysis</h2></div>', unsafe_allow_html=True)
    
    for cohort_col, title, subtitle in [
        ("program_maturity", "by Program Maturity", "How revenue expectations evolve over time"),
        ("revenue_band", "by Company Revenue", "Correlation between company size and partner reliance")
    ]:
        if cohort_col not in flt or "expected_partner_revenue_pct" not in flt: continue
        d = flt[[cohort_col, "expected_partner_revenue_pct"]].dropna()
        if d.empty: continue
        
        st.markdown(f"**{title}** — _{subtitle}_")
        base = alt.Chart(d).transform_density(
            "expected_partner_revenue_pct", groupby=[cohort_col], as_=["value","density
