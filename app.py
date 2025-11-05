
import os
import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="SOPL 2024 – Interactive (Template)", page_icon="📊", layout="wide")

# ----------------- Config your schema here -----------------
CFG = {
    "id_col": "ResponseID",
    "cohort_filters": {
        "Revenue Band": "RevenueBand",
        "Industry": "Industry",
        "Company Size": "CompanySize",
        "Region": "Region",
        "Role Level": "RoleLevel",
    },
    "kpis": {
        "Increase focus on partnerships (%)": "KPI_IncreaseFocusPct",
        "Primary goal: revenue growth (%)": "KPI_PrimaryGoalRevenuePct",
        "Role is/might be at risk (%)": "KPI_RoleRiskPct",
        ">25% revenue from partnerships (%)": "KPI_RevenueGT25Pct",
        ">50% revenue from partnerships (%)": "KPI_RevenueGT50Pct",
        "Plan to expand team (%)": "KPI_TeamExpandPct",
    },
    "questions": {
        "Top Tech Priorities": "Q_TechPriority",
        "Account Mapping Priority": "Q_AccountMapping",
        "Budget Gate: Partner-sourced Rev": "Q_BudgetGatePartnerRev",
    },
    "template_path": "data/sopl_2024_required_template.csv",
}

@st.cache_data(show_spinner=False)
def load_csv(uploaded) -> pd.DataFrame:
    if uploaded is not None:
        return pd.read_csv(uploaded)
    # fallback to template bundled in repo
    if os.path.exists(CFG["template_path"]):
        return pd.read_csv(CFG["template_path"])
    return pd.DataFrame()

def percent_true(series: pd.Series) -> float:
    if series.empty:
        return 0.0
    if series.dtype.kind in "iufc":
        s = series.dropna().astype(float)
        if s.max() <= 1.0:
            return round(100.0 * s.mean(), 1)
        return round(s.mean(), 1)
    s = series.dropna().astype(str).str.strip().str.lower()
    tf = s.isin(["yes","true","y","1"])
    return round(100.0 * tf.mean(), 1)

def kpi_block(df: pd.DataFrame, kpis_map):
    cols = st.columns(3)
    items = list(kpis_map.items())
    for i, (label, col) in enumerate(items[:3]):
        val = percent_true(df[col]) if col in df.columns else float("nan")
        cols[i].metric(label, f"{val:.1f}%")
    if len(items) > 3:
        cols2 = st.columns(3)
        for j, (label, col) in enumerate(items[3:6]):
            val = percent_true(df[col]) if col in df.columns else float("nan")
            cols2[j].metric(label, f"{val:.1f}%")

def chart_category_distribution(df: pd.DataFrame, col: str, title: str):
    if col not in df.columns or df.empty:
        st.info(f"No data for **{title}**")
        return
    tmp = df[col].dropna().astype(str).value_counts(normalize=True).mul(100).rename("Percent").reset_index()
    tmp.rename(columns={"index": col}, inplace=True)
    chart = alt.Chart(tmp).mark_bar().encode(
        x=alt.X("Percent:Q", title="Percent of respondents"),
        y=alt.Y(f"{col}:N", sort="-x", title=""),
        tooltip=[col, alt.Tooltip("Percent:Q", format=".1f")]
    ).properties(height=280, title=title)
    st.altair_chart(chart, use_container_width=True)

def chart_stacked_share(df: pd.DataFrame, col: str, by: str, title: str):
    if col not in df.columns or by not in df.columns or df.empty:
        st.info(f"No data for **{title}**")
        return
    tmp = (
        df.groupby([by, col]).size().reset_index(name="n")
        .groupby(by)
        .apply(lambda g: g.assign(Percent=100*g["n"]/g["n"].sum()))
        .reset_index(drop=True)
    )
    chart = alt.Chart(tmp).mark_bar().encode(
        x=alt.X(f"{by}:N", title=by),
        y=alt.Y("Percent:Q", stack="normalize", title="Percent within cohort"),
        color=alt.Color(f"{col}:N", title=col),
        tooltip=[by, col, alt.Tooltip("Percent:Q", format=".1f")]
    ).properties(height=300, title=title)
    st.altair_chart(chart, use_container_width=True)

st.title("SOPL 2024 – Interactive Dashboard (Template)")
st.caption("This template ships with a small sample CSV. Replace it with your real SOPL CSV once ready.")

with st.sidebar:
    st.header("Data")
    uploaded_csv = st.file_uploader("Upload SOPL 2024 CSV", type=["csv"])
    df = load_csv(uploaded_csv)

    if df.empty:
        st.warning("No data found. Start with the bundled template: data/sopl_2024_template.csv")

    st.download_button(
        "Download CSV template",
        df.to_csv(index=False).encode("utf-8"),
        file_name="sopl_2024_template.csv",
        mime="text/csv"
    )

    if not df.empty:
        st.header("Filters")
        active = {}
        for label, col in CFG["cohort_filters"].items():
            if col not in df.columns:
                st.error(f"Missing column: {col}")
                continue
            options = sorted([x for x in df[col].dropna().astype(str).unique()])
            sel = st.multiselect(label, options=options, default=options)
            active[col] = sel

st.divider()

if 'df' not in locals() or df.empty:
    st.stop()

# Apply filters
filtered = df.copy()
for _, col in CFG["cohort_filters"].items():
    if col in filtered.columns:
        selected = st.session_state.get(col, None)
        # (Selections handled by the multiselects via their variable binding)
for label, col in CFG["cohort_filters"].items():
    if col in df.columns:
        chosen = st.session_state.get(label)  # handle state by label
        # fallback: infer from sidebar widget keys
        # but we passed explicit variables so Streamlit manages automatically
for label, col in CFG["cohort_filters"].items():
    # fetch chosen values from the multiselects (keys are defaulted to label)
    pass

# Re-read chosen values properly
with st.sidebar:
    user_choices = {}
    for label, col in CFG["cohort_filters"].items():
        if col in df.columns:
            # Streamlit stores the multiselect under a key equal to its label
            user_choices[col] = st.session_state.get(label, [])

for col, choices in user_choices.items():
    if choices:
        filtered = filtered[filtered[col].astype(str).isin(choices)]

# KPIs
top_l, top_r = st.columns([2,1])
with top_l:
    st.subheader("Key Performance Indicators")
    kpi_block(filtered, CFG["kpis"])

with top_r:
    st.subheader("At a glance")
    st.metric("Responses (after filters)", f"{len(filtered):,}")
    st.metric("Total responses", f"{len(df):,}")

st.divider()

left, right = st.columns(2)
with left:
    chart_category_distribution(filtered, CFG["questions"]["Top Tech Priorities"], "Top Tech Priorities")
with right:
    chart_stacked_share(filtered, CFG["questions"]["Top Tech Priorities"], CFG["cohort_filters"]["Revenue Band"], "Tech Priorities by Revenue Band")

with st.expander("Show filtered table"):
    st.dataframe(filtered, use_container_width=True)
