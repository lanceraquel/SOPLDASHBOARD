# app.py — SOPL 2024 Dashboard with robust header auto-mapping

import os, io, re, unicodedata
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from difflib import SequenceMatcher

st.set_page_config(page_title="SOPL 2024 – Interactive", page_icon="📊", layout="wide")

HOUSE_COLORS = ["#2663EB", "#24A19C", "#F29F05", "#C4373D", "#7B61FF", "#2A9D8F", "#D97706"]
def house_theme():
    return {
        "config": {
            "range": {"category": HOUSE_COLORS, "heatmap": {"scheme": "blueorange"}},
            "axis": {"labelColor": "#E5E7EB", "titleColor": "#F3F4F6", "gridColor": "#2F343B"},
            "legend": {"labelColor": "#E5E7EB", "titleColor": "#F3F4F6"},
            "title": {"color": "#F3F4F6", "fontSize": 14, "anchor": "start"},
            "background": None,
        }
    }
alt.themes.register("house", house_theme)
alt.themes.enable("house")

LOCAL_FALLBACK = "data/SOPL 1002 Results - Raw.csv"

# -------------------- Normalization & fuzzy header mapping --------------------
def normalize(txt: str) -> str:
    if txt is None: return ""
    # unify unicode (curly quotes, en dashes, accents), lower, keep letters/numbers/spaces
    t = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode("ascii")
    t = t.replace("’", "'").replace("–", "-").replace("—", "-")
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def best_match(candidates, cols_norm, cols_raw):
    """
    candidates: list[str] (phrases we expect)
    cols_norm: dict {normalized_col -> raw_col}
    cols_raw: list of original raw col names
    Returns raw column name or None
    """
    # 1) exact normalized match on any candidate
    for cand in candidates:
        nc = normalize(cand)
        if nc in cols_norm:
            return cols_norm[nc]

    # 2) token containment heuristic
    cand_tokens = [set(normalize(c).split()) for c in candidates]
    best = (0.0, None)
    for raw in cols_raw:
        nr = normalize(raw)
        for toks in cand_tokens:
            if not toks: continue
            overlap = len(toks & set(nr.split())) / max(1, len(toks))
            if overlap > best[0]:
                best = (overlap, raw)

    # 3) difflib similarity as fallback
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
    # 1) Uploaded file?
    if uploaded is not None:
        name = (uploaded.name or "").lower()
        # Excel
        if name.endswith((".xlsx", ".xls")):
            try: return pd.read_excel(uploaded)
            except Exception as e: st.warning(f"Excel read failed: {e}")
        # CSV robust
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
    # 2) Repo fallback
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
# Each key lists several acceptable phrasings so we can match variations.
SYN = {
    "company_name": [
        "Company name", "Company", "Your company name"
    ],
    "region": [
        "Please select the region where your company is headquartered.",
        "Region", "Company region", "HQ region"
    ],
    "industry": [
        "What industry sector does your company operate in?",
        "Industry", "Industry sector", "Company industry"
    ],
    "revenue_band": [
        "What is your company’s estimated annual revenue?",
        "What is your company's estimated annual revenue?",
        "Estimated annual revenue", "Annual revenue band", "Revenue band"
    ],
    "employee_count_bin": [
        "What is your company’s total number of employees?",
        "What is your company's total number of employees?",
        "Total number of employees", "Employee count", "Company size"
    ],
    "partner_team_size_bin": [
        "How many people are on your Partnerships team?",
        "Partnerships team size", "Partner team size"
    ],
    "total_partners_bin": [
        "How many total partners do you have?", "Total partners"
    ],
    "active_partners_bin": [
        "How many active partners generated revenue in the last 12 months?",
        "Active partners generated revenue in last 12 months", "Active partners"
    ],
    "time_to_first_revenue_bin": [
        "How long does it typically take for a partnership to generate revenue after the first meeting?",
        "Time to first partner revenue", "Time to first revenue"
    ],
    "program_years_bin": [
        "How long has your company had a partnership program?",
        "Program tenure", "Years running partner program"
    ],
    "expected_partner_revenue_pct": [
        "On average, what percentage of your company’s revenue is expected to come from partnerships in the next 12 months?",
        "On average, what percentage of your company's revenue is expected to come from partnerships in the next 12 months?",
        "Expected revenue from partnerships (next 12 months)",
        "Expected partner revenue percent", "Expected partner revenue %"
    ],
    "marketplace_revenue_pct": [
        "What percentage of your total revenue comes through cloud marketplaces?",
        "Revenue through cloud marketplaces", "Cloud marketplace revenue %"
    ],
    "top_challenge": [
        "What's your biggest challenge in scaling your partner program?",
        "What is your biggest challenge in scaling your partner program?",
        "Biggest challenge", "Top challenge"
    ],
}

