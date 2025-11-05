import os
import io
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# ===================== PAGE & THEME =====================
st.set_page_config(page_title="SOPL 2024 – Interactive (Pro)", page_icon="📊", layout="wide")

HOUSE_COLORS = ["#2663EB", "#24A19C", "#F29F05", "#C4373D", "#7B61FF", "#2A9D8F", "#D97706"]
def house_theme():
    return {
        "config": {
            "view": {"continuousWidth": 400, "continuousHeight": 300},
            "range": {
                "category": HOUSE_COLORS,
                "heatmap": {"scheme": "blueorange"},
            },
            "axis": {"labelColor": "#E5E7EB", "titleColor": "#F3F4F6", "grid": True, "gridColor": "#2F343B"},
            "legend": {"labelColor": "#E5E7EB", "titleColor": "#F3F4F6"},
            "title": {"color": "#F3F4F6", "fontSize": 14, "anchor": "start"},
            "background": None,
        }
    }
alt.themes.register("house", house_theme)
alt.themes.enable("house")

# ===================== CONFIG (snake_case columns) =====================
REQUIRED_COLS = [
    "company_id","company_name","region","industry","company_type","employee_count",
    "revenue_band","partner_team_size","program_maturity",
    "partner_sourced_revenue_pct","partner_influenced_revenue_pct","ecosystem_ACV_uplift_pct",
    "pipeline_from_partners_pct","time_to_first_partner_win_days","num_active_partners",
    "annual_partner_budget_usd","tooling_spend_usd","enablement_hours_per_qtr","has_formal_training",
    "sales_alignment_score","goal_setting_clarity_score","top_challenge","exec_alignment_score",
    "overall_program_health",
]
NUMERIC_COLS = [
    "employee_count","partner_team_size","partner_sourced_revenue_pct",
    "partner_influenced_revenue_pct","ecosystem_ACV_uplift_pct","pipeline_from_partners_pct",
    "time_to_first_partner_win_days","num_active_partners","annual_partner_budget_usd",
    "tooling_spend_usd","enablement_hours_per_qtr","sales_alignment_score",
    "goal_setting_clarity_score","exec_alignment_score","overall_program_health",
]
REVENUE_ORDER = ["<5M","5-20M","20-100M","100-500M","500M+"]
MATURITY_ORDER = ["Early","Developing","Mature"]
COMPANY_TYPE_ORDER = ["Startup","Scaleup","Enterprise"]
REGION_ORDER = ["APAC","EMEA","LATAM","NA"]
LOCAL_FALLBACK = "data/SOPL 1002 Results - Raw.csv"

# ===================== HELPERS =====================
def coerce_columns(df: pd.DataFrame) -> pd.DataFrame:
    # normalize headers
    df.columns = [c.strip().replace(" ", "_").replace("-", "_").lower() for c in df.columns]
    # numerics
    for c in NUMERIC_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # canonicalize categoricals
    if "revenue_band" in df.columns:
        repl = {
            "<$5m":"<5M","<$5M":"<5M","<5m":"<5M","<5M":"<5M",
            "5–20m":"5-20M","5-20m":"5-20M","5-20M":"5-20M",
            "20–100m":"20-100M","20-100m":"20-100M","20-100M":"20-100M",
            "100–500m":"100-500M","100-500m":"100-500M","100-500M":"100-500M",
            ">$500m":"500M+","500m+":"500M+","500M+":"500M+",
        }
        df["revenue_band"] = df["revenue_band"].astype(str).str.strip().map(lambda x: repl.get(x, x))
    if "program_maturity" in df.columns:
        df["program_maturity"] = df["program_maturity"].astype(str).str.title()
    if "company_type" in df.columns:
        df["company_type"] = df["company_type"].astype(str).str.title()
    if "region" in df.columns:
        df["region"] = df["region"].astype(str).str.upper()

    # derived metrics
    if {"partner_team_size","pipeline_from_partners_pct"}.issubset(df.columns):
        df["pipeline_pct_per_partner"] = df["pipeline_from_partners_pct"] / df["partner_team_size"].replace(0, np.nan)
    if {"partner_team_size","annual_partner_budget_usd"}.issubset(df.columns):
        df["budget_per_partner"] = df["annual_partner_budget_usd"] / df["partner_team_size"].replace(0, np.nan)
    if {"partner_team_size","tooling_spend_usd"}.issubset(df.columns):
        df["tooling_per_partner"] = df["tooling_spend_usd"] / df["partner_team_size"].replace(0, np.nan)
    if {"partner_team_size","enablement_hours_per_qtr"}.issubset(df.columns):
        df["enablement_hours_per_partner"] = df["enablement_hours_per_qtr"] / df["partner_team_size"].replace(0, np.nan)
    if {"partner_sourced_revenue_pct","partner_influenced_revenue_pct"}.issubset(df.columns):
        df["sourced_to_influenced_ratio"] = df["partner_sourced_revenue_pct"] / df["partner_influenced_revenue_pct"].replace(0, np.nan)
    return df

