import streamlit as st
import pandas as pd

# 1. Page Config & Professional Dashboard Styling
st.set_page_config(page_title="Dual Mode Savings", page_icon="⛽", layout="wide")
st.markdown("""
    <style>
    .block-container { padding-top: 3.5rem; padding-bottom: 1rem; }
    .sidebar-title {
        font-size: 2.8rem !important; 
        font-weight: 900; 
        line-height: 1.0;
        margin-bottom: 1.2rem; 
        color: #1a7fa3;
        text-transform: uppercase;
        letter-spacing: -1px;
    }
    .flashy-result {
        background: linear-gradient(135deg, #29B5E8 0%, #1a7fa3 100%);
        color: white; 
        padding: 40px 10px; 
        border-radius: 18px; 
        text-align: center; 
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        margin-bottom: 45px;
        border: 2px solid rgba(255,255,255,0.2);
    }
    .flash_label { font-size: 1.3rem; text-transform: uppercase; letter-spacing: 5px; opacity: 0.9; margin: 0; }
    .flash_val { 
        font-size: 8.5rem !important; 
        font-weight: 900; margin: -10px 0; line-height: 1; 
        text-shadow: 4px 4px 20px rgba(0,0,0,0.3); 
    }
    .flash_unit { font-size: 1.6rem; font-weight: 700; margin: 0; letter-spacing: 2px; }
    .stMetric { padding: 5px !important; }
    .disclaimer-box {
        background-color: #f0f7ff;
        border-left: 4px solid #29B5E8;
        padding: 10px 16px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #444;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - Branding & Mode Selector
st.sidebar.markdown('<p class="sidebar-title">DUAL MODE<br>FUEL SAVINGS</p>', unsafe_allow_html=True)

mode = st.sidebar.radio("Comparison Mode", ["ICE to PHEV", "ICE to EV"], horizontal=True)
st.sidebar.divider()

st.sidebar.header("🕹️ Controls")

unit = st.sidebar.radio("Distance Unit", ["km.", "mi."], horizontal=True)
if unit == "mi.":
    daily_miles = st.sidebar.slider("Daily Commute (mi.)", 0, 200, 30)
else:
    daily_km_input = st.sidebar.slider("Daily Commute (km.)", 0, 320, 48)
    daily_miles = daily_km_input / 1.60934

days_per_week = st.sidebar.slider("Days Driven per Week", 1, 7, 5)

fuel_price = st.sidebar.number_input("Fuel Price (AUD/Litre)", value=1.85, step=0.01)
st.sidebar.caption("Default: ABS/DISER national average. Enter your local price for accuracy.")

st.sidebar.divider()

curr_l100 = st.sidebar.number_input("Current ICE Car (L/100km)", value=12.0)
st.sidebar.caption("Tip: Check your Green Vehicle Guide rating or fuel receipt average.")

if mode == "ICE to PHEV":
    st.sidebar.header("⚡ PHEV Specs")
    new_l100 = st.sidebar.number_input("New Dual Mode PHEV (L/100km)", value=5.5)
    st.sidebar.caption("Default based on Green Vehicle Guide PHEV average.")
else:
    st.sidebar.header("🔋 EV Specs")
    ev_kw100 = st.sidebar.slider("EV Consumption (kWh/100km)", 13, 25, 18)
    st.sidebar.caption("Range: 13 kWh (small hatch) to 25 kWh (large SUV). Source: Green Vehicle Guide.")
    elec_price = st.sidebar.number_input("Electricity Price (AUD/kWh)", value=0.30, step=0.01)
    st.sidebar.caption("Default: AEMO national average. Enter your plan's rate for accuracy.")

# 3. Logic & Unit Conversion
ann_miles = daily_miles * days_per_week * 52
ann_km = ann_miles * 1.60934
curr_ann = (ann_km / 100) * curr_l100 * fuel_price

if mode == "ICE to PHEV":
    new_ann = (ann_km / 100) * new_l100 * fuel_price
    savings = curr_ann - new_ann
    new_label = "New Dual Mode"
else:
    new_ann = (ann_km / 100) * ev_kw100 * elec_price
    savings = curr_ann - new_ann
    new_label = "Full EV"

# 4. Disclaimer Banner
st.markdown("""
    <div class="disclaimer-box">
    ⚠️ <strong>General Estimate Only.</strong> This calculator provides indicative figures and does not 
    constitute financial advice. Results are based on user-provided inputs and national averages. 
    Individual results will vary. Not a substitute for professional financial or automotive advice.
    </div>
    """, unsafe_allow_html=True)

# 5. ICE to EV segment warning
if mode == "ICE to EV":
    st.info("ℹ️ For accurate comparisons, compare vehicles of the same segment (e.g. small hatch vs. small hatch). Mixing segments will produce misleading results.")

# 6. The Main Dashboard Hero
st.markdown(f"""
    <div class="flashy-result">
        <p class="flash_label">Estimated Annual Savings</p>
        <h1 class="flash_val">${savings:,.2f}</h1>
        <p class="flash_unit">INDICATIVE ESTIMATE — AUD PER YEAR</p>
    </div>
    """, unsafe_allow_html=True)

# 7. Visual Insights Layout
col_chart, col_stats = st.columns([2, 1], gap="large")

with col_chart:
    st.subheader("Cost Comparison")
    chart_df = pd.DataFrame({
        "Vehicle": ["Current ICE", new_label],
        "Annual Cost": [curr_ann, new_ann]
    })
    st.bar_chart(chart_df, x="Vehicle", y="Annual Cost", color="Vehicle")

with col_stats:
    st.subheader("Key Metrics")
    st.metric("Current Monthly", f"${(curr_ann/12):,.2f}")
    st.metric(f"{new_label} Monthly", f"${(new_ann/12):,.2f}", delta=f"-${(savings/12):,.2f}")
    if unit == "mi.":
        st.metric("Annual Distance", f"{ann_miles:,.0f} mi.")
    else:
        st.metric("Annual Distance", f"{ann_km:,.0f} km.")
    if mode == "ICE to EV":
        st.metric("EV Energy Cost", f"${new_ann:,.2f}/yr")
    st.success(f"**{((curr_ann - new_ann) / curr_ann) * 100:.1f}%** cheaper than your current ride!")

# 8. Assumptions & Data Sources Expander
with st.expander("📋 Assumptions & Data Sources"):
    st.markdown(f"""
    **General**
    - All figures are indicative estimates based on the inputs provided and the national averages listed below.
    - This tool is classified as a *Generic Calculator* and does not constitute financial, legal, or automotive advice.
    - Results assume consistent driving behaviour and do not account for traffic, terrain, vehicle age, or maintenance costs.

    **Distance & Usage**
    - Annual distance calculated as: Daily Commute × Days per Week × 52 weeks.
    - Unit conversion: 1 mile = 1.60934 km.

    **Fuel Price**
    - Default fuel price: **$1.85 AUD/Litre** — ABS/DISER national average.
    - Source: [Australian Bureau of Statistics](https://www.abs.gov.au) | [DISER](https://www.energy.gov.au)

    **ICE Fuel Consumption**
    - Default ICE consumption: **12.0 L/100km** — Green Vehicle Guide national average for passenger vehicles.
    - Source: [Green Vehicle Guide](https://www.greenvehicleguide.gov.au)

    {"**PHEV Consumption** — Default: **5.5 L/100km** — Green Vehicle Guide PHEV average. Source: [Green Vehicle Guide](https://www.greenvehicleguide.gov.au)" if mode == "ICE to PHEV" else ""}

    {"**EV Electricity Consumption** — Range: **13–25 kWh/100km** (small hatch to large SUV). Source: [Green Vehicle Guide](https://www.greenvehicleguide.gov.au)" if mode == "ICE to EV" else ""}

    {"**Electricity Price** — Default: **$0.30 AUD/kWh** — AEMO national average. Source: [AEMO](https://www.aemo.com.au)" if mode == "ICE to EV" else ""}

    **Vehicle Segment Note**
    - For legally compliant comparisons under ACL guidelines, always compare vehicles of equivalent segments
      (e.g. small hatch vs. small hatch). Refer to the Green Vehicle Guide for segment classifications.

    **Note:** Default values should be reviewed periodically as fuel and electricity prices change.
    """)

# 9. Footer
st.markdown("---")
st.caption("General estimates only. Not financial advice. Data sources: ABS, DISER, AEMO, Green Vehicle Guide.")