# -------------------- Numeric mappings for bins --------------------
EMPLOYEES_MAP = {
    "Less than 100 employees": 50.0,
    "100 – 500 employees": 300.0,
    "100 - 500 employees": 300.0,
    "501 – 5,000 employees": 2500.0,
    "501 - 5,000 employees": 2500.0,
    "More than 5,000 employees": 8000.0,
}
TEAM_SIZE_MAP = {"Less than 10": 5.0, "10–50": 30.0, "10-50": 30.0, "51–200": 125.0, "51-200": 125.0, "More than 200": 300.0}
TOTAL_PARTNERS_MAP = {
    "Less than 50": 25.0, "50 – 499": 275.0, "50 - 499": 275.0,
    "500 – 999": 750.0, "500 - 999": 750.0,
    "1,000 – 4,999": 3000.0, "1,000 - 4,999": 3000.0, "5,000+": 6000.0
}
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
    # try exact first, then normalize dashes
    val = mapping.get(str(label).strip())
    if val is None:
        alt_label = str(label).replace("–","-")
        val = mapping.get(alt_label.strip())
    return val

def median_iqr(s, fmt="{:.1f}"):
    x = pd.to_numeric(s, errors="coerce").dropna()
    if x.empty: return ("—","—","0")
    med = np.median(x); q1, q3 = np.percentile(x, [25, 75])
    return (fmt.format(med), f"[{fmt.format(q1)}–{fmt.format(q3)}]", f"{len(x)}")

def render_chart(chart: alt.Chart, name: str, height=None):
    if height is not None: chart = chart.properties(height=height)
    st.altair_chart(chart, use_container_width=True)
    try:
        import vl_convert as vlc
        png = vlc.vegalite_to_png(chart.to_dict(), scale=2)
        st.download_button(f"Download {name}.png", png, file_name=f"{name}.png", mime="image/png")
    except Exception:
        pass

# -------------------- Standardize using auto-mapped headers --------------------
def resolve_headers(df_raw: pd.DataFrame) -> dict:
    """Return dict of {logical_key -> raw_column_name} using fuzzy/normalized match."""
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
    # Build user-friendly missing message based on the *variants* we expect
    missing_readable = []
    for k in missing_keys:
        # show the first canonical variant to help the user see what's intended
        missing_readable.append(SYN[k][0])

    if missing_readable:
        st.error("Missing expected columns in CSV:\n- " + "\n- ".join(missing_readable))

    # proceed with whatever we have (non-missing) so the app still runs
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

    # numeric estimates for binned questions
    if "employee_count_bin" in d: d["employee_count_est"] = d["employee_count_bin"].apply(lambda x: mid_from_bins(x, EMPLOYEES_MAP))
    if "partner_team_size_bin" in d: d["partner_team_size_est"] = d["partner_team_size_bin"].apply(lambda x: mid_from_bins(x, TEAM_SIZE_MAP))
    if "total_partners_bin" in d: d["total_partners_est"] = d["total_partners_bin"].apply(lambda x: mid_from_bins(x, TOTAL_PARTNERS_MAP))
    if "active_partners_bin" in d: d["active_partners_est"] = d["active_partners_bin"].apply(lambda x: mid_from_bins(x, ACTIVE_PARTNERS_MAP))
    if "time_to_first_revenue_bin" in d: d["time_to_first_revenue_years"] = d["time_to_first_revenue_bin"].apply(lambda x: mid_from_bins(x, TTF_REVENUE_MAP))
    if "program_years_bin" in d: d["program_maturity"] = d["program_years_bin"].apply(maturity_from_years)

    # derived
    if {"active_partners_est","total_partners_est"}.issubset(d.columns):
        d["partners_active_ratio"] = d["active_partners_est"] / d["total_partners_est"]
    if {"expected_partner_revenue_pct","partner_team_size_est"}.issubset(d.columns):
        d["expected_partner_revenue_per_partner"] = d["expected_partner_revenue_pct"] / d["partner_team_size_est"]

    return d, mapping, missing_readable

