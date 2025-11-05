import os
import re
import io
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# ───────────────────────── Page & Theme ─────────────────────────
st.set_page_config(page_title="SOPL 2024 – Interactive (Raw Columns)", page_icon="📊", layout="wide")

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

# ─────────────────────── Helpers: coercions ───────────────────────
def mid_from_range(label: str, mapping: dict) -> float | None:
    """Map a categorical range label to an estimated midpoint using mapping; return None if unknown."""
    if pd.isna(label):
        return None
    s = str(label).strip()
    return mapping.get(s, None)

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
    if "3-5 year" in s or "3–5 year" in s: return "Developing"
    if "6-10 year" in s or "6–10 year" in s: return "Mature"
    if "More than 10 years" in s: return "Mature"
    return "Unknown"

def years_to_numeric(x: str) -> float | None:
    if pd.isna(x): return np.nan
    s = str(x)
    if "Less than 1 year" in s: return 0.5
    if "1-2 year" in s or "1–2 year" in s: return 1.5
    if "2-3 year" in s or "2–3 year" in s: return 2.5
    if "3-5 year" in s or "3–5 year" in s: return 4.0
    if "6-10 year" in s or "6–10 year" in s: return 8.0
    if "More than 10 years" in s: return 12.0
    return np.nan

def render_chart(chart: alt.Chart, filename: str):
    st.altair_chart(chart, use_container_width=True)
    try:
        import vl_convert as vlc
        png = vlc.vegalite_to_png(chart.to_dict(), scale=2)
        st.download_button(f"Download {filename}.png", png, file_name=f"{filename}.png", mime="image/png")
    except Exception:
        pass

# ───────────────────── Load & standardize data ─────────────────────
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
    "I don't have this data": np.nan,
}

@st.cache_data(show_spinner=False)
def load_raw(uploaded):
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    elif os.path.exists(LOCAL_FALLBACK):
        df = pd.read_csv(LOCAL_FALLBACK)
    else:
        return pd.DataFrame()
    return df

def standardize(df_raw: pd.DataFrame) -> pd.DataFrame:
    # ensure columns exist
    for need in RAW.values():
        if need not in df_raw.columns:
            st.error(f"Missing column in CSV: {need}")
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

    # numeric estimates (for charts/correlations)
    d["employee_count_est"] = d["employee_count_bin"].apply(lambda x: mid_from_range(x, EMPLOYEES_MAP))
    d["partner_team_size_est"] = d["partner_team_size_bin"].apply(lambda x: mid_from_range(x, TEAM_SIZE_MAP))
    d["total_partners_est"] = d["total_partners_bin"].apply(lambda x: mid_from_range(x, TOTAL_PARTNERS_MAP))
    d["active_partners_est"] = d["active_partners_bin"].apply(lambda x: mid_from_range(x, ACTIVE_PARTNERS_MAP))
    d["time_to_first_revenue_years"] = d["time_to_first_revenue_bin"].apply(lambda x: mid_from_range(x, TTF_REVENUE_MAP))

    # derived maturity
    d["program_maturity"] = df_raw[RAW["program_years_bin"]].apply(maturity_from_years)

    # useful efficiency metrics
    d["partners_active_ratio"] = d["active_partners_est"] / d["total_partners_est"]
    d["expected_partner_revenue_per_partner"] = d["expected_partner_revenue_pct"] / d["partner_team_size_est"]
    return d

# ───────────────────────────── Load data ─────────────────────────────
with st.sidebar:
    st.header("Data")
    up = st.file_uploader("Upload SOPL raw CSV", type=["csv"])
raw = load_raw(up)
if raw.empty:
    st.stop()
df = standardize(raw)
if df.empty:
    st.stop()

