import streamlit as st
import pandas as pd
import numpy as np

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="UIDAI Intelligence Dashboard",
    page_icon="🆔",
    layout="wide"
)

# ===================== CUSTOM STYLING =====================
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    color: #0B5394;
}
.sub-title {
    font-size: 18px;
    color: #555;
}
.section {
    padding-top: 20px;
    padding-bottom: 10px;
}
.kpi {
    background-color: #F5F7FA;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ===================== DATA LOADING =====================
@st.cache_data
def load_data():
    demo_files = [
        "api_data_aadhar_demographic_0_500000.csv",
        "api_data_aadhar_demographic_500000_1000000.csv",
        "api_data_aadhar_demographic_1000000_1500000.csv",
        "api_data_aadhar_demographic_1500000_2000000.csv",
        "api_data_aadhar_demographic_2000000_2071700.csv"
    ]

    bio_files = [
        "api_data_aadhar_biometric_0_500000.csv",
        "api_data_aadhar_biometric_500000_1000000.csv",
        "api_data_aadhar_biometric_1000000_1500000.csv",
        "api_data_aadhar_biometric_1500000_1861108.csv"
    ]

    demo = pd.concat([pd.read_csv(f) for f in demo_files], ignore_index=True)
    bio = pd.concat([pd.read_csv(f) for f in bio_files], ignore_index=True)

    return demo, bio

demo, bio = load_data()

for df in [demo, bio]:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['month'] = df['date'].dt.to_period("M").astype(str)

# ===================== HEADER =====================
st.markdown('<div class="main-title">UIDAI Life-Event & Demographic Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Policy-ready insights from Aadhaar demographic & biometric signals</div>', unsafe_allow_html=True)
st.markdown("---")

# ===================== SIDEBAR =====================
st.sidebar.title("🔍 Controls")
state = st.sidebar.selectbox(
    "Select State",
    ["All"] + sorted(demo['state'].dropna().unique())
)

if state != "All":
    demo_f = demo[demo['state'] == state]
    bio_f = bio[bio['state'] == state]
else:
    demo_f = demo.copy()
    bio_f = bio.copy()

# ===================== KPI SUMMARY =====================
st.markdown("## 📊 Key Summary Indicators")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Records", f"{len(demo_f):,}")
k2.metric("Active Districts", demo_f['district'].nunique())
k3.metric("States Covered", demo_f['state'].nunique())
k4.metric("Biometric Updates", f"{bio_f.shape[0]:,}")

st.markdown("---")

# ===================== TEMPORAL ANALYTICS =====================
st.markdown("## 📈 Life-Event Trends Over Time")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 👶 Child Enrolments (Proxy)")
    st.line_chart(demo_f.groupby("month")["demo_age_5_17"].sum())

with c2:
    st.markdown("### 🎒 School-Age Enrolments")
    st.line_chart(demo_f.groupby("month")["demo_age_5_17"].sum())

with c3:
    st.markdown("### 🧑 Adult Biometric Updates")
    st.line_chart(bio_f.groupby("month")["bio_age_17_"].sum())

st.markdown("---")

# ===================== DISTRICT RISK =====================
st.markdown("## ⚠️ District Life-Event Pressure Index")

district_scores = demo_f.groupby("district").agg({
    "demo_age_5_17": "sum",
    "demo_age_17_": "sum"
}).reset_index()

district_scores["Life_Event_Pressure"] = (
    district_scores["demo_age_5_17"] +
    district_scores["demo_age_17_"]
)

q1, q2 = district_scores["Life_Event_Pressure"].quantile([0.33, 0.66])

district_scores["Risk_Level"] = np.where(
    district_scores["Life_Event_Pressure"] >= q2, "High",
    np.where(district_scores["Life_Event_Pressure"] >= q1, "Medium", "Low")
)

st.dataframe(
    district_scores.sort_values("Life_Event_Pressure", ascending=False),
    use_container_width=True
)

# ===================== TOP DISTRICTS =====================
st.markdown("## 🚨 Top 10 High-Pressure Districts")

top10 = district_scores.sort_values(
    "Life_Event_Pressure", ascending=False
).head(10)

st.bar_chart(top10.set_index("district")["Life_Event_Pressure"])

# ===================== POLICY INSIGHTS =====================
st.markdown("## 🧠 Automated Policy Recommendations")

if st.button("Generate Insights"):
    st.success("Policy Insights Generated")

    if (district_scores["Life_Event_Pressure"] == 0).any():
        st.write("• Zero-activity districts detected — audit data pipelines.")

    if district_scores["Life_Event_Pressure"].max() > district_scores["Life_Event_Pressure"].mean() * 3:
        st.write("• Extreme enrolment spikes — deploy mobile Aadhaar units.")

    st.write("• High-risk districts require staffing and infrastructure prioritization.")
    st.write("• Temporal signals enable proactive enrolment planning.")

st.markdown("---")
st.caption("© UIDAI Hackathon | Data-Driven Governance Intelligence")
