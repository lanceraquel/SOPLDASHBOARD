# app.py — SOPL 2024 Interactive Dashboard (robust loader, correct ordering)

import os
import io
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# ───────────────────────── Page & Theme ─────────────────────────
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

# Repo fallback path (optional—commit a CSV or XLSX here)
LOCAL_FALLBACK = "data/SOPL 1002 Results - Raw.csv"

# ─────────────────────── Raw header mapping (must match your survey) ───────────────────────
RAW = {
    "company_name": "Company name",
    "region": "Please select the region where your company is headquartered.",
    "industry": "What industry sector does your company operate in?",
    "revenue_band": "What is your company’s estimated annual revenue?",
    "employee_count_bin": "What is your company’s total number of employees?",
    "partner_team_size_bin": "How many people are on your Partnerships team?",
    "total_partners_bin": "How many total partners do you have?",
    "active_partners_bin": "How many active partners generated revenue in the last 12 months?",
    "time_to_first_revenue_bin": "How long does it typically take for a partnership to generate revenue after the first meeting?",
    "program_years_bin": "How long has your company had a partnership program?",
    "expected_partner_revenue_pct": "On average, what percentage of your company’s revenue is expected to come from partnerships in the next 12 months?",
    "marketplace_revenue_pct": "What percentage of your total revenue comes through cloud marketplaces?",
    "top_challenge": "What's your biggest challenge in scaling your partner program?",
}

# ─────────────────────── Bin midpoints (tune as needed) ───────────────────────
EMPLOYEES_MAP = {
    "Less than 100 employees": 50.0,
    "100 – 500 employees": 300.0,
    "501 – 5,000 employees": 2500.0,
    "More than 5,000 employees": 8000.0,
}
TEAM_SIZE_MAP = {
    "Less than 10": 5.0,
    "10–50": 30.0,
    "51–200": 125.0,
    "More than 200": 300.0,
}
TOTAL_PARTNERS_MAP = {
    "Less than 50": 25.0,
    "50 – 499": 275.0,
    "500 – 999": 750.0,
    "1,000 – 4,999": 3000.0,
    "5,000+": 6000.0,
}
ACTIVE_PARTNERS_MAP = {
    "Less than 10": 5.0,
    "10 – 99": 55.0,
    "100 – 499": 300.0,
    "500 – 999": 750.0,
    "1,000+": 1200.0,
    "Not currently monitored": np.nan,
}
TTF_REVENUE_MAP = {  # years
    "Less than 1 year": 0.5,
    "1–2 years": 1.5,
    "2–3 years": 2.5,
    "3–5 years": 4.0,
    "6–10 years": 8.0,
    "More than 10 years": 12.0,
    "I don't have this data": np.nan,
}

# ─────────────────────── Helpers ───────────────────────
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
    if "1-2 year" in s or "1–2 year" in s: return "Early"
    if "2-3 year" in s or "2–3 year" in s: return "Developing"
    if "3-5 year" in s or "3–5 year" in s: return "Developing"
    if "6-10 year" in s or "6–10 year" in s: return "Mature"
    if "More than 10 years" in s: return "Mature"
    return "Unknown"

def mid_from_bins(label: str, mapping: dict) -> float | None:
    if pd.isna(label): return None
    return mapping.get(str(label).strip(), None)

def median_iqr(s, fmt="{:.1f}"):
    x = pd.to_numeric(s, errors="coerce").dropna()
    if x.empty: return ("—","—","0")
    med = np.median(x)
    q1, q3 = np.percentile(x, [25, 75])
    return (fmt.format(med), f"[{fmt.format(q1)}–{fmt.format(q3)}]", f"{len(x)}")

def render_chart(chart: alt.Chart, name: str, height=None):
    if height is not None:
        chart = chart.properties(height=height)
    st.altair_chart(chart, use_container_width=True)
    try:
        import vl_convert as vlc
        png = vlc.vegalite_to_png(chart.to_dict(), scale=2)
        st.download_button(f"Download {name}.png", png, file_name=f"{name}.png", mime="image/png")
    except Exception:
        pass

