import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Dual Mode Savings", page_icon="⛽", layout="wide")

# 2. SVG Icons
SVG_CAR = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1a7fa3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><path d="M5 17H3a2 2 0 0 1-2-2v-4l2.38-4.76A2 2 0 0 1 5.17 5h13.66a2 2 0 0 1 1.79 1.1L23 11v4a2 2 0 0 1-2 2h-2"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="16.5" cy="17.5" r="2.5"/></svg>"""
SVG_BOLT = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1a7fa3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>"""
SVG_PRINT = """<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>"""
SVG_CONTROLS = """<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1a7fa3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/><circle cx="8" cy="6" r="2" fill="white"/><circle cx="16" cy="12" r="2" fill="white"/><circle cx="10" cy="18" r="2" fill="white"/></svg>"""

# 3. Data
ICE_SEGMENTS = {
    'Average Small SUV': 7.5,
    'Average Hatchback': 6.2,
    'Average Sedan': 6.8,
    'Average Ute (Diesel)': 9.5,
}

BYD_EV_MODELS = {
    'Atto 3': 16.0,
    'Dolphin': 12.6,
    'Seal': 14.4,
    'Shark 6': 18.5,
}

BYD_PHEV_MODELS = {
    'Seal DM-i': 4.9,
    'Sealion 6 DM-i': 5.5,
    'Tang DM-i': 6.0,
    'Shark 6 PHEV': 7.0,
}

# 4. CSS
st.markdown("""
<style>
@media print {
    [data-testid="stSidebar"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    header, .stButton, .screen-only,
    .flashy-result, .disclaimer-box,
    .info-box, .stBarChart { display: none !important; }
    .print-summary { display: block !important; }
    .assumptions-section { display: block !important; }
    .block-container { padding: 0 !important; }
}
@media screen { .print-summary { display: none !important; } }

.block-container { padding-top: 3.5rem; padding-bottom: 1rem; }
.sidebar-title { font-size: 2.8rem !important; font-weight: 900; line-height: 1.0; margin-bottom: 1.2rem; color: #1a7fa3; text-transform: uppercase; letter-spacing: -1px; }
.flashy-result { background: linear-gradient(135deg, #29B5E8 0%, #1a7fa3 100%); color: white; padding: 40px 10px; border-radius: 18px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.2); margin-bottom: 45px; border: 2px solid rgba(255,255,255,0.2); }
.flash_label { font-size: 1.3rem; text-transform: uppercase; letter-spacing: 5px; opacity: 0.9; margin: 0; }
.flash_val { font-size: 8.5rem !important; font-weight: 900; margin: -10px 0; line-height: 1; text-shadow: 4px 4px 20px rgba(0,0,0,0.3); }
.flash_unit { font-size: 1.6rem; font-weight: 700; margin: 0; letter-spacing: 2px; }
.disclaimer-box { background-color: #f0f7ff; border-left: 4px solid #29B5E8; padding: 10px 16px; border-radius: 4px; font-size: 0.85rem; color: #444; margin-bottom: 1rem; }
.info-box { background:#e8f4fb; border-left:4px solid #29B5E8; padding:10px 16px; border-radius:4px; font-size:0.85rem; color:#1a5575; margin-bottom:1rem; }
.segment-header { font-size: 0.7rem; font-weight: 700; letter-spacing: 3px; color: #888; text-transform: uppercase; margin: 0.5rem 0 0.75rem; display: flex; align-items: center; gap: 4px; }

/* Radio as Cards */
div[data-testid="stRadio"] > div[role="radiogroup"] { display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 10px !important; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label { background: white; border: 1.5px solid #e0eaf3; border-radius: 12px; padding: 14px 16px; cursor: pointer; transition: border-color 0.15s; display: flex !important; align-items: center !important; gap: 8px; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { border-color: #29B5E8; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) { background: linear-gradient(135deg, #0a2a5e, #0d3d7a); border-color: #0a2a5e; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p { color: white !important; }
div[role="radiogroup"] > label > div:first-child { display: none !important; }

/* Badges */
.badge { display: inline-block; font-size: 0.6rem; font-weight: 700; padding: 2px 7px; border-radius: 4px; margin-left: 6px; vertical-align: middle; letter-spacing: 1px; text-transform: uppercase; }
.badge-c { background: #e8f0fe; color: #1a5fa3; }
.badge-s { background: #e6f4ea; color: #137333; }
.badge-v { background: #fce8b2; color: #b06000; }

/* Metric Cards */
.metric-card { background: #f8fafc; border: 1px solid #e0eaf3; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; }
.metric-label { font-size: 0.82rem; color: #666; margin: 0 0 4px; }
.metric-value { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; margin: 0; }
.metric-sub { font-size: 0.72rem; color: #999; margin: 3px 0 0; }
.metric-delta { font-size: 0.82rem; color: #c0392b; margin: 2px 0 0; font-weight: 600; }

/* Assumptions */
.assumptions-section { background: #f8fafc; border: 1px solid #e0eaf3; border-radius: 10px; padding: 24px 28px; margin-top: 2rem; }
.assumptions-title { font-size: 0.75rem; font-weight: 700; color: #1a7fa3; text-transform: uppercase; letter-spacing: 2px; margin: 0 0 16px; }

/* Print Summary */
.print-summary { font-family: Arial, sans-serif; padding: 20px; }
.print-summary h1 { font-size: 18pt; color: #1a7fa3; }
.print-summary table { width: 100%; border-collapse: collapse; margin: 12px 0; }
.print-summary td, .print-summary th { border: 1px solid #ddd; padding: 8px 12px; font-size: 10pt; }
.print-summary th { background: #f0f7ff; font-weight: bold; }
.print-disclaimer { background: #f0f7ff; border-left: 3px solid #29B5E8; padding: 10px 14px; font-size: 9pt; margin: 12px 0; }
</style>
""", unsafe_allow_html=True)