# -------------------- MAIN --------------------
with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload SOPL raw CSV or Excel", type=["csv","xlsx","xls"])

raw = load_raw(uploaded)
if raw.empty:
    st.info("No data loaded. Upload a CSV/XLSX or commit a fallback at:\n"
            f"**{LOCAL_FALLBACK}**")
    st.stop()

df, mapping, missing = standardize(raw)
if df.empty:
    st.stop()

# Show mapping so you can verify what matched (and what didn’t)
with st.sidebar.expander("Show detected header mapping"):
    mdf = pd.DataFrame({
        "Logical Field": list(mapping.keys()),
        "Matched Column": [mapping[k] for k in mapping.keys()]
    })
    st.dataframe(mdf, use_container_width=True)

# -------------------- Filters --------------------
with st.sidebar:
    st.header("Filters")
    def opts(col):
        return sorted(df[col].dropna().astype(str).unique().tolist()) if col in df else []

    rev_sel = st.multiselect("Revenue Band", options=opts("revenue_band"), default=opts("revenue_band"))
    ind_sel = st.multiselect("Industry", options=opts("industry"), default=opts("industry"))
    reg_order = ["APAC","EMEA","LATAM","NA"]
    reg_all = opts("region")
    reg_sorted = [r for r in reg_order if r in reg_all] + [r for r in reg_all if r not in reg_order]
    reg_sel = st.multiselect("Region", options=reg_sorted, default=reg_sorted)
    mat_order = ["Early","Developing","Mature","Unknown"]
    mat_all = opts("program_maturity")
    mat_sorted = [m for m in mat_order if m in mat_all]
    mat_sel = st.multiselect("Program Maturity", options=mat_sorted, default=mat_sorted)
    emp_sel = st.multiselect("Employee Count (bin)", options=opts("employee_count_bin"), default=opts("employee_count_bin"))
    team_sel = st.multiselect("Partner Team Size (bin)", options=opts("partner_team_size_bin"), default=opts("partner_team_size_bin"))

flt = df.copy()
if "revenue_band" in flt and rev_sel: flt = flt[flt["revenue_band"].isin(rev_sel)]
if "industry" in flt and ind_sel: flt = flt[flt["industry"].isin(ind_sel)]
if "region" in flt and reg_sel: flt = flt[flt["region"].isin(reg_sel)]
if "program_maturity" in flt and mat_sel: flt = flt[flt["program_maturity"].isin(mat_sel)]
if "employee_count_bin" in flt and emp_sel: flt = flt[flt["employee_count_bin"].isin(emp_sel)]
if "partner_team_size_bin" in flt and team_sel: flt = flt[flt["partner_team_size_bin"].isin(team_sel)]

# -------------------- KPIs --------------------
st.title("SOPL 2024 – Interactive Dashboard (Auto-mapped headers)")

def kpi(series, title, fmt="{:.1f}"):
    x = pd.to_numeric(series, errors="coerce") if series is not None else pd.Series(dtype=float)
    if x.dropna().empty:
        st.metric(title, "—", "—"); return
    m = np.median(x.dropna()); q1, q3 = np.percentile(x.dropna(), [25, 75]); n = x.dropna().shape[0]
    st.metric(title, fmt.format(m), f"[{fmt.format(q1)}–{fmt.format(q3)}] | N={n}")

col1, col2, col3, col4 = st.columns(4)
kpi(flt.get("expected_partner_revenue_pct"), "Expected partner revenue (%)")
kpi(flt.get("marketplace_revenue_pct"), "Marketplace revenue (%)")
kpi(flt.get("partner_team_size_est"), "Partner team size (est)", "{:.0f}")
kpi(flt.get("time_to_first_revenue_years"), "Time to first revenue (yrs)")