# ─────────────────────── Robust loader ───────────────────────
@st.cache_data(show_spinner=False)
def load_raw(uploaded):
    """
    Robust reader:
    - Excel first
    - CSV with multiple encodings/delimiters
    - forgiving parser; skip bad lines
    - fallback to LOCAL_FALLBACK
    """
    # Uploaded?
    if uploaded is not None:
        name = (uploaded.name or "").lower()

        # Excel?
        if name.endswith((".xlsx", ".xls")):
            try:
                return pd.read_excel(uploaded)
            except Exception as e:
                st.warning(f"Excel read failed: {e}")

        # CSV bytes
        try:
            data = uploaded.getvalue()
        except Exception:
            uploaded.seek(0)
            data = uploaded.read()

        encodings = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
        delimiters = [None, ",", "\t", ";", "|"]  # None = sniff
        for enc in encodings:
            for sep in delimiters:
                try:
                    buf = io.BytesIO(data)
                    df = pd.read_csv(
                        buf,
                        encoding=enc,
                        sep=sep,
                        engine="python",
                        on_bad_lines="skip",
                        encoding_errors="replace",
                    )
                    if df.shape[1] >= 2:
                        return df
                except Exception:
                    continue
        st.error("Could not decode the uploaded file. If possible, upload XLSX or UTF-8 CSV.")

    # Fallback on repo
    if os.path.exists(LOCAL_FALLBACK):
        if LOCAL_FALLBACK.lower().endswith((".xlsx", ".xls")):
            try:
                return pd.read_excel(LOCAL_FALLBACK)
            except Exception as e:
                st.warning(f"Local Excel fallback failed: {e}")
        try:
            return pd.read_csv(LOCAL_FALLBACK, sep=None, engine="python")
        except Exception:
            for enc in ["utf-8-sig", "utf-8", "cp1252", "latin-1"]:
                try:
                    return pd.read_csv(
                        LOCAL_FALLBACK,
                        encoding=enc,
                        sep=None,
                        engine="python",
                        on_bad_lines="skip",
                        encoding_errors="replace",
                    )
                except Exception:
                    continue
            st.error("Local fallback exists but could not be decoded.")

    return pd.DataFrame()