@st.cache_data(show_spinner=False)
def load_data(uploaded):
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    elif os.path.exists(LOCAL_FALLBACK):
        df = pd.read_csv(LOCAL_FALLBACK)
    else:
        return pd.DataFrame()
    df = coerce_columns(df)
    missing = [c for c in [c.lower() for c in REQUIRED_COLS] if c not in df.columns]
    if missing:
        st.error("Missing required columns: " + ", ".join(missing))
        return pd.DataFrame()
    return df

# ---------- Deep-linking helpers ----------
SEP = "|"
def qp_read_list(key, default):
    v = st.query_params.get(key, None)
    if not v:
        return default
    if isinstance(v, list):  # streamlit may store multiple
        v = v[-1]
    return [x for x in v.split(SEP) if x]

def qp_read_range(key, default):
    v = st.query_params.get(key, None)
    if not v:
        return default
    if isinstance(v, list): v = v[-1]
    try:
        lo, hi = v.split(",")
        return (int(lo), int(hi))
    except Exception:
        return default

def qp_write(**kwargs):
    # kwargs are lists or tuples -> string encodings
    payload = {}
    for k, v in kwargs.items():
        if isinstance(v, (list, tuple)):
            if len(v) == 2 and all(isinstance(x, (int, np.integer)) for x in v):
                payload[k] = f"{v[0]},{v[1]}"
            else:
                payload[k] = SEP.join([str(x) for x in v])
        else:
            payload[k] = str(v)
    st.query_params.clear()
    st.query_params.update(payload)

# ---------- Chart rendering + PNG download ----------
def render_chart(chart: alt.Chart, filename: str, helptext: str = ""):
    st.altair_chart(chart, use_container_width=True)
    png_bytes = None
    try:
        import vl_convert as vlc
        png_bytes = vlc.vegalite_to_png(chart.to_dict(), scale=2)
    except Exception:
        png_bytes = None
    if png_bytes:
        st.download_button(
            f"Download {filename}.png",
            data=png_bytes,
            file_name=f"{filename}.png",
            mime="image/png",
            help=helptext or "High-res (2x) PNG export"
        )
    else:
        st.info("PNG export not available in this environment. You can still right-click → Save image or download the data beneath.")

# ---------- Small utilities ----------
def safe_mean(s, fmt="{:.1f}"):
    s = pd.to_numeric(s, errors="coerce")
    if s.dropna().empty:
        return "—"
    return fmt.format(s.mean())


# ===================== LOAD =====================
with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Upload SOPL CSV", type=["csv"])
df = load_data(uploaded)
if df.empty:
    st.stop()