col5, col6, col7, col8 = st.columns(4)
kpi(flt.get("total_partners_est"), "Total partners (est)", "{:.0f}")
kpi(flt.get("active_partners_est"), "Active partners (est)", "{:.0f}")
kpi(flt.get("partners_active_ratio"), "Activation ratio (active/total)", "{:.2f}")
if {"partner_team_size_est","employee_count_est"}.issubset(flt.columns):
    tpe = (flt["partner_team_size_est"] / (flt["employee_count_est"] / 1000)).replace([np.inf,-np.inf], np.nan)
    kpi(tpe, "Team per 1k employees", "{:.2f}")
else:
    st.metric("Team per 1k employees", "—", "—")

g1, g2 = st.columns(2)
g1.metric("Responses (after filters)", f"{len(flt):,}")
g2.metric("Total responses", f"{len(df):,}")

st.divider()

# -------------------- Expected partner revenue --------------------
if {"expected_partner_revenue_pct","program_maturity"}.issubset(flt.columns):
    st.subheader("Expected Partner Revenue — Distributions & Cohorts")
    for cohort_col, title in [("program_maturity", "by Program Maturity"), ("revenue_band", "by Revenue Band")]:
        if cohort_col not in flt or "expected_partner_revenue_pct" not in flt: continue
        d = flt[[cohort_col, "expected_partner_revenue_pct"]].dropna()
        if d.empty: continue
        base = alt.Chart(d).transform_density(
            "expected_partner_revenue_pct", groupby=[cohort_col], as_=["value","density"]
        )
        chart = base.mark_area(opacity=0.45).encode(
            x=alt.X("value:Q", title="Expected partner revenue (%)"),
            y=alt.Y("density:Q", title="Density"),
            color=alt.Color(f"{cohort_col}:N", title=cohort_col.replace("_"," ").title()),
            tooltip=[cohort_col, alt.Tooltip("value:Q", format=".1f"), alt.Tooltip("density:Q", format=".3f")]
        ).properties(title=f"Distribution {title}", height=260)
        render_chart(chart, f"exp_rev_{cohort_col}_density")

    if {"region","expected_partner_revenue_pct"}.issubset(flt.columns):
        d = flt[["region","expected_partner_revenue_pct"]].dropna()
        if not d.empty:
            chart = alt.Chart(d).mark_boxplot().encode(
                x=alt.X("region:N", title="Region"),
                y=alt.Y("expected_partner_revenue_pct:Q", title="Expected partner revenue (%)"),
                color=alt.Color("region:N", legend=None)
            ).properties(title="Expected Partner Revenue by Region", height=260)
            render_chart(chart, "exp_rev_region_box")

st.divider()

# -------------------- Partner counts & activation --------------------
st.subheader("Partner Counts & Activation")
if {"revenue_band","partners_active_ratio"}.issubset(flt.columns):
    d = flt[["revenue_band","partners_active_ratio"]].dropna()
    if not d.empty:
        agg = d.groupby("revenue_band")["partners_active_ratio"].median().reset_index()
        bars = alt.Chart(agg).mark_bar().encode(
            x=alt.X("revenue_band:N", title="Revenue Band"),
            y=alt.Y("partners_active_ratio:Q", title="Median active/total"),
            tooltip=["revenue_band", alt.Tooltip("partners_active_ratio:Q", format=".2f")]
        ).properties(title="Activation Ratio by Revenue Band (median)", height=280)
        render_chart(bars, "activation_by_revenue_band")

if {"industry","partners_active_ratio"}.issubset(flt.columns):
    d2 = flt[["industry","partners_active_ratio"]].dropna()
    if not d2.empty:
        topN = d2["industry"].value_counts().head(12).index.tolist()
        d2 = d2[d2["industry"].isin(topN)]
        agg2 = d2.groupby("industry")["partners_active_ratio"].median().sort_values(ascending=False).reset_index()
        bars2 = alt.Chart(agg2).mark_bar().encode(
            x=alt.X("partners_active_ratio:Q", title="Median active/total"),
            y=alt.Y("industry:N", sort="-x", title=""),
            tooltip=["industry", alt.Tooltip("partners_active_ratio:Q", format=".2f")]
        ).properties(title="Activation Ratio by Industry (Top 12)", height=320)
        render_chart(bars2, "activation_by_industry")

st.divider()