# 5. Sidebar
st.sidebar.markdown('<p class="sidebar-title">DUAL MODE<br>FUEL SAVINGS</p>', unsafe_allow_html=True)
mode = st.sidebar.radio("Comparison Mode", ["ICE to PHEV", "ICE to EV"], horizontal=True)
st.sidebar.divider()
st.sidebar.markdown(f'{SVG_CONTROLS} **Controls**', unsafe_allow_html=True)

unit = st.sidebar.radio("Distance Unit", ["km.", "mi."], horizontal=True)
if unit == "mi.":
    daily_miles = st.sidebar.slider("Daily Commute (mi.)", 0, 200, 30)
else:
    daily_km_input = st.sidebar.slider("Daily Commute (km.)", 0, 320, 48)
    daily_miles = daily_km_input / 1.60934

days_per_week = st.sidebar.slider("Days Driven per Week", 1, 7, 5)
fuel_price = st.sidebar.number_input("Fuel Price (AUD/Litre)", value=1.85, step=0.01)
st.sidebar.caption("Default: ABS/DISER national average. Enter your local price for accuracy.")

elec_price = 0.30
if mode == "ICE to EV":
    st.sidebar.divider()
    elec_price = st.sidebar.number_input("Electricity Price (AUD/kWh)", value=0.30, step=0.01)
    st.sidebar.caption("Default: AEMO national average. Enter your plan's rate for accuracy.")

# 6. Disclaimer
st.markdown("""
<div class="disclaimer-box">
<strong>General Estimate Only.</strong> This calculator provides indicative figures and does not constitute financial advice. Results are based on user-provided inputs and national averages. Individual results will vary. Not a substitute for professional financial or automotive advice.
</div>
""", unsafe_allow_html=True)

if mode == "ICE to EV":
    st.markdown("""
    <div class="info-box">
    For accurate comparisons, compare vehicles of the same segment (e.g. small hatch vs. small hatch). Mixing segments will produce misleading results.
    </div>
    """, unsafe_allow_html=True)

# 7. Card Selectors
col_ice, col_byd = st.columns(2)

with col_ice:
    st.markdown(f'<p class="segment-header">{SVG_CAR} Current ICE Segment</p>', unsafe_allow_html=True)
    ice_options = [f"{k}  ·  {v} L/100km" for k, v in ICE_SEGMENTS.items()]
    ice_selection = st.radio("ice", ice_options, index=2, label_visibility="collapsed", key="ice_radio")
    selected_ice_name = list(ICE_SEGMENTS.keys())[ice_options.index(ice_selection)]
    ice_l100 = ICE_SEGMENTS[selected_ice_name]

