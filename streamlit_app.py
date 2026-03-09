import streamlit as st
import pandas as pd

# 1. Page Config & Professional Dashboard Styling
st.set_page_config(page_title="Dual Mode Savings", page_icon="⛽", layout="wide")
st.markdown("""
    <style>
    /* Balanced padding to ensure shadows breathe without forcing a scroll */
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    
    /* BIG Sidebar Title */
    .sidebar-title {
        font-size: 2.8rem !important; 
        font-weight: 900; 
        line-height: 1.0;
        margin-bottom: 1.2rem; 
        color: #1a7fa3;
        text-transform: uppercase;
        letter-spacing: -1px;
    }

    /* THE FLASHY RESULT (Optimized spacing for shadows) */
    .flashy-result {
        background: linear-gradient(135deg, #29B5E8 0%, #1a7fa3 100%);
        color: white; 
        padding: 40px 10px; 
        border-radius: 18px; 
        text-align: center; 
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        margin-bottom: 45px; /* Fixed: Clears the shadow from elements below */
        border: 2px solid rgba(255,255,255,0.2);
    }
    .flash_label { font-size: 1.3rem; text-transform: uppercase; letter-spacing: 5px; opacity: 0.9; margin: 0; }
    .flash_val { 
        font-size: 8.5rem !important; 
        font-weight: 900; margin: -10px 0; line-height: 1; 
        text-shadow: 4px 4px 20px rgba(0,0,0,0.3); 
    }
    .flash_unit { font-size: 1.6rem; font-weight: 700; margin: 0; letter-spacing: 2px; }

    /* UI Refinement */
    .stMetric { padding: 5px !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar - Branding & Controls
st.sidebar.markdown('<p class="sidebar-title">DUAL MODE<br>FUEL SAVINGS</p>', unsafe_allow_html=True)
st.sidebar.header("🕹️ Controls")
daily_miles = st.sidebar.slider("Daily Commute (Miles)", 0, 200, 30)
days_per_week = st.sidebar.slider("Days Driven per Week", 1, 7, 5)
fuel_price = st.sidebar.number_input("Fuel Price (AUD/Litre)", value=1.85)
st.sidebar.divider()
curr_l100 = st.sidebar.number_input("Current Car (L/100km)", value=12.0)
new_l100 = st.sidebar.number_input("New Dual Mode (L/100km)", value=5.5)

# 3. Logic & Hybrid Unit Conversion (1 mile = 1.60934 km)
ann_miles = daily_miles * days_per_week * 52
ann_km = ann_miles * 1.60934
curr_ann = (ann_km / 100) * curr_l100 * fuel_price
new_ann = (ann_km / 100) * new_l100 * fuel_price
savings = curr_ann - new_ann

# 4. The Main Dashboard Hero
st.markdown(f"""
    <div class="flashy-result">
        <p class="flash_label">Estimated Annual Savings</p>
        <h1 class="flash_val">${savings:,.2f}</h1>
        <p class="flash_unit">AUD PER YEAR</p>
    </div>
    """, unsafe_allow_html=True)

# 5. Visual Insights Layout
col_chart, col_stats = st.columns([2, 1], gap="large")

with col_chart:
    st.subheader("Cost Comparison")
    chart_df = pd.DataFrame({
        "Vehicle": ["Current ICE", "New Dual Mode"],
        "Annual Cost": [curr_ann, new_ann]
    })
    st.bar_chart(chart_df, x="Vehicle", y="Annual Cost", color="Vehicle")

with col_stats:
    st.subheader("Key Metrics")
    st.metric("Current Monthly", f"${(curr_ann/12):,.2f}")
    st.metric("New Monthly", f"${(new_ann/12):,.2f}", delta=f"-${(savings/12):,.2f}")
    st.metric("Annual Distance", f"{ann_miles:,} Mi")
    st.success(f"**{((curr_ann-new_ann)/curr_ann)*100:.1f}%** cheaper than your current ride!")