# ===================== FILTERS (with deep-links) =====================
with st.sidebar:
    st.header("Filters")

    # Build defaults from query params (or data)
    rev_avail = [r for r in REVENUE_ORDER if r in df["revenue_band"].dropna().unique().tolist()]
    rev_default = rev_avail or REVENUE_ORDER
    ind_all = sorted(df["industry"].dropna().astype(str).unique().tolist())
    type_all = [c for c in COMPANY_TYPE_ORDER if c in df["company_type"].unique()] + \
               [c for c in sorted(df["company_type"].unique()) if c not in COMPANY_TYPE_ORDER]
    region_all = [r for r in REGION_ORDER if r in df["region"].unique()] + \
                 [r for r in sorted(df["region"].unique()) if r not in REGION_ORDER]
    mat_all = [m for m in MATURITY_ORDER if m in df["program_maturity"].unique()] + \
              [m for m in sorted(df["program_maturity"].unique()) if m not in MATURITY_ORDER]

    rev_sel = st.multiselect("Revenue Band",
                             options=REVENUE_ORDER,
                             default=qp_read_list("rev", rev_default))
    ind_sel = st.multiselect("Industry",
                             options=ind_all,
                             default=qp_read_list("ind", ind_all))
    ctype_sel = st.multiselect("Company Type",
                               options=type_all,
                               default=qp_read_list("ctype", type_all))
    region_sel = st.multiselect("Region",
                                options=region_all,
                                default=qp_read_list("reg", region_all))
    maturity_sel = st.multiselect("Program Maturity",
                                  options=mat_all,
                                  default=qp_read_list("mat", mat_all))

    emp_min, emp_max = int(df["employee_count"].min()), int(df["employee_count"].max())
    emp_sel = st.slider("Employee Count", min_value=emp_min, max_value=emp_max,
                        value=qp_read_range("emp", (emp_min, emp_max)))
    team_min, team_max = int(df["partner_team_size"].min()), int(df["partner_team_size"].max())
    team_sel = st.slider("Partner Team Size", min_value=team_min, max_value=team_max,
                         value=qp_read_range("team", (team_min, team_max)))

    # Update URL with current selections
    qp_write(rev=rev_sel, ind=ind_sel, ctype=ctype_sel, reg=region_sel, mat=maturity_sel,
             emp=emp_sel, team=team_sel)

# Apply filters
flt = df.copy()
flt = flt[flt["revenue_band"].astype(str).isin(rev_sel)]
flt = flt[flt["industry"].astype(str).isin(ind_sel)]
flt = flt[flt["company_type"].astype(str).isin(ctype_sel)]
flt = flt[flt["region"].astype(str).isin(region_sel)]
flt = flt[flt["program_maturity"].astype(str).isin(maturity_sel)]
flt = flt[flt["employee_count"].between(emp_sel[0], emp_sel[1])]
flt = flt[flt["partner_team_size"].between(team_sel[0], team_sel[1])]

# ===================== KPI STRIP =====================
st.title("SOPL 2024 – Interactive Dashboard")
st.caption("Deep-linked filters • House palette • PNG chart downloads • Derived efficiency metrics")

k1,k2,k3,k4 = st.columns(4)
k1.metric("Partner-sourced revenue (%)", safe_mean(flt["partner_sourced_revenue_pct"]))
k2.metric("Partner-influenced revenue (%)", safe_mean(flt["partner_influenced_revenue_pct"]))
k3.metric("Pipeline from partners (%)", safe_mean(flt["pipeline_from_partners_pct"]))
k4.metric("Time to first win (days)", safe_mean(flt["time_to_first_partner_win_days"], "{:.0f}"))

k5,k6,k7,k8 = st.columns(4)
k5.metric("Active partners (avg)", safe_mean(flt["num_active_partners"], "{:.0f}"))
k6.metric("Annual partner budget (USD)", f"${pd.to_numeric(flt['annual_partner_budget_usd'], errors='coerce').mean():,.0f}" if not flt.empty else "—")
k7.metric("Tooling spend (USD)", f"${pd.to_numeric(flt['tooling_spend_usd'], errors='coerce').mean():,.0f}" if not flt.empty else "—")
k8.metric("Enablement hrs / qtr", safe_mean(flt["enablement_hours_per_qtr"], "{:.0f}"))

k9,k10,k11,k12 = st.columns(4)
k9.metric("Sales alignment (1–5)", safe_mean(flt["sales_alignment_score"], "{:.2f}"))
k10.metric("Goal clarity (1–5)", safe_mean(flt["goal_setting_clarity_score"], "{:.2f}"))
k11.metric("Exec alignment (1–5)", safe_mean(flt["exec_alignment_score"], "{:.2f}"))
k12.metric("Program health (1–5)", safe_mean(flt["overall_program_health"], "{:.2f}"))

g1,g2 = st.columns(2)
g1.metric("Responses (after filters)", f"{len(flt):,}")
g2.metric("Total responses", f"{len(df):,}")