with col_byd:
    if mode == "ICE to PHEV":
        st.markdown(f'<p class="segment-header">{SVG_BOLT} Target BYD PHEV Model</p>', unsafe_allow_html=True)
        phev_options = [f"{k}  ·  {v} L/100km" for k, v in BYD_PHEV_MODELS.items()]
        byd_selection = st.radio("phev", phev_options, index=0, label_visibility="collapsed", key="phev_radio")
        selected_byd_name = list(BYD_PHEV_MODELS.keys())[phev_options.index(byd_selection)]
        byd_consumption = BYD_PHEV_MODELS[selected_byd_name]
        byd_unit_label = "L/100km"
    else:
        st.markdown(f'<p class="segment-header">{SVG_BOLT} Target BYD EV Model</p>', unsafe_allow_html=True)
        ev_options = [f"{k}  ·  {v} kWh/100km" for k, v in BYD_EV_MODELS.items()]
        byd_selection = st.radio("ev", ev_options, index=1, label_visibility="collapsed", key="ev_radio")
        selected_byd_name = list(BYD_EV_MODELS.keys())[ev_options.index(byd_selection)]
        byd_consumption = BYD_EV_MODELS[selected_byd_name]
        byd_unit_label = "kWh/100km"

# 8. Calculations
ann_miles = daily_miles * days_per_week * 52
ann_km = ann_miles * 1.60934
curr_ann = (ann_km / 100) * ice_l100 * fuel_price

if mode == "ICE to PHEV":
    new_ann = (ann_km / 100) * byd_consumption * fuel_price
else:
    new_ann = (ann_km / 100) * byd_consumption * elec_price

savings = curr_ann - new_ann
pct_saving = ((curr_ann - new_ann) / curr_ann) * 100 if curr_ann > 0 else 0
new_label = f"BYD {selected_byd_name}"
ann_dist_display = f"{ann_miles:,.0f} mi." if unit == "mi." else f"{ann_km:,.0f} km."

# 9. Hero
st.markdown(f"""
<div class="flashy-result">
    <p class="flash_label">Estimated Annual Savings</p>
    <h1 class="flash_val">${savings:,.2f}</h1>
    <p class="flash_unit">INDICATIVE ESTIMATE — AUD PER YEAR</p>
</div>
""", unsafe_allow_html=True)

# 10. Chart + Key Metrics
col_chart, col_stats = st.columns([2, 1], gap="large")

with col_chart:
    st.subheader("Cost Comparison")
    chart_df = pd.DataFrame({
        "Vehicle": [selected_ice_name, new_label],
        "Annual Cost (AUD)": [round(curr_ann, 2), round(new_ann, 2)]
    })
    st.bar_chart(chart_df, x="Vehicle", y="Annual Cost (AUD)", color="Vehicle")

with col_stats:
    st.subheader("Key Metrics")
    st.markdown(f"""
    <div class="metric-card">
        <p class="metric-label">Current Monthly <span class="badge badge-c">C · Cost</span></p>
        <p class="metric-value">${(curr_ann/12):,.2f}</p>
        <p class="metric-sub">{selected_ice_name} · {ice_l100} L/100km</p>
    </div>
    <div class="metric-card">
        <p class="metric-label">{new_label} Monthly <span class="badge badge-s">S · Savings</span></p>
        <p class="metric-value">${(new_ann/12):,.2f}</p>
        <p class="metric-delta">↓ −${(savings/12):,.2f}/mo vs ICE</p>
        <p class="metric-sub">{byd_consumption} {byd_unit_label}</p>
    </div>
    <div class="metric-card">
        <p class="metric-label">Annual Distance</p>
        <p class="metric-value">{ann_dist_display}</p>
        <p class="metric-sub">{days_per_week} days/week × 52 weeks</p>
    </div>
    <div class="metric-card" style="background:#e6f4ea;border-color:#b7dfbf;">
        <p class="metric-label" style="color:#137333;">Estimated Value <span class="badge badge-v">V · Value</span></p>
        <p class="metric-value" style="color:#137333;">{pct_saving:.1f}% cheaper</p>
        <p class="metric-sub" style="color:#137333;">vs {selected_ice_name}</p>
    </div>
    """, unsafe_allow_html=True)

