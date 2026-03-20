import streamlit as st
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Dual Mode Savings", page_icon="⛽", layout="wide")

# ── SVG Icons ──────────────────────────────────────────────────────────────────
SVG_CAR  = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1a7fa3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><path d="M5 17H3a2 2 0 0 1-2-2v-4l2.38-4.76A2 2 0 0 1 5.17 5h13.66a2 2 0 0 1 1.79 1.1L23 11v4a2 2 0 0 1-2 2h-2"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="16.5" cy="17.5" r="2.5"/></svg>'
SVG_BOLT = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1a7fa3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>'

# ── Data ───────────────────────────────────────────────────────────────────────
# [I1]-[I4] = ICE segment data. Source: Green Vehicle Guide national averages.
ICE_SEGMENTS = {
    "Average Small SUV":    {"l100": 7.5, "cite": "I1"},
    "Average Hatchback":    {"l100": 6.2, "cite": "I2"},
    "Average Sedan":        {"l100": 6.8, "cite": "I3"},
    "Average Ute (Diesel)": {"l100": 9.5, "cite": "I4"},
}

# [D1]-[D6] EV: GVG EnergyConsumptionWhkm / 10 = kWh/100km
BYD_EV_MODELS = {
    "Dolphin":   {"val": 12.6, "unit": "kWh/100km", "cite": "D1"},
    "Seal":      {"val": 13.8, "unit": "kWh/100km", "cite": "D2"},
    "Atto 3":    {"val": 14.8, "unit": "kWh/100km", "cite": "D3"},
    "Atto 1":    {"val": 15.5, "unit": "kWh/100km", "cite": "D4"},
    "Atto 2":    {"val": 17.0, "unit": "kWh/100km", "cite": "D5"},
    "Sealion 7": {"val": 17.9, "unit": "kWh/100km", "cite": "D6"},
}

# [D1]-[D4] PHEV: GVG FuelConsumptionCombined L/100km
BYD_PHEV_MODELS = {
    "Sealion 6": {"val": 1.1, "unit": "L/100km", "cite": "D1"},
    "Sealion 8": {"val": 1.1, "unit": "L/100km", "cite": "D2"},
    "Sealion 5": {"val": 1.2, "unit": "L/100km", "cite": "D3"},
    "Shark 6":   {"val": 2.0, "unit": "L/100km", "cite": "D4"},
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.block-container { padding-top:3.5rem; padding-bottom:1rem; }
.sidebar-title {
    font-size:2.8rem!important; font-weight:900; line-height:1.0;
    margin-bottom:1.2rem; color:#1a7fa3;
    text-transform:uppercase; letter-spacing:-1px;
}

/* Sidebar radio: small, centered, single line */
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] {
    display:grid!important; grid-template-columns:1fr 1fr!important; gap:8px!important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background:white!important; border:1.5px solid #dce8f5!important;
    border-radius:10px!important; padding:8px 4px!important;
    cursor:pointer!important; min-height:38px!important; height:38px!important;
    box-sizing:border-box!important; display:flex!important;
    flex-direction:row!important; justify-content:center!important;
    align-items:center!important; white-space:nowrap!important;
    overflow:hidden!important; transition:border-color 0.15s!important; width:100%!important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { border-color:#29B5E8!important; }
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background:linear-gradient(135deg,#0a2a5e 0%,#0d3d7a 100%)!important; border-color:#0a2a5e!important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p,
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) span { color:white!important; }
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
    font-size:0.78rem!important; font-weight:600!important; margin:0!important;
    text-align:center!important; white-space:nowrap!important;
    overflow:hidden!important; text-overflow:ellipsis!important; line-height:1!important;
}
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display:none!important; }

