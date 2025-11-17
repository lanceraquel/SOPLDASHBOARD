# app.py — SOPL 2025 Executive Dashboard
import os
import io
import re
import unicodedata
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import streamlit.components.v1 as components
import pydeck as pdk
import json
from difflib import SequenceMatcher
from pathlib import Path

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="SOPL 2025 - Partnership Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CLEAN CSS ====================
st.markdown("""
<style>
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


    .theme-light {
        --bg: #f9fafb;
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
        color: var(--text);
        padding: 18px 24px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    }

    .header-row { display:flex; align-items:center; justify-content:space-between; gap:12px; }
    .main-header { font-size: 1.8rem; font-weight:800; margin:0; color:var(--text); }
    .sub-header { font-size:0.95rem; color:var(--muted); margin:0; }

    .metric-grid { display:flex; gap:12px; flex-wrap:wrap; }
    .metric-card {
        background: var(--panel);
        border-radius: 10px;
        padding: 14px;
        flex:1 1 220px;
        min-width: 180px;
        box-shadow: 0 6px 18px rgba(15,23,42,0.10);
        border: 1px solid rgba(15,23,42,0.06);
    }

    .metric-value { font-size: 1.6rem; font-weight:700; color:var(--text); }
    .metric-label { font-size:0.85rem; color:var(--muted); font-weight:600; }

    .section-header { font-size:1.1rem; font-weight:700; color:var(--text); margin-top:18px; margin-bottom:8px; }
    .card { background: var(--panel); border-radius:10px; padding:12px; border:1px solid rgba(15,23,42,0.06); }

    .status-pill { padding:6px 10px; border-radius:8px; font-weight:700; }

    /* small responsive tweaks */
    @media (max-width: 800px) {
        .header-row { flex-direction:column; align-items:flex-start; }
        .metric-grid { flex-direction:column; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIMPLE COLOR SCHEME ====================
# Atlas blue first
COLORS = ["#3b308f", "#4f46e5", "#10b981", "#f59e0b", "#6366f1", "#06b6d4", "#84cc16", "#f97316"]

def simple_theme():
    # darker theme (kept as an option)
    return {
        "config": {
            "view": {"stroke": "transparent"},
            "background": "#0b1120",
            "range": {"category": COLORS},
            "axis": {
                "labelColor": "#cbd5f5",
                "titleColor": "#e5e7eb",
                "titleFontWeight": 600,
                "gridColor": "#1e293b",
                "domainColor": "#1f2937"
            },
            "legend": {
                "labelColor": "#e5e7eb",
                "titleColor": "#e5e7eb",
                "titleFontWeight": 600,
            },
            "title": {
                "color": "#e5e7eb",
                "fontSize": 16,
                "fontWeight": 700,
                "anchor": "start"
            }
        }
    }

def light_theme():
    # light / Atlas blue theme
    return {
        "config": {
            "view": {"stroke": "transparent"},
            "background": "#ffffff",
            "range": {"category": COLORS},
            "axis": {
                "labelColor": "#64748b",
                "titleColor": "#020617",
                "titleFontWeight": 600,
                "gridColor": "#e2e8f0",
                "domainColor": "#cbd5e1"
            },
            "legend": {
                "labelColor": "#64748b",
                "titleColor": "#020617",
                "titleFontWeight": 600,
            },
            "title": {
                "color": "#020617",
                "fontSize": 16,
                "fontWeight": 700,
                "anchor": "start"
            }
        }
    }

alt.themes.register("simple", simple_theme)
alt.themes.register("light_simple", light_theme)
alt.themes.enable("light_simple")

# ==================== DATA PROCESSING ====================
APP_DIR = Path(__file__).parent
LOCAL_FALLBACK = APP_DIR / "data" / "SOPL 1002 Results - Raw.csv"

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
def load_raw(uploaded, encoding_override: str | None = None):
    """Load an uploaded file (CSV/XLSX) with robust encoding handling."""
    if uploaded is not None:
        name = (uploaded.name or "").lower()
        if name.endswith((".xlsx", ".xls")):
            try:
                return pd.read_excel(uploaded)
            except Exception as e:
                st.warning(f"Excel read failed: {e}")
        try:
            data = uploaded.getvalue()
        except Exception:
            uploaded.seek(0)
            data = uploaded.read()

        encs = ["cp1252", "utf-8-sig", "utf-8", "latin-1"]
        if encoding_override and encoding_override != "auto":
            encs = [encoding_override]
        seps = [None, ",", "\t", ";", "|"]

        for allow_replace in (False, True):
            for enc in encs:
                for sep in seps:
                    try:
                        buf = io.BytesIO(data)
                        if allow_replace:
                            df = pd.read_csv(buf, encoding=enc, sep=sep, engine="python",
                                             on_bad_lines="skip", encoding_errors="replace")
                        else:
                            df = pd.read_csv(buf, encoding=enc, sep=sep, engine="python",
                                             on_bad_lines="skip")
                        if df.shape[1] >= 2:
                            df = _repair_replacement_chars(df)
                            return df
                    except Exception:
                        continue
        st.error("Could not decode upload. Try XLSX or re-save CSV as UTF-8.")

    # Fallback to local file if present — "data living in there permanently"
    # Fallback to local file if present
    if LOCAL_FALLBACK.exists():
        lf = str(LOCAL_FALLBACK)
        if lf.lower().endswith((".xlsx", ".xls")):
            try:
                return pd.read_excel(lf)
            except Exception as e:
                st.warning(f"Local Excel fallback failed: {e}")

        encs2 = ["cp1252", "utf-8-sig", "utf-8", "latin-1"]
        if encoding_override and encoding_override != "auto":
            encs2 = [encoding_override]
        for allow_replace in (False, True):
            for enc in encs2:
                try:
                    if allow_replace:
                        df = pd.read_csv(lf, encoding=enc, sep=None, engine="python",
                                         on_bad_lines="skip", encoding_errors="replace")
                    else:
                        df = pd.read_csv(lf, encoding=enc, sep=None, engine="python",
                                         on_bad_lines="skip")
                    df = _repair_replacement_chars(df)
                    return df
                except Exception:
                    continue
        st.error(f"Local fallback exists at {lf} but could not be decoded.")
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
    "expected_partner_revenue_pct": ["On average, what percentage of your company's revenue is expected to come from partnerships in the next 12 months?", "Expected revenue from partnerships (next 12 months)", "Expected partner revenue percent"],
    "deal_size_comparison": ["How does your average deal size involving partners compare to direct or non-partner deals?", "Deal size comparison"],
    "win_rate": ["What's your win rate for deals where partners are involved?", "Win rate with partners"],
    "cac_comparison": ["How does your customer acquisition cost (CAC) from partners compared to direct sales and marketing?", "CAC comparison"],
    "sales_cycle_comparison": ["How does your partner-led sales cycle compare to your direct sales cycle?", "Sales cycle comparison"],
}

EMPLOYEES_MAP = {"Less than 100 employees": 50.0, "100 – 500 employees": 300.0, "100 - 500 employees": 300.0, "501 – 5,000 employees": 2500.0, "501 - 5,000 employees": 2500.0, "More than 5,000 employees": 8000.0}
TEAM_SIZE_MAP = {"Less than 10": 5.0, "10–50": 30.0, "10-50": 30.0, "51–200": 125.0, "51-200": 125.0, "More than 200": 300.0}
TOTAL_PARTNERS_MAP = {"Less than 50": 25.0, "50 – 499": 275.0, "50 - 499": 275.0, "500 – 999": 750.0, "500 - 999": 750.0, "1,000 – 4,999": 3000.0, "1,000 - 4,999": 3000.0, "5,000+": 6000.0}
ACTIVE_PARTNERS_MAP = {"Less than 10": 5.0, "10 – 99": 55.0, "10 - 99": 55.0, "100 – 499": 300.0, "100 - 499": 300.0, "500 – 999": 750.0, "500 - 999": 750.0, "1,000+": 1200.0, "Not currently monitored": np.nan}

def to_pct_numeric(x):
    if pd.isna(x): return np.nan
    s = str(x).strip().replace("%","")
    try: return float(s)
    except: return np.nan

def map_region_full(x: str) -> str:
    if pd.isna(x): return x
    s = str(x)
    if "North America" in s: return "North America"
    if "Latin America" in s: return "Latin America"
    if "Asia-Pacific" in s or "APAC" in s: return "Asia Pacific"
    if "Europe" in s or "EMEA" in s: return "Europe"
    return s

def mid_from_bins(label: str, mapping: dict) -> float | None:
    if pd.isna(label): return None
    val = mapping.get(str(label).strip())
    if val is None:
        alt_label = str(label).replace("–","-")
        val = mapping.get(alt_label.strip())
    return val

def _repair_replacement_chars(df: pd.DataFrame) -> pd.DataFrame:
    """Attempt to fix decoding replacement characters."""
    repl = "\ufffd"
    for c in df.select_dtypes(include=['object']).columns:
        try:
            series = df[c].astype(str)
            if not series.str.contains(repl).any():
                continue
            def fix_val(v):
                if not isinstance(v, str):
                    return v
                if repl not in v:
                    return v
                try:
                    b = v.encode('latin-1', errors='ignore')
                    s2 = b.decode('cp1252', errors='ignore')
                    if repl in s2:
                        return s2.replace(repl, '')
                    return s2
                except Exception:
                    return v.replace(repl, '')
            df[c] = df[c].apply(fix_val)
        except Exception:
            continue
    return df

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
    if col("region") in df_raw: d["region"] = df_raw[col("region")].map(map_region_full)
    if col("industry") in df_raw: d["industry"] = df_raw[col("industry")]
    if col("revenue_band") in df_raw: d["revenue_band"] = df_raw[col("revenue_band")]
    if col("employee_count_bin") in df_raw: d["employee_count_bin"] = df_raw[col("employee_count_bin")]
    if col("partner_team_size_bin") in df_raw: d["partner_team_size_bin"] = df_raw[col("partner_team_size_bin")]
    if col("total_partners_bin") in df_raw: d["total_partners_bin"] = df_raw[col("total_partners_bin")]
    if col("active_partners_bin") in df_raw: d["active_partners_bin"] = df_raw[col("active_partners_bin")]
    if col("expected_partner_revenue_pct") in df_raw:
        d["expected_partner_revenue_pct"] = df_raw[col("expected_partner_revenue_pct")].apply(to_pct_numeric)
    if col("deal_size_comparison") in df_raw: d["deal_size_comparison"] = df_raw[col("deal_size_comparison")]
    if col("win_rate") in df_raw: d["win_rate"] = df_raw[col("win_rate")].apply(to_pct_numeric)
    if col("cac_comparison") in df_raw: d["cac_comparison"] = df_raw[col("cac_comparison")]
    if col("sales_cycle_comparison") in df_raw: d["sales_cycle_comparison"] = df_raw[col("sales_cycle_comparison")]

    if "employee_count_bin" in d: d["employee_count_est"] = d["employee_count_bin"].apply(lambda x: mid_from_bins(x, EMPLOYEES_MAP))
    if "partner_team_size_bin" in d: d["partner_team_size_est"] = d["partner_team_size_bin"].apply(lambda x: mid_from_bins(x, TEAM_SIZE_MAP))
    if "total_partners_bin" in d: d["total_partners_est"] = d["total_partners_bin"].apply(lambda x: mid_from_bins(x, TOTAL_PARTNERS_MAP))
    if "active_partners_bin" in d: d["active_partners_est"] = d["active_partners_bin"].apply(lambda x: mid_from_bins(x, ACTIVE_PARTNERS_MAP))

    if {"active_partners_est","total_partners_est"}.issubset(d.columns):
        d["partners_active_ratio"] = d["active_partners_est"] / d["total_partners_est"]
    if {"expected_partner_revenue_pct","partner_team_size_est"}.issubset(d.columns):
        d["revenue_per_team_member"] = d["expected_partner_revenue_pct"] / d["partner_team_size_est"]

    return d, mapping, missing_readable

# ==================== SIMPLE UI COMPONENTS ====================
def create_metric_card(value, label, description=None, delta=None):
    """Create a metric card using native Streamlit layout."""
    n_match = re.search(r"\\(N=(\\d+)\\)", str(value))
    n_badge = int(n_match.group(1)) if n_match else None

    delta_html = ""
    if delta is not None:
        try:
            d_val = float(delta)
            bg = 'rgba(22,163,74,0.12)' if d_val > 0 else ('rgba(239,68,68,0.12)' if d_val < 0 else 'transparent')
            color = 'var(--success)' if d_val > 0 else ('var(--danger)' if d_val < 0 else 'var(--muted)')
            sign = '+' if d_val > 0 else ''
            delta_html = (
                f"<div title='Delta vs dataset median' style='background:{bg}; padding:4px 8px; "
                f"border-radius:8px; font-weight:700; color:{color}; font-size:0.85rem; margin-left:8px'>"
                f"{sign}{d_val:+.1%}</div>"
            )
        except Exception:
            delta_html = ''

    left_html = f"""
<div style='padding:8px 6px;'>
  <div style='display:flex; align-items:center; justify-content:space-between;'>
    <div style='font-size:0.85rem; color:var(--muted); font-weight:700'>{label}</div>
    {f"<div title='Sample size' aria-label='sample-size' style='background:var(--glass); padding:6px 10px; border-radius:999px; font-weight:700; color:var(--text); font-size:0.75rem;'>N={n_badge}</div>" if n_badge is not None else ''}
  </div>
  <div style='display:flex; align-items:center; gap:8px; margin-top:6px'>
    <div style='font-size:1.45rem; font-weight:700'>{value}</div>
    {delta_html}
  </div>
  {f"<div style='font-size:0.75rem; color:var(--muted); margin-top:6px'>{description}</div>" if description else ''}
</div>
"""

    with st.container():
        c1, c2 = st.columns([6, 1], gap='small')
        with c1:
            st.markdown(
                f"<div style='background:var(--panel); border-radius:8px; padding:6px; border:1px solid rgba(15,23,42,0.06);'>{left_html}</div>",
                unsafe_allow_html=True,
            )
        with c2:
            chart_key = f"spark_{label}"
            if chart_key in st.session_state:
                try:
                    st.altair_chart(
                        st.session_state[chart_key].properties(width=110, height=48),
                        use_container_width=False,
                    )
                except Exception:
                    pass

def create_section_header(title):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)

def create_data_health_panel(df: pd.DataFrame, mapping: dict, missing_readable: list):
    with st.expander("Data Health & Column Mapping", expanded=False):
        st.markdown("**Dataset summary**")
        st.write(f"Rows: {len(df):,}")
        st.write(f"Columns: {df.shape[1]}")

        if missing_readable:
            st.warning("Missing expected columns: \n- " + "\n- ".join(missing_readable))
        else:
            st.success("All expected columns detected (or no required columns were missing).")

        if not df.empty:
            na_counts = df.isna().sum()
            na_pct = (na_counts / max(1, len(df))) * 100
            na_table = pd.DataFrame({"missing_count": na_counts, "missing_pct": na_pct}).sort_values("missing_pct", ascending=False)
            st.markdown("**Top missing rates**")
            st.dataframe(na_table.head(20).style.format({"missing_pct": "{:.1f}%"}), use_container_width=True)

        st.markdown("**Detected header mapping (automatic)**")
        if mapping:
            map_items = [(k, v if v is not None else "(not found)") for k, v in mapping.items()]
            map_df = pd.DataFrame(map_items, columns=["logical_field", "detected_column"]) 
            st.dataframe(map_df, use_container_width=True)
            try:
                json_str = json.dumps(mapping, default=str, indent=2)
                st.download_button("Export mapping JSON", json_str, file_name="sopl_mapping.json", mime="application/json")
            except Exception:
                pass

        st.markdown("**Sample rows**")
        try:
            st.dataframe(df.head(5), use_container_width=True)
        except Exception:
            st.write(df.head(5).to_html(), unsafe_allow_html=True)

# ==================== MAIN APP ====================
def main():
    # Theme selector (default to Light)
    theme = st.sidebar.radio("Theme", options=["Dark", "Light"], index=1, help="Switch UI theme")
    try:
        if theme == "Light":
            alt.themes.enable("light_simple")
        else:
            alt.themes.enable("simple")
    except Exception:
        pass

    # Bot toggle moved to sidebar (global)
    show_bot = st.sidebar.checkbox(
        "Show Assistant Bot (Pickaxe)",
        value=st.session_state.get('show_bot', False),
        help="Toggle the embedded assistant"
    )
    st.session_state['show_bot'] = bool(show_bot)

    theme_class = "theme-light" if theme == "Light" else ""
    st.markdown(f'<div class="app-wrapper {theme_class}">', unsafe_allow_html=True)

    # Header
    st.markdown(
        '<div class="header-row"><div>'
        '<div class="main-header">SOPL 2025 Insights Platform</div>'
        '<div class="sub-header">partnership analytics and strategic insights - SOPL</div>'
        '</div></div>',
        unsafe_allow_html=True
    )

    # Data Upload (optional – app will use bundled data if nothing uploaded)
    with st.expander("Upload Data (optional)", expanded=False):
        uploaded = st.file_uploader("Upload SOPL Data", type=["csv","xlsx","xls"], label_visibility="collapsed")
        encoding_choice = st.selectbox(
            "Encoding (auto attempts common encodings)",
            options=["auto","cp1252","utf-8","utf-8-sig","latin-1"],
            index=0
        )
        st.caption("If you don't upload anything, the dashboard uses the built-in SOPL dataset packaged with the app.")

    # Load Data
    with st.spinner("Loading data..."):
        raw = load_raw(
            uploaded,
            encoding_override=st.session_state.get('encoding_override', None) or
                             (encoding_choice if 'encoding_choice' in locals() else None)
        )
    
    if raw.empty:
        st.error("No data available. Upload a SOPL data file or ensure the local fallback CSV exists.")
        return

    # Process Data
    df, mapping, missing = standardize(raw)
    if df.empty:
        st.error("Unable to process the uploaded file.")
        return

    # Overall medians (unfiltered) for deltas
    overall_medians = {}
    for colname in ["expected_partner_revenue_pct", "partners_active_ratio", "win_rate"]:
        if colname in df.columns and not df[colname].isna().all():
            try:
                overall_medians[colname] = float(df[colname].dropna().median())
            except Exception:
                overall_medians[colname] = None

    # Data health panel
    create_data_health_panel(df, mapping, missing)

    # Detect time-like column
    time_col = None
    try:
        candidates = []
        for c in raw.columns:
            try:
                parsed = pd.to_datetime(raw[c], errors='coerce')
                non_null = int(parsed.notna().sum())
                unique_dates = int(parsed.dt.date.nunique()) if non_null > 0 else 0
                if non_null >= 5 and unique_dates >= 2:
                    candidates.append((c, non_null))
            except Exception:
                continue
        if candidates:
            time_col = sorted(candidates, key=lambda x: x[1], reverse=True)[0][0]
            st.sidebar.caption(f"Detected time column: {time_col}")
    except Exception:
        time_col = None

    if 'trend_period' not in st.session_state:
        st.session_state['trend_period'] = 'M'

    # Data health status pill (unfiltered)
    if missing:
        health_status = "ERROR - missing expected columns"
        status_color = "#ef4444"
    elif len(df) < 30:
        health_status = "WARNING - small sample size"
        status_color = "#f59e0b"
    else:
        health_status = "OK"
        status_color = "#16a34a"

    st.markdown(
        f"<div style='padding:6px; display:inline-block; border-radius:6px; "
        f"background:{status_color}; color:#f9fafb; font-weight:700;'>{health_status}</div>",
        unsafe_allow_html=True
    )

    # ==================== GLOBAL FILTERS ====================
    with st.sidebar:
        st.subheader("Filters")

        industries = None
        regions = None
        revenues = None
        employees = None

        if 'industry' in df.columns:
            industry_options = sorted(df['industry'].dropna().unique())
            industries = st.multiselect("Industry", options=industry_options, default=industry_options)

        if 'region' in df.columns:
            region_options = sorted(df['region'].dropna().unique())
            regions = st.multiselect("Region", options=region_options, default=region_options)

        if 'revenue_band' in df.columns:
            rev_options = sorted(df['revenue_band'].dropna().unique())
            revenues = st.multiselect("Revenue Band", options=rev_options, default=rev_options)

        if 'employee_count_bin' in df.columns:
            emp_options = sorted(df['employee_count_bin'].dropna().unique())
            employees = st.multiselect("Employee Count", options=emp_options, default=emp_options)

    # Apply filters to create flt and mask
    flt_mask = pd.Series(True, index=df.index)

    if 'industry' in df.columns and industries:
        flt_mask &= df['industry'].isin(industries)
    if 'region' in df.columns and regions:
        flt_mask &= df['region'].isin(regions)
    if 'revenue_band' in df.columns and revenues:
        flt_mask &= df['revenue_band'].isin(revenues)
    if 'employee_count_bin' in df.columns and employees:
        flt_mask &= df['employee_count_bin'].isin(employees)

    flt = df[flt_mask].copy()

    # Summary stats (filtered)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Replaced "Total Companies" with something more meaningful
        if "partner_team_size_est" in flt.columns and not flt["partner_team_size_est"].isna().all():
            median_team = flt["partner_team_size_est"].median()
            st.metric("Median Partnerships Team Size", f"{median_team:,.0f}")
        elif "employee_count_est" in flt.columns and not flt["employee_count_est"].isna().all():
            median_emp = flt["employee_count_est"].median()
            st.metric("Median Employee Count (est.)", f"{median_emp:,.0f}")
        else:
            st.metric("Filtered Companies (N)", f"{len(flt):,}")

    with col2:
        industries_count = flt['industry'].nunique() if 'industry' in flt.columns else 0
        st.metric("Industries", f"{industries_count}")

    with col3:
        regions_count = flt['region'].nunique() if 'region' in flt.columns else 0
        st.metric("Regions", f"{regions_count}")

    with col4:
        if 'expected_partner_revenue_pct' in flt.columns and not flt['expected_partner_revenue_pct'].isna().all():
            avg_revenue = flt['expected_partner_revenue_pct'].median()
            st.metric("Median Expected Partner Revenue", f"{avg_revenue:.1f}%")

    # Sparkline helper (respects filters)
    def build_and_store_sparkline(col_name, label, period='M'):
        if not time_col or col_name not in flt.columns:
            return
        try:
            ts_raw = pd.to_datetime(raw[time_col], errors='coerce')
            ts_filtered = ts_raw[flt_mask]
            series_df = pd.DataFrame({'_time': ts_filtered, 'val': flt[col_name]})
            series_df = series_df.dropna(subset=['_time','val'])
            if series_df.empty:
                return
            if period == 'W':
                series_df['_period'] = series_df['_time'].dt.to_period('W').dt.start_time
            elif period == 'Q':
                series_df['_period'] = series_df['_time'].dt.to_period('Q').dt.start_time
            else:
                series_df['_period'] = series_df['_time'].dt.to_period('M').dt.to_timestamp()
            agg = series_df.groupby('_period').val.median().reset_index()
            chart = alt.Chart(agg).mark_line(color='#3b308f').encode(
                x=alt.X('_period:T', title=None),
                y=alt.Y('val:Q', title=None)
            ).properties(height=48)
            st.session_state[f"spark_{label}"] = chart
        except Exception:
            return

    st.markdown("---")

    # ==================== MAIN TABS ====================
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Performance", "Geography", "Data", "Trends"])

    with tab1:
        create_section_header("Partnership Performance Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if "expected_partner_revenue_pct" in flt.columns and not flt["expected_partner_revenue_pct"].isna().all():
                series = flt["expected_partner_revenue_pct"].dropna()
                median_val = series.median()
                n_rev = int(series.count())
                build_and_store_sparkline('expected_partner_revenue_pct', 'Expected Partner Revenue', period=st.session_state.get('trend_period','M'))
                delta_rev = None
                if overall_medians.get('expected_partner_revenue_pct') is not None:
                    delta_rev = (median_val/100.0) - (overall_medians.get('expected_partner_revenue_pct')/100.0)
                create_metric_card(f"{median_val:.1f}% (N={n_rev})", "Expected Partner Revenue", "Median expected revenue from partnerships", delta=delta_rev)

        with col2:
            if "partners_active_ratio" in flt.columns and not flt["partners_active_ratio"].isna().all():
                series_act = flt["partners_active_ratio"].dropna()
                activation_median = series_act.median()
                n_act = int(series_act.count())
                build_and_store_sparkline('partners_active_ratio', 'Partner Activation', period=st.session_state.get('trend_period','M'))
                delta_act = None
                if overall_medians.get('partners_active_ratio') is not None:
                    delta_act = activation_median - overall_medians.get('partners_active_ratio')
                create_metric_card(f"{activation_median:.1%} (N={n_act})", "Partner Activation", "Active vs total partners", delta=delta_act)

        with col3:
            if "deal_size_comparison" in flt.columns:
                higher_deals = (flt["deal_size_comparison"] == "Higher than direct deals").sum()
                total_deals = flt["deal_size_comparison"].notna().sum()
                if total_deals > 0:
                    premium_pct = (higher_deals / total_deals) * 100
                    build_and_store_sparkline('deal_size_comparison', 'Deal Size Premium', period=st.session_state.get('trend_period','M'))
                    create_metric_card(f"{premium_pct:.1f}% (N={total_deals})", "Deal Size Premium", "Partners drive larger deals")

        with col4:
            if "win_rate" in flt.columns and not flt["win_rate"].isna().all():
                series_win = flt["win_rate"].dropna()
                win_median = series_win.median()
                n_win = int(series_win.count())
                build_and_store_sparkline('win_rate', 'Win Rate', period=st.session_state.get('trend_period','M'))
                delta_win = None
                if overall_medians.get('win_rate') is not None:
                    delta_win = (win_median/100.0) - (overall_medians.get('win_rate')/100.0)
                create_metric_card(f"{win_median:.1f}% (N={n_win})", "Win Rate", "Deals with partner involvement", delta=delta_win)

        # Revenue by Industry
        create_section_header("Revenue: median expected partner revenue by industry")
        if {"industry","expected_partner_revenue_pct"}.issubset(flt.columns):
            d = flt[["industry","expected_partner_revenue_pct"]].dropna()
            if not d.empty:
                agg = d.groupby("industry").agg(
                    median_pct=("expected_partner_revenue_pct","median"),
                    count=("expected_partner_revenue_pct","count")
                ).reset_index()
                top = agg.sort_values("count", ascending=False).head(8)
                top = top.sort_values("median_pct", ascending=True)

                chart = alt.Chart(top).mark_bar().encode(
                    x=alt.X("median_pct:Q", title="Median Expected Partner Revenue (%)", axis=alt.Axis(format=".1f")),
                    y=alt.Y("industry:N", sort=alt.SortField(field="median_pct", order="ascending")),
                    color=alt.Color("median_pct:Q", scale=alt.Scale(scheme='blues'), legend=None),
                    tooltip=[
                        alt.Tooltip("industry:N", title="Industry"),
                        alt.Tooltip("median_pct:Q", title="Median (%)", format=".1f"),
                        alt.Tooltip("count:Q", title="N")
                    ]
                ).properties(height=360)

                labels = alt.Chart(top).mark_text(align='left', dx=4, color='#020617').encode(
                    x=alt.X('median_pct:Q'),
                    y=alt.Y('industry:N'),
                    text=alt.Text('count:Q')
                )

                st.altair_chart((chart + labels).configure_view(stroke=None), use_container_width=True)
                if (top['count'] < 10).any():
                    st.warning("Some industries have small sample sizes (N < 10). Interpret medians with caution.")

        # Partner Activation by Industry
        create_section_header("Partner Activation (median) by Industry")
        if "partners_active_ratio" in flt.columns:
            d2 = flt[["industry","partners_active_ratio"]].dropna()
            if not d2.empty:
                invalid_count = (d2["partners_active_ratio"] > 1).sum()
                if invalid_count:
                    st.warning(f"{invalid_count} rows have activation > 100% (active > total) and were excluded from aggregation.")
                d2 = d2[d2["partners_active_ratio"] <= 1]

                agg2 = d2.groupby("industry").partners_active_ratio.agg([
                    ('median_activation','median'),
                    ('q1', lambda s: s.quantile(0.25)),
                    ('q3', lambda s: s.quantile(0.75)),
                    ('count','count')
                ]).reset_index()
                top2 = agg2.sort_values("count", ascending=False).head(8).sort_values("median_activation", ascending=True)

                base = alt.Chart(top2).encode(
                    y=alt.Y('industry:N', sort=alt.SortField(field='median_activation', order='ascending'))
                )

                bars = base.mark_bar().encode(
                    x=alt.X('median_activation:Q', title='Median Partner Activation (ratio)', axis=alt.Axis(format='.0%')),
                    color=alt.condition(alt.datum['count'] < 10, alt.value('#9ca3af'), alt.value('#3b308f')),
                    tooltip=[
                        alt.Tooltip('industry:N', title='Industry'),
                        alt.Tooltip('median_activation:Q', title='Median', format='.1%'),
                        alt.Tooltip('count:Q', title='N')
                    ]
                ).properties(height=320)

                rules = base.mark_rule(color='#020617').encode(
                    x='q1:Q', x2='q3:Q'
                )

                labels2 = alt.Chart(top2).mark_text(align='left', dx=4, color='#020617').encode(
                    x=alt.X('median_activation:Q'),
                    y=alt.Y('industry:N'),
                    text=alt.Text('count:Q')
                )

                st.altair_chart((bars + rules + labels2).configure_view(stroke=None), use_container_width=True)
                if (top2['count'] < 10).any():
                    st.warning('Some industries have small sample sizes (N < 10). Interpret activation rates with caution.')
                st.info('Note: activation ratios are estimated from binned responses (midpoint estimates).')

    with tab2:
        create_section_header("Performance Benchmarks")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "deal_size_comparison" in flt.columns:
                create_section_header("Deal Size: Partners vs Direct")
                deal_counts = flt["deal_size_comparison"].value_counts()
                if not deal_counts.empty:
                    deal_data = pd.DataFrame({
                        'Comparison': deal_counts.index,
                        'Count': deal_counts.values
                    })
                    
                    chart = alt.Chart(deal_data).mark_bar().encode(
                        x=alt.X('Count:Q', title='Number of Companies'),
                        y=alt.Y('Comparison:N', title='', sort='-x'),
                        color=alt.Color('Comparison:N', legend=None)
                    ).properties(height=300)
                    
                    st.altair_chart(chart, use_container_width=True)
            
        with col2:
            if "cac_comparison" in flt.columns:
                create_section_header("Customer Acquisition Cost")
                cac_counts = flt["cac_comparison"].value_counts()
                if not cac_counts.empty:
                    cac_data = pd.DataFrame({
                        'Comparison': cac_counts.index,
                        'Count': cac_counts.values
                    })
                    
                    chart = alt.Chart(cac_data).mark_bar().encode(
                        x=alt.X('Count:Q', title='Number of Companies'),
                        y=alt.Y('Comparison:N', title='', sort='-x'),
                        color=alt.Color('Comparison:N', legend=None)
                    ).properties(height=300)
                    
                    st.altair_chart(chart, use_container_width=True)

        if "win_rate" in flt.columns and not flt["win_rate"].isna().all():
            create_section_header("Win Rate Distribution")
            d = flt[["win_rate"]].dropna()
            chart = alt.Chart(d).mark_bar(color="#3b308f").encode(
                x=alt.X("win_rate:Q", bin=alt.Bin(maxbins=20), title="Win Rate (%)"),
                y=alt.Y("count():Q", title="Number of Companies")
            ).properties(height=300)
            
            st.altair_chart(chart, use_container_width=True)

    with tab3:
        create_section_header("Geographic Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "region" in flt.columns:
                create_section_header("Companies by Region")
                region_counts = flt["region"].value_counts()
                region_data = pd.DataFrame({
                    'Region': region_counts.index,
                    'Count': region_counts.values
                })
                
                chart = alt.Chart(region_data).mark_bar().encode(
                    x=alt.X('Count:Q', title='Number of Companies'),
                    y=alt.Y('Region:N', title='', sort='-x'),
                    color=alt.Color('Region:N', legend=None)
                ).properties(height=300)
                
                st.altair_chart(chart, use_container_width=True)
        
        with col2:
            if "region" in flt.columns and "expected_partner_revenue_pct" in flt.columns:
                create_section_header("Revenue by Region")
                d = flt[["region","expected_partner_revenue_pct"]].dropna()
                if not d.empty:
                    region_revenue = d.groupby("region")["expected_partner_revenue_pct"].median().reset_index()
                    
                    chart = alt.Chart(region_revenue).mark_bar().encode(
                        x=alt.X('expected_partner_revenue_pct:Q', title='Median Expected Revenue (%)'),
                        y=alt.Y('region:N', title='', sort='-x'),
                        color=alt.Color('region:N', legend=None)
                    ).properties(height=300)
                    
                    st.altair_chart(chart, use_container_width=True)

        if "region" in flt.columns:
            create_section_header("Global Distribution")
            
            region_coords = {
                "North America": [40.0, -100.0],
                "Europe": [50.0, 10.0],
                "Asia Pacific": [30.0, 100.0],
                "Latin America": [-20.0, -60.0]
            }
            
            map_data = []
            region_counts = flt["region"].value_counts()
            
            for region, count in region_counts.items():
                if region in region_coords:
                    map_data.append({
                        "region": region,
                        "count": count,
                        "lat": region_coords[region][0],
                        "lon": region_coords[region][1]
                    })
            
            if map_data:
                df_map = pd.DataFrame(map_data)
                
                layer = pdk.Layer(
                    "ScatterplotLayer",
                    df_map,
                    get_position=["lon", "lat"],
                    get_color=[59, 48, 143, 160],  # Atlas blue
                    get_radius="count * 50000",
                    pickable=True,
                )
                
                view_state = pdk.ViewState(
                    latitude=20,
                    longitude=0,
                    zoom=1,
                    pitch=0,
                )
                
                st.pydeck_chart(pdk.Deck(
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={"text": "{region}\\nCount: {count}"}
                ))

    with tab5:
        create_section_header("Trends")
        if time_col is None:
            st.info("No time-like column detected in the uploaded file. Include a timestamp column to enable trend charts.")
        else:
            st.markdown(f"**Using time column:** {time_col}")
            ts = pd.to_datetime(raw[time_col], errors='coerce')
            ser_time = ts[flt_mask]  # respect filters

            period_label = st.selectbox(
                "Period granularity",
                options=["Monthly","Weekly","Quarterly"],
                index={"M":0,"W":1,"Q":2}.get(st.session_state.get('trend_period','M'),0)
            )
            mapping_period = {"Monthly":"M","Weekly":"W","Quarterly":"Q"}
            st.session_state['trend_period'] = mapping_period.get(period_label, 'M')

            def period_median(col, period='M'):
                s = pd.DataFrame({'_time': ser_time, 'val': flt[col]})
                s = s.dropna(subset=['_time','val'])
                if s.empty:
                    return pd.DataFrame()
                if period == 'W':
                    s['_period'] = s['_time'].dt.to_period('W').dt.start_time
                elif period == 'Q':
                    s['_period'] = s['_time'].dt.to_period('Q').dt.start_time
                else:
                    s['_period'] = s['_time'].dt.to_period('M').dt.to_timestamp()
                out = s.groupby('_period').val.median().reset_index()
                return out

            cols_to_plot = []
            if 'expected_partner_revenue_pct' in flt.columns:
                cols_to_plot.append(('expected_partner_revenue_pct','Median Expected Partner Revenue (%)'))
            if 'partners_active_ratio' in flt.columns:
                cols_to_plot.append(('partners_active_ratio','Median Partner Activation (ratio)'))
            if 'win_rate' in flt.columns:
                cols_to_plot.append(('win_rate','Median Win Rate (%)'))

            for cname, title in cols_to_plot:
                mts = period_median(cname, period=st.session_state.get('trend_period','M'))
                if mts.empty:
                    st.markdown(f"No time series data for {title}")
                    continue
                chart = alt.Chart(mts).mark_line(point=True, color="#3b308f").encode(
                    x=alt.X('_period:T', title='Period'),
                    y=alt.Y(
                        'val:Q',
                        title=title,
                        axis=alt.Axis(format='.0%') if 'ratio' in cname or 'win' in cname.lower() else None
                    ),
                    tooltip=[
                        alt.Tooltip('_period:T', title='Period'),
                        alt.Tooltip('val:Q', title=title, format='.2f')
                    ]
                ).properties(height=240)
                st.altair_chart(chart, use_container_width=True)

    with tab4:
        create_section_header("Data Explorer")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            show_columns = st.multiselect(
                "Select Columns", 
                options=flt.columns.tolist(), 
                default=flt.columns.tolist()[:6]
            )
        
        with col2:
            rows_to_show = st.slider("Rows to display", 10, 100, 20)
        
        st.dataframe(flt[show_columns].head(rows_to_show), use_container_width=True)
        
        csv = flt[show_columns].to_csv(index=False)
        st.download_button(
            "Export Data as CSV",
            csv,
            "sopl_2025_data.csv",
            "text/csv"
        )

    # ==================== MAIN PAGE BOT (BIG) ====================
    if st.session_state.get('show_bot', False):
        st.markdown("---")
        st.markdown("### Assistant (Pickaxe)")

        pickaxe_html = """
<div id="deployment-5870ff7d-8fcf-4395-976b-9e9fdefbb0ff" style="width:100%; max-width:1200px; margin:0 auto;"></div>
<script src="https://studio.pickaxe.co/api/embed/bundle.js" defer></script>
"""
        # Big embed on main page, but constrained to fit nicely
        components.html(pickaxe_html, height=650, scrolling=True)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #94a3b8; font-size: 0.9rem; padding: 1rem;'>"
        "SOPL 2025 Insights Platform • partnership analytics and strategic insights"
        "</div>", 
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