# 11. Print Button
st.markdown(f"""
<div style="margin: 1.5rem 0 0.5rem;">
    <button onclick="window.print()" style="background: linear-gradient(135deg, #29B5E8, #1a7fa3); color: white; border: none; padding: 10px 24px; border-radius: 8px; font-size: 0.88rem; font-weight: 600; cursor: pointer; letter-spacing: 0.5px; display:inline-flex; align-items:center;">
        {SVG_PRINT} Print Summary
    </button>
</div>
""", unsafe_allow_html=True)

# 12. Always-Visible Assumptions Section
phev_row = f"""<tr><td style="padding:7px 10px;border:1px solid #e0eaf3;">PHEV Consumption</td><td style="padding:7px 10px;border:1px solid #e0eaf3;">BYD {selected_byd_name}: <strong>{byd_consumption} L/100km</strong></td><td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></td></tr>""" if mode == "ICE to PHEV" else ""
ev_rows = f"""
<tr><td style="padding:7px 10px;border:1px solid #e0eaf3;">EV Consumption</td><td style="padding:7px 10px;border:1px solid #e0eaf3;">BYD {selected_byd_name}: <strong>{byd_consumption} kWh/100km</strong></td><td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></td></tr>
<tr><td style="padding:7px 10px;border:1px solid #e0eaf3;">Electricity Price</td><td style="padding:7px 10px;border:1px solid #e0eaf3;"><strong>${elec_price:.2f} AUD/kWh</strong> (user-set; default: AEMO national avg.)</td><td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.aemo.com.au" target="_blank">AEMO</a></td></tr>
""" if mode == "ICE to EV" else ""

st.markdown(f"""
<div class="assumptions-section">
    <p class="assumptions-title">Assumptions & Data Sources</p>
    <p style="font-size:0.82rem;color:#555;margin:0 0 14px;">All figures are indicative estimates. This tool is classified as a <em>Generic Calculator</em> and does not constitute financial, legal, or automotive advice. Results assume consistent driving behaviour and do not account for traffic, terrain, vehicle age, or maintenance costs.</p>
    <table style="width:100%;border-collapse:collapse;font-size:0.8rem;">
        <thead>
            <tr style="background:#e8f0fb;">
                <th style="text-align:left;padding:8px 10px;border:1px solid #d0dff0;font-weight:600;">Parameter</th>
                <th style="text-align:left;padding:8px 10px;border:1px solid #d0dff0;font-weight:600;">Value Used</th>
                <th style="text-align:left;padding:8px 10px;border:1px solid #d0dff0;font-weight:600;">Source</th>
            </tr>
        </thead>
        <tbody>
            <tr><td style="padding:7px 10px;border:1px solid #e0eaf3;">Annual Distance</td><td style="padding:7px 10px;border:1px solid #e0eaf3;">Daily Commute × {days_per_week} days/week × 52 weeks</td><td style="padding:7px 10px;border:1px solid #e0eaf3;">User input</td></tr>
            <tr><td style="padding:7px 10px;border:1px solid #e0eaf3;">Fuel Price</td><td style="padding:7px 10px;border:1px solid #e0eaf3;"><strong>${fuel_price:.2f} AUD/Litre</strong> (user-set; default: ABS/DISER national avg.)</td><td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.abs.gov.au" target="_blank">ABS</a> / <a href="https://www.energy.gov.au" target="_blank">DISER</a></td></tr>
            <tr><td style="padding:7px 10px;border:1px solid #e0eaf3;">ICE Segment</td><td style="padding:7px 10px;border:1px solid #e0eaf3;"><strong>{selected_ice_name}: {ice_l100} L/100km</strong></td><td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></td></tr>
            {phev_row}
            {ev_rows}
            <tr><td style="padding:7px 10px;border:1px solid #e0eaf3;">Unit Conversion</td><td style="padding:7px 10px;border:1px solid #e0eaf3;">1 mile = 1.60934 km</td><td style="padding:7px 10px;border:1px solid #e0eaf3;">Standard</td></tr>
            <tr><td style="padding:7px 10px;border:1px solid #e0eaf3;">Vehicle Segment Note</td><td style="padding:7px 10px;border:1px solid #e0eaf3;" colspan="2">Compare equivalent segments only (e.g. small hatch vs. small hatch). Refer to Green Vehicle Guide for classifications.</td></tr>
        </tbody>
    </table>
    <p style="font-size:0.75rem;color:#999;margin:12px 0 0;">Default values should be reviewed periodically as fuel and electricity prices change.</p>
</div>
""", unsafe_allow_html=True)