# -------------------- Time to first revenue --------------------
st.subheader("Time to First Partner Revenue")
if {"program_maturity","industry","time_to_first_revenue_years"}.issubset(flt.columns):
    d = flt[["program_maturity","industry","time_to_first_revenue_years"]].dropna()
    if not d.empty:
        top_ind = d["industry"].value_counts().head(10).index.tolist()
        d = d[d["industry"].isin(top_ind)]
        heat = alt.Chart(d).mark_rect().encode(
            x=alt.X("program_maturity:N", title="Program Maturity"),
            y=alt.Y("industry:N", title="Industry"),
            color=alt.Color("mean(time_to_first_revenue_years):Q", title="Mean years"),
            tooltip=[
                "industry","program_maturity",
                alt.Tooltip("mean(time_to_first_revenue_years):Q", format=".2f", title="Mean years"),
                alt.Tooltip("count():Q", title="N")
            ],
        ).properties(title="Ramp Speed (Mean Years) by Maturity × Industry", height=360)
        render_chart(heat, "ttf_heatmap")

st.divider()

# -------------------- Biggest challenge --------------------
st.subheader("Biggest Challenge × Program Maturity")
if {"top_challenge","program_maturity"}.issubset(flt.columns):
    d = flt[["top_challenge","program_maturity"]].dropna()
    if not d.empty:
        norm = (d.groupby(["program_maturity","top_challenge"]).size()
                  .groupby(level=0).apply(lambda s: 100 * s / s.sum()).reset_index(name="pct"))
        top_chal = norm.groupby("top_challenge")["pct"].sum().sort_values(ascending=False).head(12).index.tolist()
        norm = norm[norm["top_challenge"].isin(top_chal)]
        chart = alt.Chart(norm).mark_rect().encode(
            x=alt.X("program_maturity:N", title="Program Maturity"),
            y=alt.Y("top_challenge:N", title="Top Challenge", sort="-x"),
            color=alt.Color("pct:Q", title="Share within maturity (%)"),
            tooltip=["program_maturity","top_challenge", alt.Tooltip("pct:Q", format=".1f")]
        ).properties(title="What Blocks Growth? (normalized within maturity)", height=360)
        render_chart(chart, "challenge_matrix")

st.divider()

# -------------------- Marketplace revenue --------------------
st.subheader("Cloud Marketplace Revenue by Industry")
if {"industry","marketplace_revenue_pct"}.issubset(flt.columns):
    d = flt[["industry","marketplace_revenue_pct"]].dropna()
    if not d.empty:
        top_ind = d["industry"].value_counts().head(10).index.tolist()
        d = d[d["industry"].isin(top_ind)]
        chart = alt.Chart(d).mark_boxplot().encode(
            x=alt.X("marketplace_revenue_pct:Q", title="Marketplace revenue (%)"),
            y=alt.Y("industry:N", sort="-x", title="Industry"),
            color=alt.Color("industry:N", legend=None)
        ).properties(title="Marketplace Revenue by Industry (Top 10)", height=340)
        render_chart(chart, "marketplace_by_industry")

st.divider()

# -------------------- Efficiency Explorer --------------------
st.subheader("Efficiency Explorer")
num_choices = [
    "expected_partner_revenue_pct","marketplace_revenue_pct",
    "employee_count_est","partner_team_size_est","total_partners_est",
    "active_partners_est","partners_active_ratio","time_to_first_revenue_years",
    "expected_partner_revenue_per_partner"
]
with st.expander("Pick axes / color / bubble size"):
    x_sel = st.selectbox("X axis", [c for c in num_choices if c in flt.columns],
                         index=[c for c in num_choices if c in flt.columns].index("partner_team_size_est") if "partner_team_size_est" in flt.columns else 0)
    y_sel = st.selectbox("Y axis", [c for c in num_choices if c in flt.columns],
                         index=[c for c in num_choices if c in flt.columns].index("expected_partner_revenue_pct") if "expected_partner_revenue_pct" in flt.columns else 0)
    color_by = [c for c in ["program_maturity","revenue_band","industry","region"] if c in flt.columns]
    color_sel = st.selectbox("Color by", color_by, index=0 if color_by else None)
    size_opts = [None] + [s for s in ["partner_team_size_est","total_partners_est","active_partners_est"] if s in flt.columns]
    size_sel = st.selectbox("Bubble size (optional)", size_opts)