st.divider()

# ===================== DISTRIBUTIONS =====================
left, right = st.columns(2)
with left:
    # Industry mix
    tmp = flt["industry"].value_counts(normalize=True).mul(100).rename("Percent").reset_index()
    tmp.columns = ["industry","Percent"]
    chart = alt.Chart(tmp).mark_bar().encode(
        x=alt.X("Percent:Q", title="Percent of companies"),
        y=alt.Y("industry:N", sort="-x"),
        tooltip=[alt.Tooltip("industry:N", title="Industry"), alt.Tooltip("Percent:Q", format=".1f")],
    ).properties(height=280, title="Industry Mix (Filtered)")
    render_chart(chart, "industry_mix")

with right:
    # Program Maturity mix
    tmp = flt["program_maturity"].value_counts(normalize=True).mul(100).rename("Percent").reset_index()
    tmp.columns = ["program_maturity","Percent"]
    tmp["program_maturity"] = pd.Categorical(tmp["program_maturity"], categories=MATURITY_ORDER, ordered=True)
    chart = alt.Chart(tmp).mark_bar().encode(
        x=alt.X("Percent:Q", title="Percent of companies"),
        y=alt.Y("program_maturity:N", sort="-y"),
        tooltip=[alt.Tooltip("program_maturity:N", title="Maturity"), alt.Tooltip("Percent:Q", format=".1f")],
    ).properties(height=280, title="Program Maturity Mix")
    render_chart(chart, "maturity_mix")

st.divider()

# ===================== BOX PLOTS =====================
b1, b2 = st.columns(2)
with b1:
    d = flt[["partner_sourced_revenue_pct","revenue_band"]].dropna()
    d["revenue_band"] = pd.Categorical(d["revenue_band"], categories=REVENUE_ORDER, ordered=True)
    chart = alt.Chart(d).mark_boxplot().encode(
        x=alt.X("revenue_band:N", title="Revenue Band"),
        y=alt.Y("partner_sourced_revenue_pct:Q", title="Partner-sourced revenue (%)"),
        color=alt.Color("revenue_band:N", legend=None),
        tooltip=["revenue_band","partner_sourced_revenue_pct"]
    ).properties(height=320, title="Partner-Sourced % by Revenue Band")
    render_chart(chart, "sourced_by_revenue_band")

with b2:
    d = flt[["partner_influenced_revenue_pct","program_maturity"]].dropna()
    d["program_maturity"] = pd.Categorical(d["program_maturity"], categories=MATURITY_ORDER, ordered=True)
    chart = alt.Chart(d).mark_boxplot().encode(
        x=alt.X("program_maturity:N", title="Program Maturity"),
        y=alt.Y("partner_influenced_revenue_pct:Q", title="Partner-influenced revenue (%)"),
        color=alt.Color("program_maturity:N", legend=None),
        tooltip=["program_maturity","partner_influenced_revenue_pct"]
    ).properties(height=320, title="Partner-Influenced % by Maturity")
    render_chart(chart, "influenced_by_maturity")

st.divider()

# ===================== RELATIONSHIP EXPLORER =====================
st.subheader("Relationship Explorer (customizable)")

numeric_choices = [c for c in NUMERIC_COLS + [
    "pipeline_pct_per_partner","budget_per_partner",
    "tooling_per_partner","enablement_hours_per_partner",
    "sourced_to_influenced_ratio"
] if c in flt.columns]

with st.expander("Pick axes / color / bubble size"):
    x_sel = st.selectbox("X axis", numeric_choices,
                         index=numeric_choices.index("annual_partner_budget_usd") if "annual_partner_budget_usd" in numeric_choices else 0)
    y_sel = st.selectbox("Y axis", numeric_choices,
                         index=numeric_choices.index("partner_sourced_revenue_pct") if "partner_sourced_revenue_pct" in numeric_choices else 0)
    color_sel = st.selectbox("Color by", ["program_maturity","revenue_band","company_type","region"])
    size_sel = st.selectbox("Bubble size (optional)", [None,"partner_team_size","num_active_partners","employee_count"])