# 13. Print Summary (hidden on screen, visible on print)
ev_print_row = f"<tr><td>Electricity Price</td><td>${elec_price:.2f} AUD/kWh</td></tr>" if mode == "ICE to EV" else ""

st.markdown(f"""
<div class="print-summary">
    <h1>Dual Mode Fuel Savings — Summary Report</h1>
    <p style="font-size:10pt;color:#555;">Comparison Mode: <strong>{mode}</strong></p>
    <hr/>
    <h2 style="font-size:13pt;color:#1a7fa3;">Your Selection</h2>
    <table>
        <tr><th>Parameter</th><th>Value</th></tr>
        <tr><td>Current ICE Segment</td><td>{selected_ice_name} — {ice_l100} L/100km</td></tr>
        <tr><td>Target BYD Model</td><td>BYD {selected_byd_name} — {byd_consumption} {byd_unit_label}</td></tr>
        <tr><td>Annual Distance</td><td>{ann_km:,.0f} km / {ann_miles:,.0f} mi.</td></tr>
        <tr><td>Days Driven per Week</td><td>{days_per_week}</td></tr>
        <tr><td>Fuel Price</td><td>${fuel_price:.2f} AUD/Litre</td></tr>
        {ev_print_row}
    </table>
    <h2 style="font-size:13pt;color:#1a7fa3;">Results</h2>
    <table>
        <tr><th>Metric</th><th>Value</th><th>Indicator</th></tr>
        <tr><td>Current ICE Annual Cost</td><td><strong>${curr_ann:,.2f} AUD</strong></td><td>C · Cost</td></tr>
        <tr><td>BYD {selected_byd_name} Annual Cost</td><td><strong>${new_ann:,.2f} AUD</strong></td><td>S · Savings</td></tr>
        <tr><td>Estimated Annual Savings</td><td><strong>${savings:,.2f} AUD</strong></td><td>Indicative estimate only</td></tr>
        <tr><td>Monthly Saving</td><td><strong>${(savings/12):,.2f} AUD/mo</strong></td><td>S · Savings</td></tr>
        <tr><td>Cost Reduction</td><td><strong>{pct_saving:.1f}%</strong></td><td>V · Value</td></tr>
    </table>
    <h2 style="font-size:13pt;color:#1a7fa3;">Assumptions & Data Sources</h2>
    <table>
        <tr><th>Parameter</th><th>Value Used</th><th>Source</th></tr>
        <tr><td>Fuel Price</td><td>${fuel_price:.2f} AUD/Litre (default: ABS/DISER national avg.)</td><td>ABS / DISER</td></tr>
        <tr><td>ICE Segment</td><td>{selected_ice_name}: {ice_l100} L/100km</td><td>Green Vehicle Guide</td></tr>
        <tr><td>BYD Model</td><td>BYD {selected_byd_name}: {byd_consumption} {byd_unit_label}</td><td>Green Vehicle Guide</td></tr>
        {"<tr><td>Electricity Price</td><td>$" + f"{elec_price:.2f}" + " AUD/kWh (default: AEMO national avg.)</td><td>AEMO</td></tr>" if mode == "ICE to EV" else ""}
        <tr><td>Annual Distance</td><td>{ann_km:,.0f} km ({days_per_week} days/week × 52 weeks)</td><td>User input</td></tr>
    </table>
    <div class="print-disclaimer">
        <strong>General Estimate Only.</strong> This calculator provides indicative figures and does not constitute financial advice. Results are based on user-provided inputs and national averages. Individual results will vary. Not a substitute for professional financial or automotive advice. ICE segment averages and BYD model consumption figures sourced from the Green Vehicle Guide. Fuel price default sourced from ABS/DISER. Electricity price default sourced from AEMO. Default values should be reviewed periodically as prices change.
    </div>
    <p style="font-size:8pt;color:#aaa;margin-top:16px;">General estimates only. Not financial advice. Data sources: ABS, DISER, AEMO, Green Vehicle Guide.</p>
</div>
""", unsafe_allow_html=True)

# 14. Footer
st.markdown("---")
st.caption("General estimates only. Not financial advice. Data sources: ABS, DISER, AEMO, Green Vehicle Guide.")