# ─────────────────────── Standardize (define BEFORE using it) ───────────────────────
def standardize(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Validate required raw columns (show exactly what’s missing)
    missing = [v for v in RAW.values() if v not in df_raw.columns]
    if missing:
        st.error("Missing expected columns in CSV:\n- " + "\n- ".join(missing))
        return pd.DataFrame()

    d = pd.DataFrame({
        "company_name": df_raw[RAW["company_name"]],
        "region": df_raw[RAW["region"]].map(map_region_short),
        "industry": df_raw[RAW["industry"]],
        "revenue_band": df_raw[RAW["revenue_band"]],
        "employee_count_bin": df_raw[RAW["employee_count_bin"]],
        "partner_team_size_bin": df_raw[RAW["partner_team_size_bin"]],
        "total_partners_bin": df_raw[RAW["total_partners_bin"]],
        "active_partners_bin": df_raw[RAW["active_partners_bin"]],
        "time_to_first_revenue_bin": df_raw[RAW["time_to_first_revenue_bin"]],
        "program_years_bin": df_raw[RAW["program_years_bin"]],
        "expected_partner_revenue_pct": df_raw[RAW["expected_partner_revenue_pct"]].apply(to_pct_numeric),
        "marketplace_revenue_pct": df_raw[RAW["marketplace_revenue_pct"]].apply(to_pct_numeric),
        "top_challenge": df_raw[RAW["top_challenge"]],
    })

    # Numeric estimates for binned questions
    d["employee_count_est"] = d["employee_count_bin"].apply(lambda x: mid_from_bins(x, EMPLOYEES_MAP))
    d["partner_team_size_est"] = d["partner_team_size_bin"].apply(lambda x: mid_from_bins(x, TEAM_SIZE_MAP))
    d["total_partners_est"] = d["total_partners_bin"].apply(lambda x: mid_from_bins(x, TOTAL_PARTNERS_MAP))
    d["active_partners_est"] = d["active_partners_bin"].apply(lambda x: mid_from_bins(x, ACTIVE_PARTNERS_MAP))
    d["time_to_first_revenue_years"] = d["time_to_first_revenue_bin"].apply(lambda x: mid_from_bins(x, TTF_REVENUE_MAP))

    # Derived maturity from program tenure
    d["program_maturity"] = df_raw[RAW["program_years_bin"]].apply(maturity_from_years)

    # Efficiency/derived
    d["partners_active_ratio"] = d["active_partners_est"] / d["total_partners_est"]
    d["expected_partner_revenue_per_partner"] = d["expected_partner_revenue_pct"] / d["partner_team_size_est"]

    return d

# ─────────────────────── MAIN (runs after all defs exist) ───────────────────────
with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload SOPL raw CSV or Excel", type=["csv", "xlsx", "xls"])

raw = load_raw(uploaded)
if raw.empty:
    st.info("No data loaded yet. Upload a CSV/XLSX or add a repo fallback file at:\n"
            f"**{LOCAL_FALLBACK}**")
    st.stop()

try:
    df = standardize(raw)
except Exception as e:
    st.exception(e)
    st.stop()

if df.empty:
    st.stop()

# ─────────────────────── Filters ───────────────────────
with st.sidebar:
    st.header("Filters")

    rev_opts = df["revenue_band"].dropna().unique().tolist()
    rev_sel = st.multiselect("Revenue Band", options=rev_opts, default=rev_opts)

    ind_opts = sorted(df["industry"].dropna().astype(str).unique().tolist())
    ind_sel = st.multiselect("Industry", options=ind_opts, default=ind_opts)

    region_order = ["APAC", "EMEA", "LATAM", "NA"]
    reg_in = [r for r in region_order if r in df["region"].dropna().unique().tolist()]
    reg_extra = [r for r in sorted(df["region"].dropna().unique().tolist()) if r not in region_order]
    reg_sel = st.multiselect("Region", options=reg_in + reg_extra, default=reg_in + reg_extra)

    mat_order = ["Early", "Developing", "Mature", "Unknown"]
    mat_in = [m for m in mat_order if m in df["program_maturity"].dropna().unique().tolist()]
    mat_sel = st.multiselect("Program Maturity", options=mat_in, default=mat_in)

    emp_bins = df["employee_count_bin"].dropna().unique().tolist()
    emp_sel = st.multiselect("Employee Count (bin)", options=emp_bins, default=emp_bins)

    team_bins = df["partner_team_size_bin"].dropna().unique().tolist()
    team_sel = st.multiselect("Partner Team Size (bin)", options=team_bins, default=team_bins)

flt = df.copy()
flt = flt[flt["revenue_band"].isin(rev_sel)]
flt = flt[flt["industry"].isin(ind_sel)]
flt = flt[flt["region"].isin(reg_sel)]
flt = flt[flt["program_maturity"].isin(mat_sel)]
flt = flt[flt["employee_count_bin"].isin(emp_sel)]
flt = flt[flt["partner_team_size_bin"].isin(team_sel)]

# ─────────────────────── KPIs ───────────────────────
st.title("SOPL 2024 – Interactive Dashboard (Aligned to Survey Questions)")

k1, k2, k3, k4 = st.columns(4)
m, iqr, n = median_iqr(flt["expected_partner_revenue_pct"])
k1.metric("Expected partner revenue (%)", m, f"{iqr} | N={n}")

m, iqr, n = median_iqr(flt["marketplace_revenue_pct"])
k2.metric("Marketplace revenue (%)", m, f"{iqr} | N={n}")

m, iqr, n = median_iqr(flt["partner_team_size_est"], "{:.0f}")
k3.metric("Partner team size (est)", m, f"{iqr} | N={n}")

m, iqr, n = median_iqr(flt["time_to_first_revenue_years"])
k4.metric("Time to first revenue (yrs)", m, f"{iqr} | N={n}")

k5, k6, k7, k8 = st.columns(4)
m, iqr, n = median_iqr(flt["total_partners_est"], "{:.0f}")
k5.metric("Total partners (est)", m, f"{iqr} | N={n}")

m, iqr, n = median_iqr(flt["active_partners_est"], "{:.0f}")
k6.metric("Active partners (est)", m, f"{iqr} | N={n}")

m, iqr, n = median_iqr(flt["partners_active_ratio"], "{:.2f}")
k7.metric("Activation ratio (active/total)", m, f"{iqr} | N={n}")

if {"partner_team_size_est","employee_count_est"}.issubset(flt.columns):
    tpe = (flt["partner_team_size_est"] / (flt["employee_count_est"] / 1000)).replace([np.inf, -np.inf], np.nan)
    m, iqr, n = median_iqr(tpe, "{:.2f}")
    k8.metric("Team per 1k employees", m, f"{iqr} | N={n}")
else:
    k8.metric("Team per 1k employees", "—", "—")

g1, g2 = st.columns(2)
g1.metric("Responses (after filters)", f"{len(flt):,}")
g2.metric("Total responses", f"{len(df):,}")

st.divider()

# ─────────────────────── Expected partner revenue ───────────────────────
st.subheader("Expected Partner Revenue — Distributions & Cohorts")

for cohort_col, title in [("program_maturity", "by Program Maturity"), ("revenue_band", "by Revenue Band")]:
    d = flt[[cohort_col, "expected_partner_revenue_pct"]].dropna()
    if d.empty:
        st.info(f"No data for {title}.")
        continue
    base = alt.Chart(d).transform_density(
        "expected_partner_revenue_pct", groupby=[cohort_col], as_=["value","density"]
    )
    chart = base.mark_area(opacity=0.45).encode(
        x=alt.X("value:Q", title="Expected partner revenue (%)"),
        y=alt.Y("density:Q", title="Density"),
        color=alt.Color(f"{cohort_col}:N", title=cohort_col.replace("_"," ").title())
    ).properties(title=f"Distribution {title}", height=260)
    render_chart(chart, f"expected_rev_{cohort_col}_density")

d = flt[["region","expected_partner_revenue_pct"]].dropna()
if not d.empty:
    chart = alt.Chart(d).mark_boxplot().encode(
        x=alt.X("region:N", title="Region"),
        y=alt.Y("expected_partner_revenue_pct:Q", title="Expected partner revenue (%)"),
        color=alt.Color("region:N", legend=None)
    ).properties(title="Expected Partner Revenue by Region", height=260)
    render_chart(chart, "expected_rev_by_region")

st.divider()

# ─────────────────────── Partners & activation ───────────────────────
st.subheader("Partner Counts & Activation")

d = flt[["revenue_band","partners_active_ratio"]].dropna()
if not d.empty:
    agg = d.groupby("revenue_band")["partners_active_ratio"].median().reset_index()
    bars = alt.Chart(agg).mark_bar().encode(
        x=alt.X("revenue_band:N", title="Revenue Band"),
        y=alt.Y("partners_active_ratio:Q", title="Median active/total"),
        tooltip=["revenue_band", alt.Tooltip("partners_active_ratio:Q", format=".2f")]
    ).properties(title="Activation Ratio by Revenue Band (median)", height=280)
    render_chart(bars, "activation_by_revenue_band")

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

# ─────────────────────── Time to first revenue ───────────────────────
st.subheader("Time to First Partner Revenue")

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

# ─────────────────────── Biggest challenge ───────────────────────
st.subheader("Biggest Challenge × Program Maturity")

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

# ─────────────────────── Marketplace revenue ───────────────────────
st.subheader("Cloud Marketplace Revenue by Industry")

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

# ─────────────────────── Efficiency Explorer ───────────────────────
st.subheader("Efficiency Explorer")

num_choices = [
    "expected_partner_revenue_pct","marketplace_revenue_pct",
    "employee_count_est","partner_team_size_est","total_partners_est",
    "active_partners_est","partners_active_ratio","time_to_first_revenue_years",
    "expected_partner_revenue_per_partner"
]
with st.expander("Pick axes / color / bubble size"):
    x_sel = st.selectbox("X axis", num_choices, index=num_choices.index("partner_team_size_est"))
    y_sel = st.selectbox("Y axis", num_choices, index=num_choices.index("expected_partner_revenue_pct"))
    color_sel = st.selectbox("Color by", ["program_maturity","revenue_band","industry","region"])
    size_sel = st.selectbox("Bubble size (optional)", [None,"partner_team_size_est","total_partners_est","active_partners_est"])

d = flt[["company_name","revenue_band","program_maturity","industry","region", x_sel, y_sel] + ([size_sel] if size_sel else [])].dropna()
if not d.empty:
    enc = {
        "x": alt.X(f"{x_sel}:Q", title=x_sel.replace("_"," ").title()),
        "y": alt.Y(f"{y_sel}:Q", title=y_sel.replace("_"," ").title()),
        "color": alt.Color(f"{color_sel}:N", title=color_sel.replace("_"," ").title()),
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

# ─────────────────────── A/B Cohort Comparison ───────────────────────
st.subheader("A/B Cohort Comparison")

def pick(label, values, key=None):
    return st.multiselect(label, sorted([x for x in values if pd.notna(x)]), key=key)

colA, colB = st.columns(2)
with colA:
    st.markdown("**Cohort A**")
    revA = pick("Revenue (A)", df["revenue_band"].unique())
    matA = pick("Maturity (A)", df["program_maturity"].unique())
    indA = pick("Industry (A)", df["industry"].unique())
    regA = pick("Region (A)", df["region"].unique())
with colB:
    st.markdown("**Cohort B**")
    revB = pick("Revenue (B)", df["revenue_band"].unique(), key="revB")
    matB = pick("Maturity (B)", df["program_maturity"].unique(), key="matB")
    indB = pick("Industry (B)", df["industry"].unique(), key="indB")
    regB = pick("Region (B)", df["region"].unique(), key="regB")

def subset(data, rev, mat, ind, reg):
    s = data.copy()
    if rev: s = s[s["revenue_band"].isin(rev)]
    if mat: s = s[s["program_maturity"].isin(mat)]
    if ind: s = s[s["industry"].isin(ind)]
    if reg: s = s[s["region"].isin(reg)]
    return s

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
    x = pd.to_numeric(s[col], errors="coerce").dropna()
    return float(np.median(x)) if not x.empty else np.nan

rows = []
for label, col in metrics.items():
    a = coh_median(A, col)
    b = coh_median(B, col)
    diff = (b - a) if (pd.notna(a) and pd.notna(b)) else np.nan
    rows.append([label, a, b, diff])

cmp_df = pd.DataFrame(rows, columns=["Metric", "Cohort A (median)", "Cohort B (median)", "B - A (Δ)"])
st.dataframe(cmp_df, use_container_width=True)

st.divider()

# ─────────────────────── Full table & export ───────────────────────
with st.expander("Show filtered table"):
    st.dataframe(flt, use_container_width=True)

st.download_button("Download filtered CSV", flt.to_csv(index=False).encode("utf-8"),
                   file_name="sopl_filtered.csv", mime="text/csv")