needed = ["company_name","revenue_band","program_maturity","industry","region"]
for n in needed:
    if n not in flt.columns: flt[n] = np.nan
cols = ["company_name","revenue_band","program_maturity","industry","region", x_sel, y_sel] + ([size_sel] if size_sel else [])
d = flt[cols].dropna()
if not d.empty:
    enc = {
        "x": alt.X(f"{x_sel}:Q", title=x_sel.replace("_"," ").title()),
        "y": alt.Y(f"{y_sel}:Q", title=y_sel.replace("_"," ").title()),
        "color": alt.Color(f"{color_sel}:N", title=color_sel.replace("_"," ").title()) if color_sel else alt.value("#2663EB"),
        "tooltip": ["company_name","revenue_band","program_maturity","industry","region", x_sel, y_sel],
    }
    if size_sel:
        enc["size"] = alt.Size(f"{size_sel}:Q", title=size_sel.replace("_"," ").title())
    chart = alt.Chart(d).mark_circle(opacity=0.85).encode(**enc).properties(
        title=f"{y_sel.replace('_',' ').title()} vs {x_sel.replace('_',' ').title()}",
        height=380
    )
    render_chart(chart, "efficiency_explorer")

st.divider()

# -------------------- A/B Cohort Comparison --------------------
st.subheader("A/B Cohort Comparison")
def pick(label, values, key=None): return st.multiselect(label, sorted([x for x in values if pd.notna(x)]), key=key)

def subset(data, rev=None, mat=None, ind=None, reg=None):
    s = data.copy()
    if rev and "revenue_band" in s: s = s[s["revenue_band"].isin(rev)]
    if mat and "program_maturity" in s: s = s[s["program_maturity"].isin(mat)]
    if ind and "industry" in s: s = s[s["industry"].isin(ind)]
    if reg and "region" in s: s = s[s["region"].isin(reg)]
    return s

colA, colB = st.columns(2)
with colA:
    st.markdown("**Cohort A**")
    revA = pick("Revenue (A)", df["revenue_band"].unique()) if "revenue_band" in df else []
    matA = pick("Maturity (A)", df["program_maturity"].unique()) if "program_maturity" in df else []
    indA = pick("Industry (A)", df["industry"].unique()) if "industry" in df else []
    regA = pick("Region (A)", df["region"].unique()) if "region" in df else []
with colB:
    st.markdown("**Cohort B**")
    revB = pick("Revenue (B)", df["revenue_band"].unique(), key="revB") if "revenue_band" in df else []
    matB = pick("Maturity (B)", df["program_maturity"].unique(), key="matB") if "program_maturity" in df else []
    indB = pick("Industry (B)", df["industry"].unique(), key="indB") if "industry" in df else []
    regB = pick("Region (B)", df["region"].unique(), key="regB") if "region" in df else []

A = subset(flt, revA, matA, indA, regA)
B = subset(flt, revB, matB, indB, regB)

metrics = {
    "Expected partner revenue (%)": "expected_partner_revenue_pct",
    "Marketplace revenue (%)": "marketplace_revenue_pct",
    "Activation ratio (active/total)": "partners_active_ratio",
    "Time to first revenue (yrs)": "time_to_first_revenue_years",
    "Partner team size (est)": "partner_team_size_est",
    "Total partners (est)": "total_partners_est",
    "Active partners (est)": "active_partners_est",
}

def coh_median(s, col):
    if col not in s.columns: return np.nan
    x = pd.to_numeric(s[col], errors="coerce").dropna()
    return float(np.median(x)) if not x.empty else np.nan

rows = []
for label, col in metrics.items():
    a = coh_median(A, col); b = coh_median(B, col)
    diff = (b - a) if (pd.notna(a) and pd.notna(b)) else np.nan
    rows.append([label, a, b, diff])

cmp_df = pd.DataFrame(rows, columns=["Metric", "Cohort A (median)", "Cohort B (median)", "B - A (Δ)"])
st.dataframe(cmp_df, use_container_width=True)

st.divider()

with st.expander("Show filtered table"):
    st.dataframe(flt, use_container_width=True)
st.download_button("Download filtered CSV", flt.to_csv(index=False).encode("utf-8"),
                   file_name="sopl_filtered.csv", mime="text/csv")