d = flt[["company_name","revenue_band","program_maturity","company_type", x_sel, y_sel] + ([size_sel] if size_sel else [])].dropna()
if not d.empty:
    enc = {
        "x": alt.X(f"{x_sel}:Q", title=x_sel.replace("_", " ").title()),
        "y": alt.Y(f"{y_sel}:Q", title=y_sel.replace("_", " ").title()),
        "color": alt.Color(f"{color_sel}:N", title=color_sel.replace("_"," ").title()),
        "tooltip": ["company_name","revenue_band","program_maturity","company_type", x_sel, y_sel],
    }
    if size_sel:
        enc["size"] = alt.Size(f"{size_sel}:Q", title=size_sel.replace("_"," ").title())
    chart = alt.Chart(d).mark_circle(opacity=0.85).encode(**enc).properties(height=380,
             title=f"{y_sel.replace('_',' ').title()} vs {x_sel.replace('_',' ').title()}")
    render_chart(chart, "relationship_explorer", helptext="If the button is disabled, PNG export isn’t available on this runtime.")
else:
    st.info("No data for the selected axes after filters.")

st.divider()

# ===================== COHORT SUMMARY TABLE =====================
metrics_for_cohort = [
    "partner_sourced_revenue_pct","partner_influenced_revenue_pct","pipeline_from_partners_pct",
    "time_to_first_partner_win_days","num_active_partners","annual_partner_budget_usd",
    "tooling_spend_usd","enablement_hours_per_qtr","sales_alignment_score",
    "goal_setting_clarity_score","exec_alignment_score","overall_program_health",
    "pipeline_pct_per_partner","budget_per_partner","tooling_per_partner","enablement_hours_per_partner",
    "sourced_to_influenced_ratio",
]
metrics_for_cohort = [m for m in metrics_for_cohort if m in flt.columns]
agg = flt.copy()
agg["revenue_band"] = pd.Categorical(agg["revenue_band"], categories=REVENUE_ORDER, ordered=True)
cohort = agg.groupby("revenue_band")[metrics_for_cohort].mean(numeric_only=True).reset_index()
st.markdown("**Cohort Means by Revenue Band**")
st.dataframe(cohort, use_container_width=True)

st.divider()

# ===================== CORRELATION HEATMAP =====================
st.subheader("Correlation (Pearson)")
corr_cols = [c for c in metrics_for_cohort if c in flt.columns]
if len(corr_cols) >= 2:
    c = flt[corr_cols].corr(numeric_only=True)
    corr = c.reset_index().melt("index")
    corr.columns = ["x","y","corr"]
    chart = alt.Chart(corr).mark_rect().encode(
        x=alt.X("x:N", title=""),
        y=alt.Y("y:N", title=""),
        color=alt.Color("corr:Q", title="r"),
        tooltip=[alt.Tooltip("x:N"), alt.Tooltip("y:N"), alt.Tooltip("corr:Q", format=".2f")],
    ).properties(height=360, title="Correlation Heatmap")
    render_chart(chart, "correlation_heatmap")
else:
    st.info("Not enough numeric columns for correlation.")

st.divider()

# ===================== LEADERBOARDS + TABLE + EXPORT =====================
st.subheader("Leaderboards")
lb1, lb2, lb3 = st.columns(3)
def topk(col, k=10, asc=False):
    if col not in flt.columns: return pd.DataFrame()
    d = flt[["company_name","revenue_band","program_maturity","company_type", col]].dropna()
    if d.empty: return d
    return d.sort_values(col, ascending=asc).head(k)

with lb1:
    st.markdown("**Top 10: Partner-sourced %**")
    st.dataframe(topk("partner_sourced_revenue_pct"), use_container_width=True, height=360)
with lb2:
    st.markdown("**Top 10: Pipeline % per Partner**")
    st.dataframe(topk("pipeline_pct_per_partner"), use_container_width=True, height=360)
with lb3:
    st.markdown("**Top 10: Program Health**")
    st.dataframe(topk("overall_program_health"), use_container_width=True, height=360)

with st.expander("Show filtered table"):
    st.dataframe(flt, use_container_width=True)

st.download_button("Download filtered CSV", flt.to_csv(index=False).encode("utf-8"),
                   file_name="sopl_filtered.csv", mime="text/csv")
