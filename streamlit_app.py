import streamlit as st
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Dual Mode Savings Calculator",
    page_icon="🚗",
    layout="wide"
)

# 2. Refined UI Styling (Added title margin)
st.markdown("""
    <style>
    /* Standardizes the top padding */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    
    /* Adds breathing room specifically for the title so it isn't cut off */
    h1 { margin-top: 1.5rem !important; margin-bottom: 1rem !important; }
    
    /* Style the metric cards */
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Tighter spacing between standard blocks */
    [data-testid="stVerticalBlock"] { gap: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# 3. Header
st.title("🚗 Dual Mode Fuel Savings Calculator")

# 4. Sidebar Inputs
with st.sidebar:
    st.header("📍 Drive & Fuel")
    daily_km = st.slider("Daily Commute (km)", 5, 300, 50)
    fuel_price = st.number_input("Fuel Price (AUD/L)", value=2.10, step=0.01)
    ice_cons = st.number_input("ICE Car (L/100km)", value=9.5, step=0.1)
    st.divider()
    st.header("⚡ DM Specs")
    dm_cons = st.number_input("DM Tech (L/100km)", value=1.5, step=0.1)

# 5. Calculations
ann_km = daily_km * 365
ice_cost = (ann_km / 100) * ice_cons * fuel_price
dm_cost = (ann_km / 100) * dm_cons * fuel_price
ann_sav = ice_cost - dm_cost
mon_sav = ann_sav / 12
litres = ann_sav / fuel_price

# 6. Main Dashboard Area
col_m1, col_m2 = st.columns(2)
col_m1.metric("Monthly Savings", f"${mon_sav:,.2f}")
col_m2.metric("Annual Savings", f"${ann_sav:,.2f}")

st.divider()

# 7. Side-by-Side Chart and Result (Scroll-free layout)
col_chart, col_result = st.columns([1.5, 1])

with col_chart:
    st.write("📊 **Cost Comparison**")
    chart_data = pd.DataFrame({
        'Vehicle': ['ICE', 'DM Tech'],
        'Cost (AUD)': [round(ice_cost, 2), round(dm_cost, 2)]
    })
    st.bar_chart(chart_data, x='Vehicle', y='Cost (AUD)', height=280)

with col_result:
    st.write("💡 **The Result**")
    st.success(f"""
    **{litres:.0f} Litres** saved yearly!
    
    That's **{litres/50:.0f} full tanks**
    of gas back in your pocket.
    """)