# ───────────────────────────── Filters ─────────────────────────────
with st.sidebar:
    st.header("Filters")
    # fixed orders where relevant
    revenue_options = df["revenue_band"].dropna().unique().tolist()
    revenue_sel = st.multiselect("Revenue Band", options=revenue_options, default=revenue_options)

    industry_options = sorted(df["industry"].dropna().astype(str).unique().tolist())
    industry_sel = st.multiselect("Industry", options=industry_options, default=industry_options)

    region_options = ["APAC","EMEA","LATAM","NA"]
    region_in_data = [r for r in region_options if r in df["region"].dropna().unique().tolist()]
    region_extra = [r for r in df["region"].dropna().unique().tolist() if r not in region_options]
    region_sel = st.multiselect("Region", options=region_in_data + region_extra, default=region_in_data + region_extra)

    maturity_options = ["Early","Developing","Mature","Unknown"]
    mat_in = [m for m in maturity_options if m in df["program_maturity"].dropna().unique().tolist()]
    mat_sel = st.multiselect("Program Maturity", options=mat_in, default=mat_in)

    emp_bins = df["employee_count_bin"].dropna().unique().tolist()
    emp_sel = st.multiselect("Employee Count (bin)", options=emp_bins, default=emp_bins)

    team_bins = df["partner_team_size_bin"].dropna().unique().tolist()
    team_sel = st.multiselect("Partner Team Size (bin)", options=team_bins, default=team_bins)

flt = df.copy()
flt = flt[flt["revenue_band"].isin(revenue_sel)]
flt = flt[flt["industry"].isin(industry_sel)]
flt = flt[flt["region"].isin(region_sel)]
flt = flt[flt["program_maturity"].isin(mat_sel)]
flt = flt[flt["employee_count_bin"].isin(emp_sel)]
flt = flt[flt["partner_team_size_bin"].isin(team_sel)]

# ───────────────────────────── KPIs ─────────────────────────────
st.title("SOPL 2024 – Interactive Dashboard (Raw-Aligned)")

def safe_mean(s, fmt="{:.1f}"):
    s = pd.to_numeric(s, errors="coerce")
    return "—" if s.dropna().empty else fmt.format(s.mean())

k1,k2,k3,k4 = st.columns(4)
k1.metric("Expected partner revenue (%)", safe_mean(flt["expected_partner_revenue_pct"]))
k2.metric("Marketplace revenue (%)", safe_mean(flt["marketplace_revenue_pct"]))
k3.metric("Employees (est)", safe_mean(flt["employee_count_est"], "{:.0f}"))
k4.metric("Partner team size (est)", safe_mean(flt["partner_team_size_est"], "{:.0f}"))

k5,k6,k7,k8 = st.columns(4)
k5.metric("Total partners (est)", safe_mean(flt["total_partners_est"], "{:.0f}"))
k6.metric("Active partners (est)", safe_mean(flt["active_partners_est"], "{:.0f}"))
k7.metric("Active / Total ratio", safe_mean(flt["partners_active_ratio"], "{:.2f}"))
k8.metric("Time to first revenue (yrs)", safe_mean(flt["time_to_first_revenue_years"], "{:.1f}"))

g1,g2 = st.columns(2)
g1.metric("Responses (after filters)", f"{len(flt):,}")
g2.metric("Total responses", f"{len(df):,}")

st.divider()

# ─────────────────────────── Distributions ───────────────────────────
left, right = st.columns(2)

with left:
    tmp = flt["industry"].value_counts(normalize=True).mul(100).rename("Percent").reset_index()
    tmp.columns = ["industry","Percent"]
    chart = alt.Chart(tmp).mark_bar().encode(
        x=alt.X("Percent:Q", title="Percent of companies"),
        y=alt.Y("industry:N", sort="-x"),
        tooltip=["industry", alt.Tooltip("Percent:Q", format=".1f")]
    ).properties(height=280, title="Industry Mix")
    render_chart(chart, "industry_mix")

with right:
    tmp = flt["revenue_band"].value_counts(normalize=True).mul(100).rename("Percent").reset_index()
    tmp.columns = ["revenue_band","Percent"]
    chart = alt.Chart(tmp).mark_bar().encode(
        x=alt.X("Percent:Q", title="Percent of companies"),
        y=alt.Y("revenue_band:N", sort="-x"),
        tooltip=["revenue_band", alt.Tooltip("Percent:Q", format=".1f")]
    ).properties(height=280, title="Revenue Band Mix")
    render_chart(chart, "revenue_mix")

st.divider()

# ───────────────────────── Cohort box plots ─────────────────────────
b1, b2 = st.columns(2)
with b1:
    d = flt[["expected_partner_revenue_pct","revenue_band"]].dropna()
    if not d.empty:
        chart = alt.Chart(d).mark_boxplot().encode(
            x=alt.X("revenue_band:N", title="Revenue Band"),
            y=alt.Y("expected_partner_revenue_pct:Q", title="Expected partner revenue (%)"),
            color=alt.Color("revenue_band:N", legend=None),
            tooltip=["revenue_band","expected_partner_revenue_pct"]
        ).properties(height=320, title="Expected Partner Revenue % by Revenue Band")
        render_chart(chart, "exp_partner_rev_by_revenue")
    else:
        st.info("No data for Expected partner revenue by Revenue Band.")