/* Main vehicle cards */
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] {
    display:grid!important; grid-template-columns:1fr 1fr!important; gap:10px!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background:white!important; border:1.5px solid #dce8f5!important;
    border-radius:12px!important; padding:14px 16px!important;
    cursor:pointer!important; min-height:78px!important; height:78px!important;
    box-sizing:border-box!important; display:flex!important;
    flex-direction:column!important; justify-content:center!important;
    align-items:flex-start!important; overflow:hidden!important;
    transition:border-color 0.15s!important; width:100%!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { border-color:#29B5E8!important; }
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background:linear-gradient(135deg,#0a2a5e 0%,#0d3d7a 100%)!important; border-color:#0a2a5e!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p,
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) span { color:white!important; }
[data-testid="stMain"] div[role="radiogroup"] > label > div:first-child { display:none!important; }
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p {
    margin:0 0 2px!important; line-height:1.25!important;
    white-space:nowrap!important; overflow:hidden!important; text-overflow:ellipsis!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p:first-child {
    font-size:0.88rem!important; font-weight:700!important; color:#1a1a2e!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p:last-child {
    font-size:0.72rem!important; color:#888!important;
}

/* Hero */
.flashy-result {
    background:linear-gradient(135deg,#29B5E8 0%,#1a7fa3 100%);
    color:white; padding:40px 48px; border-radius:18px;
    box-shadow:0 20px 40px rgba(0,0,0,0.2); margin-bottom:32px;
    border:2px solid rgba(255,255,255,0.2);
}
.flash_label { font-size:0.9rem; text-transform:uppercase; letter-spacing:6px; opacity:0.85; margin:0 0 10px; text-align:center; }
.flash_number_row { display:flex; align-items:center; justify-content:center; gap:16px; margin:0 0 8px; }
.flash_val { font-size:16rem; font-weight:900; line-height:1; text-shadow:4px 4px 20px rgba(0,0,0,0.25); margin:0; }
.flash_cite { font-size:1.1rem; font-weight:700; opacity:0.8; align-self:flex-start; margin-top:24px; }
.flash_side { display:flex; flex-direction:column; align-items:flex-start; justify-content:center; gap:2px; }
.flash_unit { font-size:0.75rem; font-weight:600; letter-spacing:2px; opacity:0.85; text-transform:uppercase; }
.flash_disclaimer { background:rgba(255,255,255,0.12); border-radius:10px; padding:14px 20px; margin-top:20px; font-size:0.78rem; line-height:1.6; }

.segment-header { font-size:0.68rem; font-weight:700; letter-spacing:3px; color:#888; text-transform:uppercase; margin:0.5rem 0 0.8rem; display:flex; align-items:center; gap:4px; }

/* Metric cards — no badges */
.metric-card { background:#f8fafc; border:1px solid #e0eaf3; border-radius:10px; padding:14px 16px; margin-bottom:10px; }
.metric-card-green { background:#e6f4ea; border:1px solid #b7dfbf; border-radius:10px; padding:14px 16px; margin-bottom:10px; }
.metric-label { font-size:0.82rem; color:#666; margin:0 0 4px; }
.metric-value { font-size:1.8rem; font-weight:700; color:#1a1a2e; margin:0; }
.metric-value-green { font-size:1.8rem; font-weight:700; color:#137333; margin:0; }
.metric-sub { font-size:0.72rem; color:#999; margin:3px 0 0; }
.metric-sub-green { font-size:0.72rem; color:#137333; margin:3px 0 0; }
.metric-delta { font-size:0.82rem; color:#c0392b; margin:2px 0 0; font-weight:600; }
.cite-tag { font-size:0.6rem; color:#1a7fa3; font-weight:700; vertical-align:super; margin-left:2px; }

/* Assumptions */
.assumptions-section { background:#f8fafc; border:1px solid #e0eaf3; border-radius:10px; padding:24px 28px; margin-top:2rem; }
.assumptions-title { font-size:0.72rem; font-weight:700; color:#1a7fa3; text-transform:uppercase; letter-spacing:2px; margin:0 0 10px; }
.assumptions-desc { font-size:0.82rem; color:#555; margin:0 0 16px; line-height:1.6; }
.cite-legend { margin-top:16px; padding-top:14px; border-top:1px solid #e0eaf3; }
.cite-legend-title { font-size:0.68rem; font-weight:700; color:#888; text-transform:uppercase; letter-spacing:2px; margin:0 0 8px; }
.cite-row { font-size:0.78rem; color:#555; margin:4px 0; line-height:1.5; }
.cite-key { font-weight:700; color:#1a7fa3; min-width:40px; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown('<p class="sidebar-title">DUAL MODE<br>FUEL SAVINGS</p>', unsafe_allow_html=True)
mode = st.sidebar.radio("Comparison Mode", ["ICE to PHEV", "ICE to EV"], horizontal=True)
st.sidebar.divider()
st.sidebar.markdown("**Controls**")

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

# ── Card Selectors ─────────────────────────────────────────────────────────────
col_ice, col_byd = st.columns(2)

with col_ice:
    st.markdown('<p class="segment-header">' + SVG_CAR + ' Current ICE Segment</p>', unsafe_allow_html=True)
    ice_keys = list(ICE_SEGMENTS.keys())
    ice_options = [
        "**" + k + "**\n\n" + str(v["l100"]) + " L/100km  [" + v["cite"] + "]"
        for k, v in ICE_SEGMENTS.items()
    ]
    ice_sel = st.radio("ice_seg", ice_options, index=2, label_visibility="collapsed", key="ice_radio")
    ice_idx = ice_options.index(ice_sel)
    selected_ice_name = ice_keys[ice_idx]
    ice_data = ICE_SEGMENTS[selected_ice_name]
    ice_l100 = ice_data["l100"]
    ice_cite = ice_data["cite"]

with col_byd:
    if mode == "ICE to PHEV":
        st.markdown('<p class="segment-header">' + SVG_BOLT + ' Target BYD PHEV Model</p>', unsafe_allow_html=True)
        byd_keys = list(BYD_PHEV_MODELS.keys())
        byd_options = [
            "**" + k + "**\n\n" + str(v["val"]) + " " + v["unit"] + "  [" + v["cite"] + "]"
            for k, v in BYD_PHEV_MODELS.items()
        ]
        byd_sel = st.radio("byd_phev", byd_options, index=0, label_visibility="collapsed", key="phev_radio")
        byd_idx = byd_options.index(byd_sel)
        selected_byd_name = byd_keys[byd_idx]
        byd_data = BYD_PHEV_MODELS[selected_byd_name]
    else:
        st.markdown('<p class="segment-header">' + SVG_BOLT + ' Target BYD EV Model</p>', unsafe_allow_html=True)
        byd_keys = list(BYD_EV_MODELS.keys())
        byd_options = [
            "**" + k + "**\n\n" + str(v["val"]) + " " + v["unit"] + "  [" + v["cite"] + "]"
            for k, v in BYD_EV_MODELS.items()
        ]
        byd_sel = st.radio("byd_ev", byd_options, index=0, label_visibility="collapsed", key="ev_radio")
        byd_idx = byd_options.index(byd_sel)
        selected_byd_name = byd_keys[byd_idx]
        byd_data = BYD_EV_MODELS[selected_byd_name]

byd_val  = byd_data["val"]
byd_unit = byd_data["unit"]
byd_cite = byd_data["cite"]

# ── Calculations ───────────────────────────────────────────────────────────────
ann_miles  = daily_miles * days_per_week * 52
ann_km     = ann_miles * 1.60934
curr_ann   = (ann_km / 100) * ice_l100 * fuel_price
new_ann    = (ann_km / 100) * byd_val * (fuel_price if mode == "ICE to PHEV" else elec_price)
savings    = curr_ann - new_ann
pct_saving = (savings / curr_ann * 100) if curr_ann > 0 else 0
ann_dist_display = (f"{ann_miles:,.0f}" + " mi.") if unit == "mi." else (f"{ann_km:,.0f}" + " km.")
new_label  = "BYD " + selected_byd_name

# ── Hero ───────────────────────────────────────────────────────────────────────
segment_note_html = ""
if mode == "ICE to EV":
    segment_note_html = (
        "<br><strong>Segment note:</strong> For accurate comparisons, use vehicles of the same segment "
        "(e.g. small hatch vs. small hatch). Mixing segments will produce misleading results."
    )

hero_html = (
    '<div class="flashy-result">'
      '<p class="flash_label">Estimated Annual Savings</p>'
      '<div class="flash_number_row">'
        '<h1 class="flash_val">$' + f"{savings:,.2f}" + '</h1>'
        '<sup class="flash_cite">*[P1]</sup>'
        '<div class="flash_side">'
          '<span class="flash_unit">Indicative Estimate</span>'
          '<span class="flash_unit">AUD per Year</span>'
        '</div>'
      '</div>'
      '<div class="flash_disclaimer">'
        '<strong>General Estimate Only.</strong> This calculator provides indicative figures and does not '
        'constitute financial advice. Results are based on user-provided inputs and national averages. '
        'Individual results will vary. Not a substitute for professional financial or automotive advice.'
        + segment_note_html +
      '</div>'
    '</div>'
)
st.markdown(hero_html, unsafe_allow_html=True)

# ── Chart + Key Metrics ────────────────────────────────────────────────────────
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
    metrics_html = (
        '<div class="metric-card">'
          '<p class="metric-label">Current Monthly</p>'
          '<p class="metric-value">$' + f"{curr_ann/12:,.2f}" + '<sup class="cite-tag">[C1]</sup></p>'
          '<p class="metric-sub">' + selected_ice_name + ' · ' + str(ice_l100) + ' L/100km <sup>[' + ice_cite + ']</sup></p>'
        '</div>'
        '<div class="metric-card">'
          '<p class="metric-label">' + new_label + ' Monthly</p>'
          '<p class="metric-value">$' + f"{new_ann/12:,.2f}" + '<sup class="cite-tag">[S1]</sup></p>'
          '<p class="metric-delta">&#8595; &minus;$' + f"{savings/12:,.2f}" + '/mo vs ICE <sup class="cite-tag">[S2]</sup></p>'
          '<p class="metric-sub">' + str(byd_val) + ' ' + byd_unit + ' <sup>[' + byd_cite + ']</sup></p>'
        '</div>'
        '<div class="metric-card">'
          '<p class="metric-label">Annual Distance</p>'
          '<p class="metric-value">' + ann_dist_display + '<sup class="cite-tag">[C2]</sup></p>'
          '<p class="metric-sub">' + str(days_per_week) + ' days/week &times; 52 weeks</p>'
        '</div>'
        '<div class="metric-card-green">'
          '<p class="metric-label" style="color:#137333;">Estimated Value</p>'
          '<p class="metric-value-green">' + f"{pct_saving:.1f}" + '% cheaper<sup class="cite-tag">[V1]</sup></p>'
          '<p class="metric-sub-green">vs ' + selected_ice_name + '</p>'
        '</div>'
    )
    st.markdown(metrics_html, unsafe_allow_html=True)

# ── PDF Generation ─────────────────────────────────────────────────────────────
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Header bar
    pdf.set_fill_color(26, 127, 163)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_y(8)
    pdf.cell(0, 10, "Dual Mode Fuel Savings - Summary Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Comparison Mode: " + mode, ln=True, align="C")
    pdf.ln(10)
    pdf.set_text_color(30, 30, 30)

    def section_title(title):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(26, 127, 163)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_text_color(30, 30, 30)

    # Your Selection
    section_title("Your Selection")
    pdf.set_font("Helvetica", "", 9)
    col_w = [85, 95]
    rows_sel = [
        ("Current ICE Segment [" + ice_cite + "]", selected_ice_name + " - " + str(ice_l100) + " L/100km"),
        ("Target BYD Model [" + byd_cite + "]", "BYD " + selected_byd_name + " - " + str(byd_val) + " " + byd_unit),
        ("Annual Distance [C2]", f"{ann_km:,.0f} km / {ann_miles:,.0f} mi."),
        ("Days Driven per Week", str(days_per_week)),
        ("Fuel Price [P1]", "$" + f"{fuel_price:.2f}" + " AUD/Litre"),
    ]
    if mode == "ICE to EV":
        rows_sel.append(("Electricity Price [P2]", "$" + f"{elec_price:.2f}" + " AUD/kWh"))
    for label, value in rows_sel:
        pdf.set_fill_color(240, 247, 255)
        pdf.cell(col_w[0], 7, label, border=1, fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_w[1], 7, value, border=1, fill=True, ln=True)
    pdf.ln(4)

    # Results
    section_title("Results")
    pdf.set_font("Helvetica", "", 9)
    col_w3 = [80, 75, 25]
    pdf.set_fill_color(224, 234, 251)
    pdf.set_font("Helvetica", "B", 9)
    for h, w in zip(["Metric", "Value", "Ref"], col_w3):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    rows_res = [
        ("Current ICE Annual Cost",              "$" + f"{curr_ann:,.2f}" + " AUD",   "[C1]"),
        ("BYD " + selected_byd_name + " Annual", "$" + f"{new_ann:,.2f}" + " AUD",    "[S1]"),
        ("Estimated Annual Savings",             "$" + f"{savings:,.2f}" + " AUD",    "[P1]"),
        ("Monthly Saving",                       "$" + f"{savings/12:,.2f}" + "/mo",  "[S2]"),
        ("Cost Reduction",                       f"{pct_saving:.1f}% cheaper",        "[V1]"),
    ]
    for label, value, ref in rows_res:
        pdf.cell(col_w3[0], 7, label, border=1)
        pdf.cell(col_w3[1], 7, value, border=1)
        pdf.cell(col_w3[2], 7, ref, border=1, ln=True)
    pdf.ln(4)

    # Assumptions
    section_title("Assumptions & Data Sources")
    col_w4 = [18, 58, 62, 42]
    pdf.set_fill_color(224, 234, 251)
    pdf.set_font("Helvetica", "B", 9)
    for h, w in zip(["Ref", "Parameter", "Value", "Source"], col_w4):
        pdf.cell(w, 7, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    assumption_rows = [
        ("[P1]",             "Fuel Price",          "$" + f"{fuel_price:.2f}" + " AUD/L",     "ABS / DISER"),
        ("[" + ice_cite + "]", "ICE Segment",       selected_ice_name[:25] + ": " + str(ice_l100) + " L/100km", "Green Vehicle Guide"),
        ("[C2]",             "Annual Distance",      f"{ann_km:,.0f} km",                      "User input"),
        ("[" + byd_cite + "]", "BYD " + selected_byd_name, str(byd_val) + " " + byd_unit,    "Green Vehicle Guide"),
        ("[V1]",             "% Saving",             f"{pct_saving:.1f}% cheaper",             "Calculated"),
    ]
    if mode == "ICE to EV":
        assumption_rows.insert(3, ("[P2]", "Electricity Price", "$" + f"{elec_price:.2f}" + " AUD/kWh", "AEMO"))
    for row in assumption_rows:
        for i, cell in enumerate(row):
            pdf.cell(col_w4[i], 6, cell, border=1)
        pdf.ln()
    pdf.ln(4)

    # Citation key
    section_title("Citation & Formula Key")
    pdf.set_font("Helvetica", "", 8)
    cite_lines = [
        "[P1] Fuel price - user-set or ABS/DISER national average.",
        "[C1] Current Monthly Cost = (Annual km / 100) x ICE L/100km x Fuel Price / 12",
        "[C2] Annual Distance = Daily Commute x Days/week x 52 weeks",
        "[S1] BYD Monthly Cost = (Annual km / 100) x BYD Consumption x Energy Price / 12",
        "[S2] Monthly Saving = ICE Monthly [C1] - BYD Monthly [S1]",
        "[V1] % Value = (ICE Annual - BYD Annual) / ICE Annual x 100",
        "[I1] Avg Small SUV: 7.5  [I2] Avg Hatchback: 6.2  [I3] Avg Sedan: 6.8  [I4] Avg Ute Diesel: 9.5 L/100km - Green Vehicle Guide",
    ]
    if mode == "ICE to EV":
        cite_lines.insert(1, "[P2] Electricity price - user-set or AEMO national average.")
        for i, (k, v) in enumerate(BYD_EV_MODELS.items(), 1):
            cite_lines.append("[D" + str(i) + "] BYD " + k + ": " + str(v["val"]) + " kWh/100km - Green Vehicle Guide")
    else:
        for i, (k, v) in enumerate(BYD_PHEV_MODELS.items(), 1):
            cite_lines.append("[D" + str(i) + "] BYD " + k + ": " + str(v["val"]) + " L/100km - Green Vehicle Guide")
    for line in cite_lines:
        pdf.cell(0, 5, line, ln=True)
    pdf.ln(4)

    # Disclaimer
    pdf.set_fill_color(240, 247, 255)
    pdf.set_font("Helvetica", "B", 8)
    pdf.multi_cell(
        0, 5,
        "GENERAL ESTIMATE ONLY. This calculator provides indicative figures and does not constitute "
        "financial advice. Results are based on user-provided inputs and national averages. Individual "
        "results will vary. Not a substitute for professional financial or automotive advice. BYD model "
        "consumption data sourced from greenvehicleguide.gov.au. Fuel price default: ABS/DISER. "
        "Electricity price default: AEMO.",
        border=1, fill=True
    )
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "General estimates only. Not financial advice. Sources: ABS, DISER, AEMO, Green Vehicle Guide.", ln=True, align="C")

    return bytes(pdf.output())

# ── Download Button ────────────────────────────────────────────────────────────
pdf_bytes = generate_pdf()
st.download_button(
    label="Download as PDF",
    data=pdf_bytes,
    file_name="DualMode_Savings_Summary.pdf",
    mime="application/pdf"
)

# ── Assumptions — always visible ───────────────────────────────────────────────
if mode == "ICE to PHEV":
    mode_rows = (
        '<tr>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">PHEV Consumption <sup>[' + byd_cite + ']</sup></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">BYD ' + selected_byd_name + ': <strong>' + str(byd_val) + ' L/100km</strong></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></td>'
        '</tr>'
    )
else:
    mode_rows = (
        '<tr>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">EV Consumption <sup>[' + byd_cite + ']</sup></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">BYD ' + selected_byd_name + ': <strong>' + str(byd_val) + ' kWh/100km</strong></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></td>'
        '</tr>'
        '<tr>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">Electricity Price <sup>[P2]</sup></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><strong>$' + f"{elec_price:.2f}" + ' AUD/kWh</strong> (user-set; default: AEMO national avg.)</td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.aemo.com.au" target="_blank">AEMO</a></td>'
        '</tr>'
    )

d_cite_rows = ""
if mode == "ICE to EV":
    for i, (k, v) in enumerate(BYD_EV_MODELS.items(), 1):
        d_cite_rows += (
            '<p class="cite-row"><span class="cite-key"><sup>[D' + str(i) + ']</sup></span> '
            'BYD ' + k + ' &mdash; ' + str(v["val"]) + ' kWh/100km. '
            'Source: <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
        )
else:
    for i, (k, v) in enumerate(BYD_PHEV_MODELS.items(), 1):
        d_cite_rows += (
            '<p class="cite-row"><span class="cite-key"><sup>[D' + str(i) + ']</sup></span> '
            'BYD ' + k + ' &mdash; ' + str(v["val"]) + ' L/100km. '
            'Source: <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
        )

p2_row = ""
if mode == "ICE to EV":
    p2_row = (
        '<p class="cite-row"><span class="cite-key"><sup>[P2]</sup></span> '
        'Electricity price &mdash; user-set or AEMO national average. '
        'Source: <a href="https://www.aemo.com.au" target="_blank">AEMO</a></p>'
    )

assumptions_html = (
    '<div class="assumptions-section">'
    '<p class="assumptions-title">Assumptions &amp; Data Sources</p>'
    '<p class="assumptions-desc">All figures are indicative estimates. This tool is classified as a <em>Generic Calculator</em> '
    'and does not constitute financial, legal, or automotive advice. Results assume consistent driving behaviour '
    'and do not account for traffic, terrain, vehicle age, or maintenance costs.</p>'
    '<table style="width:100%;border-collapse:collapse;font-size:0.8rem;">'
    '<thead><tr style="background:#e8f0fb;">'
    '<th style="text-align:left;padding:8px 10px;border:1px solid #d0dff0;font-weight:600;">Parameter</th>'
    '<th style="text-align:left;padding:8px 10px;border:1px solid #d0dff0;font-weight:600;">Value Used</th>'
    '<th style="text-align:left;padding:8px 10px;border:1px solid #d0dff0;font-weight:600;">Source</th>'
    '</tr></thead>'
    '<tbody>'
    '<tr>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;">Annual Distance <sup>[C2]</sup></td>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;">Daily Commute &times; ' + str(days_per_week) + ' days/week &times; 52 weeks = <strong>' + f"{ann_km:,.0f}" + ' km</strong></td>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;">User input</td>'
    '</tr>'
    '<tr>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;">Fuel Price <sup>[P1]</sup></td>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><strong>$' + f"{fuel_price:.2f}" + ' AUD/Litre</strong> (user-set; default: ABS/DISER national avg.)</td>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.abs.gov.au" target="_blank">ABS</a> / <a href="https://www.energy.gov.au" target="_blank">DISER</a></td>'
    '</tr>'
    '<tr>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;">ICE Segment <sup>[' + ice_cite + ']</sup></td>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><strong>' + selected_ice_name + ': ' + str(ice_l100) + ' L/100km</strong></td>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></td>'
    '</tr>'
    + mode_rows +
    '<tr>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;">Unit Conversion</td>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;">1 mile = 1.60934 km</td>'
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;">Standard</td>'
    '</tr>'
    '</tbody></table>'
    '<div class="cite-legend">'
    '<p class="cite-legend-title">Citation &amp; Formula Key</p>'
    '<p class="cite-row"><span class="cite-key"><sup>[P1]</sup></span> Fuel price &mdash; user-set or ABS/DISER national average. '
    'Sources: <a href="https://www.abs.gov.au" target="_blank">ABS</a>, <a href="https://www.energy.gov.au" target="_blank">DISER</a></p>'
    + p2_row +
    '<p class="cite-row"><span class="cite-key"><sup>[C1]</sup></span> Current Monthly Cost = (Annual km &divide; 100) &times; ICE L/100km &times; Fuel Price &divide; 12</p>'
    '<p class="cite-row"><span class="cite-key"><sup>[C2]</sup></span> Annual Distance = Daily Commute &times; Days/week &times; 52 weeks</p>'
    '<p class="cite-row"><span class="cite-key"><sup>[S1]</sup></span> BYD Monthly Cost = (Annual km &divide; 100) &times; BYD Consumption &times; Energy Price &divide; 12</p>'
    '<p class="cite-row"><span class="cite-key"><sup>[S2]</sup></span> Monthly Saving = ICE Monthly <sup>[C1]</sup> &minus; BYD Monthly <sup>[S1]</sup></p>'
    '<p class="cite-row"><span class="cite-key"><sup>[V1]</sup></span> % Value = (ICE Annual &minus; BYD Annual) &divide; ICE Annual &times; 100</p>'
    '<p class="cite-row"><span class="cite-key"><sup>[I1]</sup></span> Average Small SUV: 7.5 L/100km &mdash; <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
    '<p class="cite-row"><span class="cite-key"><sup>[I2]</sup></span> Average Hatchback: 6.2 L/100km &mdash; <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
    '<p class="cite-row"><span class="cite-key"><sup>[I3]</sup></span> Average Sedan: 6.8 L/100km &mdash; <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
    '<p class="cite-row"><span class="cite-key"><sup>[I4]</sup></span> Average Ute (Diesel): 9.5 L/100km &mdash; <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
    + d_cite_rows +
    '</div>'
    '<p style="font-size:0.75rem;color:#999;margin:12px 0 0;">'
    'BYD model consumption data sourced directly from greenvehicleguide.gov.au. '
    'Default values should be reviewed periodically as fuel and electricity prices change.</p>'
    '</div>'
)
st.markdown(assumptions_html, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("General estimates only. Not financial advice. Data sources: ABS, DISER, AEMO, Green Vehicle Guide.")