with b2:
    d = flt[["expected_partner_revenue_pct","program_maturity"]].dropna()
    if not d.empty:
        chart = alt.Chart(d).mark_boxplot().encode(
            x=alt.X("program_maturity:N", title="Program Maturity"),
            y=alt.Y("expected_partner_revenue_pct:Q", title="Expected partner revenue (%)"),
            color=alt.Color("program_maturity:N", legend=None),
            tooltip=["program_maturity","expected_partner_revenue_pct"]
        ).properties(height=320, title="Expected Partner Revenue % by Maturity")
        render_chart(chart, "exp_partner_rev_by_maturity")
    else:
        st.info("No data for Expected partner revenue by Maturity.")

st.divider()

# ───────────────────── Relationship Explorer ─────────────────────
st.subheader("Relationship Explorer")
num_choices = ["expected_partner_revenue_pct","marketplace_revenue_pct",
               "employee_count_est","partner_team_size_est","total_partners_est",
               "active_partners_est","partners_active_ratio","time_to_first_revenue_years",
               "expected_partner_revenue_per_partner"]
with st.expander("Pick axes / color / bubble size"):
    x_sel = st.selectbox("X axis", num_choices, index=num_choices.index("employee_count_est"))
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
    chart = alt.Chart(d).mark_circle(opacity=0.85).encode(**enc).properties(height=380,
        title=f"{y_sel.replace('_',' ').title()} vs {x_sel.replace('_',' ').title()}")
    render_chart(chart, "relationship_explorer")
else:
    st.info("No data for the selected axes after filters.")

st.divider()

# ───────────────────── Cohort summary table ─────────────────────
st.markdown("**Cohort Means (by Revenue Band)**")
metrics = ["expected_partner_revenue_pct","marketplace_revenue_pct","employee_count_est",
           "partner_team_size_est","total_partners_est","active_partners_est","partners_active_ratio",
           "time_to_first_revenue_years","expected_partner_revenue_per_partner"]
cohort = flt.groupby("revenue_band")[metrics].mean(numeric_only=True).reset_index()
st.dataframe(cohort, use_container_width=True)

st.divider()

# ───────────────────── Correlation heatmap ─────────────────────
st.subheader("Correlation (Pearson)")
corr_cols = [c for c in metrics if c in flt.columns]
if len(corr_cols) >= 2 and not flt[corr_cols].dropna().empty:
    corr = flt[corr_cols].corr(numeric_only=True).reset_index().melt("index")
    corr.columns = ["x","y","corr"]
    chart = alt.Chart(corr).mark_rect().encode(
        x=alt.X("x:N", title=""),
        y=alt.Y("y:N", title=""),
        color=alt.Color("corr:Q", title="r"),
        tooltip=[alt.Tooltip("x:N"), alt.Tooltip("y:N"), alt.Tooltip("corr:Q", format=".2f")]
    ).properties(height=360, title="Correlation Heatmap")
    render_chart(chart, "correlation_heatmap")
else:
    st.info("Not enough numeric data for correlation.")

st.divider()

# ───────────────────── Leaderboards + Table ─────────────────────
st.subheader("Leaderboards")
c1, c2, c3 = st.columns(3)
def topk(col, k=10):
    if col not in flt.columns: return pd.DataFrame()
    d = flt[["company_name","revenue_band","program_maturity","industry","region", col]].dropna()
    return d.sort_values(col, ascending=False).head(k)

with c1:
    st.markdown("**Top 10: Expected partner rev %**")
    st.dataframe(topk("expected_partner_revenue_pct"), use_container_width=True, height=360)
with c2:
    st.markdown("**Top 10: Active / Total partners ratio**")
    st.dataframe(topk("partners_active_ratio"), use_container_width=True, height=360)
with c3:
    st.markdown("**Top 10: Partner team size (est)**")
    st.dataframe(topk("partner_team_size_est"), use_container_width=True, height=360)

with st.expander("Show filtered table"):
    st.dataframe(flt, use_container_width=True)

st.download_button("Download filtered CSV", flt.to_csv(index=False).encode("utf-8"), file_name="sopl_filtered.csv", mime="text/csv")
