import streamlit as st
import pandas as pd
import altair as alt
from fpdf import FPDF

st.set_page_config(page_title="BYD Savings Calculator", page_icon="⛽", layout="wide")

# ── SVG Icons ──────────────────────────────────────────────────────────────────
SVG_CAR  = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1a7fa3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><path d="M5 17H3a2 2 0 0 1-2-2v-4l2.38-4.76A2 2 0 0 1 5.17 5h13.66a2 2 0 0 1 1.79 1.1L23 11v4a2 2 0 0 1-2 2h-2"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="16.5" cy="17.5" r="2.5"/></svg>'
SVG_BOLT = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1a7fa3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;margin-right:6px"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>'

# ── Data ───────────────────────────────────────────────────────────────────────
# Each entry has:
#   "card"  = ALL CAPS label shown on the selection card
#   "name"  = Title case name used everywhere else (metrics, chart, assumptions, PDF)
#   "l100" / "val" = consumption value
#   "cite"  = citation reference

ICE_SEGMENTS = {
    "AVERAGE HATCHBACK":    {"name": "Average Hatchback",    "l100": 6.2, "cite": "I1"},
    "AVERAGE SEDAN":        {"name": "Average Sedan",        "l100": 6.8, "cite": "I2"},
    "AVERAGE SMALL SUV":    {"name": "Average Small SUV",    "l100": 7.5, "cite": "I3"},
    "AVERAGE UTE (DIESEL)": {"name": "Average Ute (Diesel)", "l100": 9.5, "cite": "I4"},
}

# kWh/100km from GVG EnergyConsumptionWhkm / 10
BYD_EV_MODELS = {
    "BYD ATTO 1":    {"name": "BYD Atto 1",    "val": 15.5, "unit": "kWh/100km", "cite": "D1"},
    "BYD ATTO 2":    {"name": "BYD Atto 2",    "val": 17.0, "unit": "kWh/100km", "cite": "D2"},
    "BYD ATTO 3":    {"name": "BYD Atto 3",    "val": 14.8, "unit": "kWh/100km", "cite": "D3"},
    "BYD DOLPHIN":   {"name": "BYD Dolphin",   "val": 12.6, "unit": "kWh/100km", "cite": "D4"},
    "BYD SEAL":      {"name": "BYD Seal",      "val": 13.8, "unit": "kWh/100km", "cite": "D5"},
    "BYD SEALION 7": {"name": "BYD Sealion 7", "val": 17.9, "unit": "kWh/100km", "cite": "D6"},
}

# L/100km (FuelConsumptionCombined) + Wh/km (EnergyConsumptionWhkm) from GVG
BYD_PHEV_MODELS = {
    "BYD SEALION 5": {"name": "BYD Sealion 5", "val": 1.2, "unit": "L/100km", "wh_km": 120, "cite": "D1"},
    "BYD SEALION 6": {"name": "BYD Sealion 6", "val": 1.1, "unit": "L/100km", "wh_km": 169, "cite": "D2"},
    "BYD SEALION 8": {"name": "BYD Sealion 8", "val": 1.1, "unit": "L/100km", "wh_km": 150, "cite": "D3"},
    "BYD SHARK 6":   {"name": "BYD Shark 6",   "val": 2.0, "unit": "L/100km", "wh_km": 212, "cite": "D4"},
}

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;900&display=swap');

/* ── LIGHT MODE BASE ─────────────────────────────────────────────────────── */
html, body, [class*="css"], .stApp { font-family:'Montserrat',sans-serif!important; }
/* Hide Streamlit chrome */
#MainMenu, footer { visibility:hidden!important; }
[data-testid="stHeader"] { height:0!important; }
.block-container { padding-top:3.5rem!important; padding-bottom:1rem; }

/* Subtle page tint */
.stApp { background:linear-gradient(160deg,#f2f6fc 0%,#edf1f8 100%)!important; }
[data-testid="stSidebar"] > div:first-child { background:linear-gradient(180deg,#f7f9fc 0%,#f0f4fa 100%)!important; }

.sidebar-title {
    font-size:2.8rem!important; font-weight:900; line-height:1.0;
    margin-bottom:1.2rem;
    background:linear-gradient(135deg,#0d2b6b 0%,#1460a0 50%,#29B5E8 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text;
    text-transform:uppercase; letter-spacing:-1px;
}

/* Sidebar "Comparison Mode" label */
[data-testid="stSidebar"] p:has(+ div [data-testid="stHorizontalBlock"]) {
    font-size:0.7rem!important; font-weight:700!important; letter-spacing:2px!important;
    text-transform:uppercase!important; color:#6d7a88!important; margin-bottom:6px!important;
}

/* Sidebar control labels with icons */
.ctrl-label {
    font-size:0.78rem!important; font-weight:600!important;
    color:#444452!important; display:flex!important; align-items:center!important;
    gap:7px!important; margin:12px 0 3px!important; padding:0!important; line-height:1.4!important;
    letter-spacing:0.2px!important;
}
.ctrl-label svg { flex-shrink:0; color:#1a7fa3; }

/* Placeholder text colour */
[data-testid="stSidebar"] [data-testid="stNumberInput"] input::placeholder {
    color:#aab8c8!important; opacity:1!important;
}
[data-theme="dark"] [data-testid="stNumberInput"] input::placeholder {
    color:#445566!important; opacity:1!important;
}

/* Compact number input beside sliders (inside columns) — restore full column width */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stNumberInput"] {
    width:auto!important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stNumberInput"] input {
    font-size:0.78rem!important; font-weight:700!important;
    text-align:center!important; padding:2px 4px!important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="stNumberInput"] button {
    display:none!important;
}
/* Fuel / Electricity price inputs — white background, 2/3 width */
[data-testid="stSidebar"] > div > div > div [data-testid="stNumberInput"] {
    width:60%!important;
}
[data-testid="stSidebar"] > div > div > div [data-testid="stNumberInput"] > div {
    background:#ffffff!important; border-color:#d0dce8!important; transition:box-shadow 0.15s,border-color 0.15s!important;
}
[data-testid="stSidebar"] > div > div > div [data-testid="stNumberInput"] > div:hover {
    border-color:#e8192c!important; box-shadow:0 0 0 2px rgba(232,25,44,0.35)!important;
}
[data-testid="stSidebar"] > div > div > div [data-testid="stNumberInput"] input {
    background:#ffffff!important;
}
[data-testid="stSidebar"] > div > div > div [data-testid="stNumberInput"] button {
    background:#ffffff!important; border-color:#d0dce8!important; transition:background 0.15s,color 0.15s,box-shadow 0.15s!important;
}
[data-testid="stSidebar"] > div > div > div [data-testid="stNumberInput"] button:hover {
    background:#e8192c!important; color:#ffffff!important;
    box-shadow:0 0 8px rgba(232,25,44,0.55)!important; border-color:#e8192c!important;
}

/* Controls section header */
[data-testid="stSidebar"] strong { font-size:0.68rem!important; font-weight:800!important;
    text-transform:uppercase!important; letter-spacing:3px!important; color:#888896!important; }

/* Comparison mode toggle buttons */
[data-testid="stSidebar"] button[kind="primary"] {
    background:linear-gradient(135deg,#0a2a5e 0%,#0d3d7a 100%)!important;
    border:1.5px solid #0a2a5e!important; color:white!important;
    border-radius:10px!important; font-weight:700!important; font-size:0.78rem!important;
    height:40px!important; min-height:40px!important; padding:8px 4px!important;
    box-shadow:0 4px 12px rgba(10,42,94,0.35)!important;
    transition:all 0.15s!important;
}
[data-testid="stSidebar"] button[kind="secondary"] {
    background:white!important; border:1.5px solid #dce8f5!important;
    border-radius:10px!important; font-weight:600!important; font-size:0.78rem!important;
    color:#1a1a2e!important; height:40px!important; min-height:40px!important; padding:8px 4px!important;
    box-shadow:0 1px 4px rgba(0,0,0,0.06)!important; transition:all 0.15s!important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    border-color:#29B5E8!important; box-shadow:0 2px 8px rgba(41,181,232,0.2)!important;
}
[data-testid="stSidebar"] button[kind="primary"] span[data-testid="stIconMaterial"],
[data-testid="stSidebar"] button[kind="primary"] p { color:white!important; }
[data-testid="stSidebar"] button[kind="secondary"] span[data-testid="stIconMaterial"],
[data-testid="stSidebar"] button[kind="secondary"] p { color:#1a1a2e!important; }

/* Sidebar radio (km/mi) */
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
    overflow:hidden!important; transition:all 0.15s!important; width:100%!important;
    box-shadow:0 1px 3px rgba(0,0,0,0.05)!important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
    font-size:0.78rem!important; font-weight:600!important; margin:0!important;
    text-align:center!important; white-space:nowrap!important;
    overflow:hidden!important; text-overflow:ellipsis!important;
    line-height:1!important; color:#1a1a2e!important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    border-color:#29B5E8!important; box-shadow:0 2px 8px rgba(41,181,232,0.15)!important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background:linear-gradient(135deg,#0a2a5e 0%,#0d3d7a 100%)!important;
    border-color:#0a2a5e!important; box-shadow:0 4px 12px rgba(10,42,94,0.3)!important;
}
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p,
[data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) span { color:white!important; }
[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display:none!important; }

/* Force all vehicle radio containers — and every ancestor — to full width */
[data-testid="stMain"] [data-testid="stVerticalBlock"],
[data-testid="stMain"] [data-testid="element-container"],
[data-testid="stMain"] [data-testid="stRadio"],
[data-testid="stMain"] [data-testid="stRadio"] > div[role="radiogroup"] {
    width:100%!important; max-width:100%!important; box-sizing:border-box!important;
}
/* 4-card grids (ICE & PHEV): 4 columns, 1 row */
[data-testid="stMain"] div[role="radiogroup"]:has(> label:nth-child(4):last-child) {
    display:grid!important; grid-template-columns:repeat(4,1fr)!important; gap:10px!important;
}
/* 6-card grids (BYD EV): 3 columns, 2 rows */
[data-testid="stMain"] div[role="radiogroup"]:has(> label:nth-child(6):last-child) {
    display:grid!important; grid-template-columns:repeat(3,1fr)!important; gap:10px!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background:white!important; border:1.5px solid #e2eaf4!important;
    border-radius:14px!important; padding:14px 16px!important;
    cursor:pointer!important; min-height:78px!important;
    box-sizing:border-box!important; display:flex!important;
    flex-direction:column!important; justify-content:center!important;
    align-items:flex-start!important;
    transition:all 0.18s ease!important; width:100%!important;
    box-shadow:0 2px 8px rgba(0,0,0,0.05)!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    border-color:#29B5E8!important;
    box-shadow:0 6px 20px rgba(41,181,232,0.2)!important;
    transform:translateY(-2px)!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background:linear-gradient(135deg,#0a2a5e 0%,#0e4080 100%)!important;
    border-color:#1a5fa0!important;
    box-shadow:0 8px 24px rgba(10,42,94,0.4)!important;
    transform:translateY(-1px)!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p,
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) span,
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) strong { color:white!important; }
[data-testid="stMain"] div[role="radiogroup"] > label > div:first-child { display:none!important; }
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p {
    margin:0 0 2px!important; line-height:1.25!important;
    white-space:normal!important; word-break:break-word!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p:first-child {
    font-size:0.88rem!important; font-weight:700!important; color:#1a1a2e!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p:nth-child(2) {
    font-size:0.72rem!important; color:#5f6d88!important;
}
/* Citation superscript paragraph */
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p:nth-child(3) {
    font-size:0.58rem!important; color:#1a7fa3!important; font-weight:700!important;
    margin:1px 0 0!important; line-height:1!important; letter-spacing:0.5px!important;
}
[data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) > div:last-child > div > p:nth-child(3) {
    color:rgba(255,255,255,0.65)!important;
}

/* Hero */
.flashy-result {
    background:linear-gradient(135deg,#0d2b6b 0%,#1460a0 45%,#1a9fc8 100%);
    color:white; padding:40px 48px; border-radius:22px;
    box-shadow:0 24px 56px rgba(10,42,94,0.35), 0 0 0 1px rgba(255,255,255,0.08) inset;
    margin-bottom:32px; border:none;
}
.flash_label { font-size:1.0rem; text-transform:uppercase; letter-spacing:8px; opacity:0.7;
    margin:0 0 10px; text-align:center; font-weight:600; }
.flash_number_row { display:flex; align-items:center; justify-content:center; gap:16px; margin:0 0 8px; }
.flash_val { font-size:clamp(4rem, 14vw, 19rem); font-weight:900; line-height:1;
    text-shadow:0 4px 32px rgba(0,0,0,0.3); margin:0; letter-spacing:-4px; }
.flash_cite { font-size:1.3rem; font-weight:700; opacity:0.7; vertical-align:super; line-height:0; margin-left:0.15em; letter-spacing:0; }
.flash_side { display:flex; flex-direction:column; align-items:flex-start; justify-content:center; gap:2px; }
.flash_unit { font-size:0.92rem; font-weight:700; letter-spacing:3px; opacity:0.75; text-transform:uppercase; }
.flash_disclaimer { background:rgba(0,0,0,0.18); border-radius:12px; padding:14px 20px;
    margin-top:20px; font-size:0.72rem; line-height:1.7; border:1px solid rgba(255,255,255,0.08); }

/* Cost Comparison chart card */
.stVegaLiteChart {
    background:white!important; border:1px solid #e2eaf4!important;
    border-radius:14px!important; padding:16px 16px 8px!important;
    box-shadow:inset 4px 0 0 #1460a0, 0 2px 8px rgba(0,0,0,0.04)!important;
    overflow:hidden!important;
}
/* Make SVG background transparent so the card background shows through */
.stVegaLiteChart svg { background:transparent!important; }
.stVegaLiteChart svg rect.background { fill:transparent!important; }
[data-theme="dark"] .stVegaLiteChart {
    background:#141e30!important; border-color:#1e2d45!important;
    box-shadow:inset 4px 0 0 #29B5E8, 0 2px 8px rgba(0,0,0,0.12)!important;
}
/* Brighten chart text and grid lines in dark mode */
[data-theme="dark"] .stVegaLiteChart svg text { fill:#a8c0d8!important; }
[data-theme="dark"] .stVegaLiteChart svg .role-axis .grid line { stroke:rgba(80,110,150,0.35)!important; }

.segment-header { font-size:0.66rem; font-weight:800; letter-spacing:3px; color:#7a8896;
    text-transform:uppercase; margin:0.5rem 0 0.8rem; display:flex; align-items:center; gap:6px; }

/* Section divider */
.section-divider {
    height:1px; margin:24px 0;
    background:linear-gradient(90deg,transparent,#dce8f5 30%,#dce8f5 70%,transparent);
}
[data-theme="dark"] .section-divider { background:linear-gradient(90deg,transparent,#1e2d45 30%,#1e2d45 70%,transparent); }

/* Metric cards */
.metric-card {
    background:white; border:1px solid #e2eaf4; border-left:4px solid #29B5E8;
    border-radius:12px; padding:14px 16px; margin-bottom:10px;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);
    transition:transform 0.18s ease, box-shadow 0.18s ease;
}
.metric-card:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(41,181,232,0.15); }
.metric-card-green {
    background:white; border:1px solid #b7dfbf; border-left:4px solid #22c55e;
    border-radius:12px; padding:14px 16px; margin-bottom:10px;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);
    transition:transform 0.18s ease, box-shadow 0.18s ease;
}
.metric-card-green:hover { transform:translateY(-2px); box-shadow:0 6px 20px rgba(34,197,94,0.15); }
.metric-label { font-size:0.78rem; color:#5f6d7a; margin:0 0 4px; font-weight:500; letter-spacing:0.2px; }
.metric-value { font-size:1.8rem; font-weight:800; color:#1a1a2e; margin:0; letter-spacing:-1px; }
.metric-value-green { font-size:1.8rem; font-weight:800; color:#137333; margin:0; letter-spacing:-1px; }
.metric-sub { font-size:0.71rem; color:#888896; margin:3px 0 0; }
.metric-sub-green { font-size:0.71rem; color:#22a355; margin:3px 0 0; }
.metric-delta { font-size:0.82rem; color:#e05050; margin:2px 0 0; font-weight:700; }
.cite-tag { font-size:0.6rem; color:#1a7fa3; font-weight:700; vertical-align:super; margin-left:2px; }

/* Assumptions */
.assumptions-section {
    background:white; border:1px solid #e2eaf4; border-radius:14px;
    padding:24px 28px; margin-top:2rem; box-shadow:0 2px 12px rgba(0,0,0,0.04);
}
.assumptions-title { font-size:0.68rem; font-weight:800; color:#1a7fa3;
    text-transform:uppercase; letter-spacing:3px; margin:0 0 10px; }
.assumptions-desc { font-size:0.82rem; color:#52525f; margin:0 0 16px; line-height:1.7; }
.cite-legend { margin-top:16px; padding-top:14px; border-top:1px solid #e8eff8; }
.cite-legend-title { font-size:0.66rem; font-weight:800; color:#888896; text-transform:uppercase; letter-spacing:3px; margin:0 0 8px; }
.cite-row { font-size:0.78rem; color:#444452; margin:4px 0; line-height:1.5; }
.cite-key { font-weight:700; color:#1a7fa3; min-width:40px; display:inline-block; }
.assumptions-section table td, .assumptions-section table th { color:#1a1a2e!important; }

/* Download PDF button */
[data-testid="stDownloadButton"] button {
    background:linear-gradient(135deg,#0a2a5e 0%,#1460a0 100%)!important;
    color:white!important; border:none!important; border-radius:12px!important;
    padding:10px 28px!important; font-weight:700!important; font-size:0.88rem!important;
    letter-spacing:0.5px!important; box-shadow:0 4px 16px rgba(10,42,94,0.3)!important;
    transition:all 0.18s ease!important;
}
[data-testid="stDownloadButton"] button:hover {
    box-shadow:0 6px 22px rgba(10,42,94,0.45)!important; transform:translateY(-1px)!important;
}
[data-theme="dark"] [data-testid="stDownloadButton"] button {
    background:linear-gradient(135deg,#0d3060 0%,#1a5a9a 100%)!important;
    box-shadow:0 4px 16px rgba(41,181,232,0.2)!important;
}

/* Hide Streamlit heading anchor icons */
h1 a[href], h2 a[href], h3 a[href], h4 a[href] { display:none!important; }

/* ── DARK MODE OVERRIDES ──────────────────────────────────────────────────── */
[data-theme="dark"] h1, [data-theme="dark"] h2,
[data-theme="dark"] h3, [data-theme="dark"] h4 { color:#e2e8f0!important; }

/* Fix number input boxes in dark mode */
[data-theme="dark"] [data-testid="stNumberInput"] input {
    background:#1a2740!important; color:#c8daf0!important;
    border-color:#2d4060!important;
}
[data-theme="dark"] [data-testid="stNumberInput"] button {
    background:#1a2740!important; color:#c8daf0!important;
    border-color:#2d4060!important;
}
[data-theme="dark"] [data-testid="stNumberInput"] > div {
    background:#1a2740!important; border-color:#2d4060!important;
}
[data-theme="dark"] .stApp { background:linear-gradient(160deg,#0d1421 0%,#111827 100%)!important; }
[data-theme="dark"] [data-testid="stSidebar"] > div:first-child { background:linear-gradient(180deg,#131c2e 0%,#0f1826 100%)!important; }
[data-theme="dark"] .sidebar-title {
    background:linear-gradient(135deg,#29B5E8 0%,#5dd5f8 100%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
[data-theme="dark"] .ctrl-label { color:#c8daf0!important; }
[data-theme="dark"] .ctrl-label svg { color:#29B5E8; }
[data-theme="dark"] [data-testid="stSidebar"] strong { color:#445!important; }

[data-theme="dark"] [data-testid="stSidebar"] button[kind="primary"] {
    background:linear-gradient(135deg,#0a2a5e 0%,#1a4a8a 100%)!important;
    border-color:#29B5E8!important; box-shadow:0 4px 16px rgba(41,181,232,0.25)!important;
}
[data-theme="dark"] [data-testid="stSidebar"] button[kind="secondary"] {
    background:#1a2740!important; border-color:#2d4060!important; box-shadow:none!important;
}
[data-theme="dark"] [data-testid="stSidebar"] button[kind="secondary"] span[data-testid="stIconMaterial"],
[data-theme="dark"] [data-testid="stSidebar"] button[kind="secondary"] p { color:#c8daf0!important; }
[data-theme="dark"] [data-testid="stSidebar"] button[kind="secondary"]:hover { border-color:#29B5E8!important; }

[data-theme="dark"] [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background:#1a2740!important; border-color:#2d4060!important; box-shadow:none!important;
}
[data-theme="dark"] [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label p { color:#c8daf0!important; }
[data-theme="dark"] [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { border-color:#29B5E8!important; }
[data-theme="dark"] [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background:linear-gradient(135deg,#0a2a5e 0%,#1a4a8a 100%)!important;
    border-color:#29B5E8!important; box-shadow:0 4px 14px rgba(41,181,232,0.2)!important;
}
[data-theme="dark"] [data-testid="stSidebar"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p { color:white!important; }

[data-theme="dark"] [data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
    background:#1a2740!important; border-color:#2a3d58!important; box-shadow:none!important;
}
[data-theme="dark"] [data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
    border-color:#29B5E8!important; box-shadow:0 6px 20px rgba(41,181,232,0.15)!important;
}
[data-theme="dark"] [data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p:first-child { color:#e2e8f0!important; }
[data-theme="dark"] [data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child > div > p:last-child { color:#6a88a8!important; }
[data-theme="dark"] [data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
    background:linear-gradient(135deg,#0a2a5e 0%,#1a4a8a 100%)!important;
    border-color:#29B5E8!important; box-shadow:0 8px 24px rgba(10,42,94,0.5)!important;
}
[data-theme="dark"] [data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p,
[data-theme="dark"] [data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) span,
[data-theme="dark"] [data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) strong { color:white!important; }

[data-theme="dark"] .segment-header { color:#8aa0bc; }
[data-theme="dark"] .segment-header svg path { stroke:#8aa0bc; }
[data-theme="dark"] .metric-card { background:#141e30; border-color:#1e2d45; border-left-color:#29B5E8; }
[data-theme="dark"] .metric-card-green { background:#0f2018; border-color:#1e3a28; border-left-color:#22c55e; }
[data-theme="dark"] .metric-label { color:#6a88a8; }
[data-theme="dark"] .metric-value { color:#e2e8f0; }
[data-theme="dark"] .metric-value-green { color:#4ade80; }
[data-theme="dark"] .metric-sub { color:#445566; }
[data-theme="dark"] .metric-sub-green { color:#3ac870; }
[data-theme="dark"] .metric-delta { color:#f87171; }
[data-theme="dark"] .assumptions-section { background:#141e30; border-color:#1e2d45; box-shadow:none; }
[data-theme="dark"] .assumptions-title { color:#29B5E8; }
[data-theme="dark"] .assumptions-desc { color:#8aa0bc; }
[data-theme="dark"] .cite-legend { border-top-color:#1e2d45; }
[data-theme="dark"] .cite-legend-title { color:#445566; }
[data-theme="dark"] .cite-row { color:#8aa0bc; }
[data-theme="dark"] .cite-key { color:#29B5E8; }
[data-theme="dark"] .assumptions-section table thead tr { background:#1a2e50!important; }
[data-theme="dark"] .assumptions-section table th { color:#c8daf0!important; border-color:#1e2d45!important; }
[data-theme="dark"] .assumptions-section table td { color:#c8daf0!important; border-color:#1e2d45!important; background:#141e30!important; }
[data-theme="dark"] .assumptions-section table tr:nth-child(even) td { background:#1a2740!important; }

/* ── MOBILE RESPONSIVE ───────────────────────────────────────────────────── */
@media (max-width: 640px) {
    /* Hero: stack number + side text vertically so number gets full width */
    .flash_number_row {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 4px !important;
    }
    /* Side text: show inline when stacked below number */
    .flash_side {
        flex-direction: row !important;
        gap: 10px !important;
        opacity: 0.7 !important;
    }
    /* Shrink the savings number — full width now so just needs vw scaling */
    .flash_val { font-size: clamp(2.8rem, 13vw, 5rem) !important; letter-spacing: -2px !important; }
    .flash_cite { font-size: 1.0rem !important; }
    .flash_label { letter-spacing: 4px !important; font-size: 0.82rem !important; }
    .flashy-result { padding: 28px 20px !important; }

    /* Both vehicle grids: 2-col, full width, uniform 96px rows */
    [data-testid="stMain"] div[role="radiogroup"]:has(> label:nth-child(4):last-child),
    [data-testid="stMain"] div[role="radiogroup"]:has(> label:nth-child(6):last-child) {
        grid-template-columns: repeat(2, 1fr) !important;
        grid-auto-rows: 96px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        gap: 10px !important;
    }
    /* Clip cards to the row height so wrapping text can't push them taller */
    [data-testid="stMain"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        height: 96px !important;
        min-height: 96px !important;
        max-height: 96px !important;
        overflow: hidden !important;
        box-sizing: border-box !important;
    }

    /* Metric cards: reduce font size slightly */
    .metric-value, .metric-value-green { font-size: 1.4rem !important; }

    /* Block container: tighten side padding */
    .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
}

</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.markdown('<p class="sidebar-title">BYD SAVINGS<br>CALCULATOR</p>', unsafe_allow_html=True)
if "comp_mode" not in st.session_state:
    st.session_state.comp_mode = "EV"
st.sidebar.markdown("Comparison Mode")
_, mc1, mc2, _ = st.sidebar.columns([0.2, 1, 1, 0.2])
with mc1:
    if st.button("EV", key="ev_btn", icon=":material/electric_bolt:",
                 use_container_width=True,
                 type="primary" if st.session_state.comp_mode == "EV" else "secondary"):
        st.session_state.comp_mode = "EV"
        st.rerun()
with mc2:
    if st.button("PHEV", key="phev_btn", icon=":material/local_gas_station:",
                 use_container_width=True,
                 type="primary" if st.session_state.comp_mode == "PHEV" else "secondary"):
        st.session_state.comp_mode = "PHEV"
        st.rerun()
mode = st.session_state.comp_mode
st.sidebar.divider()
st.sidebar.markdown("**Controls**")

ICO_RULER   = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" style="color:inherit"><path d="M21 6.5l-3.5-3.5L3 17l3.5 3.5L21 6.5zm-14 12L4.5 16l9-9L16 9.5l-9 9zM7 16.5l1-1 1 1-1 1-1-1zm2.5-2.5l1-1 1 1-1 1-1-1zm2.5-2.5l1-1 1 1-1 1-1-1zm2.5-2.5l1-1 1 1-1 1-1-1z"/></svg>'
ICO_CAR     = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" style="color:inherit"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/></svg>'
ICO_CAL     = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" style="color:inherit"><path d="M20 3h-1V1h-2v2H7V1H5v2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 18H4V8h16v13z"/></svg>'
ICO_FUEL    = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" style="color:inherit"><path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33 0 1.38 1.12 2.5 2.5 2.5.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5S20 19.88 20 18.5V9c0-.69-.28-1.32-.73-1.77zM12 10H6V5h6v5z"/></svg>'
ICO_BOLT    = '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" style="color:inherit"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>'

def ctrl_label(icon, text):
    st.sidebar.markdown(f'<p class="ctrl-label">{icon} {text}</p>', unsafe_allow_html=True)

ctrl_label(ICO_RULER, "Distance Unit")
unit = st.sidebar.radio("Distance Unit", ["km.", "mi."], horizontal=True, label_visibility="collapsed")
if "daily_km" not in st.session_state:
    st.session_state["daily_km"] = 35
if "daily_mi" not in st.session_state:
    st.session_state["daily_mi"] = 30

if unit == "mi.":
    ctrl_label(ICO_CAR, "Daily Commute (mi.)")
    _mi_c1, _mi_c2 = st.sidebar.columns([4, 1])
    with _mi_c1:
        mi_sl = st.slider("Daily Commute (mi.)", 0, 200,
                          value=st.session_state["daily_mi"], label_visibility="collapsed")
    with _mi_c2:
        mi_ni = st.number_input("mi", min_value=0, max_value=200, step=1,
                                value=st.session_state["daily_mi"], placeholder="30", label_visibility="collapsed")
    if mi_sl != st.session_state["daily_mi"]:
        st.session_state["daily_mi"] = mi_sl
        st.rerun()
    elif mi_ni != st.session_state["daily_mi"]:
        st.session_state["daily_mi"] = int(mi_ni)
        st.rerun()
    daily_miles = float(st.session_state["daily_mi"])
else:
    ctrl_label(ICO_CAR, "Daily Commute (km.)")
    _km_c1, _km_c2 = st.sidebar.columns([4, 1])
    with _km_c1:
        km_sl = st.slider("Daily Commute (km.)", 0, 320,
                          value=st.session_state["daily_km"], label_visibility="collapsed")
    with _km_c2:
        km_ni = st.number_input("km", min_value=0, max_value=320, step=1,
                                value=st.session_state["daily_km"], placeholder="35", label_visibility="collapsed")
    if km_sl != st.session_state["daily_km"]:
        st.session_state["daily_km"] = km_sl
        st.rerun()
    elif km_ni != st.session_state["daily_km"]:
        st.session_state["daily_km"] = int(km_ni)
        st.rerun()
    daily_km_input = st.session_state["daily_km"]
    daily_miles = daily_km_input / 1.60934

if "daily_days" not in st.session_state:
    st.session_state["daily_days"] = 5

ctrl_label(ICO_CAL, "Days Driven per Week")
_d_c1, _d_c2 = st.sidebar.columns([4, 1])
with _d_c1:
    d_sl = st.slider("Days Driven per Week", 1, 7,
                     value=st.session_state["daily_days"], label_visibility="collapsed")
with _d_c2:
    d_ni = st.number_input("days", min_value=1, max_value=7, step=1,
                           value=st.session_state["daily_days"], placeholder="5", label_visibility="collapsed")
if d_sl != st.session_state["daily_days"]:
    st.session_state["daily_days"] = d_sl
    st.rerun()
elif d_ni != st.session_state["daily_days"]:
    st.session_state["daily_days"] = int(d_ni)
    st.rerun()
days_per_week = st.session_state["daily_days"]
ctrl_label(ICO_FUEL, "Fuel Price (AUD/Litre)")
fuel_price = st.sidebar.number_input("Fuel Price (AUD/Litre)", value=1.85, step=0.01, placeholder="1.85", label_visibility="collapsed")
st.sidebar.caption("Default: ABS/DISER national average. Enter your local price for accuracy.")

ctrl_label(ICO_BOLT, "Electricity Price (AUD/kWh)")
elec_price = st.sidebar.number_input("Electricity Price (AUD/kWh)", value=0.30, step=0.01, placeholder="0.30", label_visibility="collapsed")
st.sidebar.caption("Default: AEMO national average. Enter your plan's rate for accuracy.")

# ── Card Selectors ─────────────────────────────────────────────────────────────

st.markdown('<p class="segment-header">' + SVG_CAR + ' Current ICE Segment</p>', unsafe_allow_html=True)
ice_card_keys = list(ICE_SEGMENTS.keys())
ice_options = [
    "**" + k + "**\n\n" + str(v["l100"]) + " L/100km\n\n[" + v["cite"] + "]"
    for k, v in ICE_SEGMENTS.items()
]
ice_sel = st.radio("ice_seg", ice_options, index=2, label_visibility="collapsed", key="ice_radio")
ice_idx = ice_options.index(ice_sel)
selected_ice_card = ice_card_keys[ice_idx]
ice_data = ICE_SEGMENTS[selected_ice_card]
ice_name = ice_data["name"]
ice_l100 = ice_data["l100"]
ice_cite = ice_data["cite"]

if mode == "PHEV":
    st.markdown('<p class="segment-header">' + SVG_BOLT + ' Target BYD PHEV Model</p>', unsafe_allow_html=True)
    byd_card_keys = list(BYD_PHEV_MODELS.keys())
    byd_options = [
        "**" + k + "**\n\n" + str(v["val"]) + " L/100km + " + str(v["wh_km"]) + " Wh/km\n\n[" + v["cite"] + "]"
        for k, v in BYD_PHEV_MODELS.items()
    ]
    byd_sel = st.radio("byd_phev", byd_options, index=0, label_visibility="collapsed", key="phev_radio")
    byd_idx = byd_options.index(byd_sel)
    selected_byd_card = byd_card_keys[byd_idx]
    byd_data = BYD_PHEV_MODELS[selected_byd_card]
else:
    st.markdown('<p class="segment-header">' + SVG_BOLT + ' Target BYD EV Model</p>', unsafe_allow_html=True)
    byd_card_keys = list(BYD_EV_MODELS.keys())
    byd_options = [
        "**" + k + "**\n\n" + str(v["val"]) + " " + v["unit"] + "\n\n[" + v["cite"] + "]"
        for k, v in BYD_EV_MODELS.items()
    ]
    byd_sel = st.radio("byd_ev", byd_options, index=0, label_visibility="collapsed", key="ev_radio")
    byd_idx = byd_options.index(byd_sel)
    selected_byd_card = byd_card_keys[byd_idx]
    byd_data = BYD_EV_MODELS[selected_byd_card]

byd_name   = byd_data["name"]           # title case — used everywhere except card
byd_val    = byd_data["val"]
byd_unit   = byd_data["unit"]
byd_cite   = byd_data["cite"]
byd_wh_km  = byd_data.get("wh_km", 0)  # Wh/km — only present for PHEV models

# ── Calculations ───────────────────────────────────────────────────────────────
ann_miles  = daily_miles * days_per_week * 52
ann_km     = ann_miles * 1.60934
curr_ann   = (ann_km / 100) * ice_l100 * fuel_price
if mode == "PHEV":
    # Combined cost: fuel (L/100km) + electricity (Wh/km) per km driven
    new_ann = ann_km * (byd_val / 100 * fuel_price + byd_wh_km / 1000 * elec_price)
else:
    new_ann = (ann_km / 100) * byd_val * elec_price
savings    = curr_ann - new_ann
pct_saving = (savings / curr_ann * 100) if curr_ann > 0 else 0
ann_dist_display = (f"{ann_miles:,.0f}" + " mi.") if unit == "mi." else (f"{ann_km:,.0f}" + " km.")

# ── PDF Generation — title case names throughout ───────────────────────────────
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(12, 12, 12)
    W = 186  # usable width (210 - 24mm margins)

    # Header
    pdf.set_fill_color(26, 127, 163)
    pdf.rect(0, 0, 210, 20, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_y(5)
    pdf.cell(0, 8, "BYD Savings Calculator - Summary Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(0, 5, "Comparison Mode: ICE to " + mode, ln=True, align="C")
    pdf.ln(5)
    pdf.set_text_color(30, 30, 30)

    def section_title(title):
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(26, 127, 163)
        pdf.cell(0, 5, title, ln=True)
        pdf.set_text_color(30, 30, 30)

    # ── Your Selection (full width) ──
    section_title("Your Selection")
    sel_lw, sel_vw = 62, W - 62
    pdf.set_font("Helvetica", "", 8)
    rows_sel = [
        ("ICE Segment [" + ice_cite + "]",  ice_name + " - " + str(ice_l100) + " L/100km"),
        ("BYD Model [" + byd_cite + "]",    byd_name + " - " + str(byd_val) + " " + byd_unit),
        ("Annual Distance [C2]",            f"{ann_km:,.0f} km"),
        ("Days / Week",                     str(days_per_week)),
        ("Fuel Price [P1]",                 "$" + f"{fuel_price:.2f}" + " AUD/L"),
        ("Electricity Price [P2]",          "$" + f"{elec_price:.2f}" + " AUD/kWh"),
    ]
    for label, value in rows_sel:
        pdf.set_fill_color(240, 247, 255)
        pdf.cell(sel_lw, 5, label, border=1, fill=True)
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(sel_vw, 5, value, border=1, fill=True, ln=True)
    pdf.ln(2)

    # ── Results (full width) ──
    section_title("Results")
    rw = [W - 60, 40, 20]
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(224, 234, 251)
    for h, w in zip(["Metric", "Value", "Ref"], rw):
        pdf.cell(w, 5, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    rows_res = [
        ("Current ICE Annual",   "$" + f"{curr_ann:,.2f}",        "[C1]"),
        (byd_name + " Annual",   "$" + f"{new_ann:,.2f}",         "[S1]"),
        ("Annual Savings",       "$" + f"{savings:,.2f}",         "[P1]"),
        ("Monthly Saving",       "$" + f"{savings/12:,.2f}/mo",   "[S2]"),
        ("Cost Reduction",       f"{pct_saving:.1f}% cheaper",    "[V1]"),
    ]
    for lbl, val, ref in rows_res:
        pdf.cell(rw[0], 5, lbl, border=1)
        pdf.cell(rw[1], 5, val, border=1)
        pdf.cell(rw[2], 5, ref, border=1, ln=True)
    pdf.ln(2)

    # ── Assumptions ──
    section_title("Assumptions & Data Sources")
    col_w4 = [14, 52, 72, 48]
    pdf.set_fill_color(224, 234, 251)
    pdf.set_font("Helvetica", "B", 8)
    for h, w in zip(["Ref", "Parameter", "Value", "Source"], col_w4):
        pdf.cell(w, 5, h, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 7)
    assumption_rows = [
        ("[P1]",               "Fuel Price",          "$" + f"{fuel_price:.2f}" + " AUD/L",         "ABS / DISER"),
        ("[P2]",               "Electricity Price",   "$" + f"{elec_price:.2f}" + " AUD/kWh",       "AEMO"),
        ("[" + ice_cite + "]", "ICE Segment",         ice_name + ": " + str(ice_l100) + " L/100km", "Green Vehicle Guide"),
        ("[" + byd_cite + "]", byd_name + " Fuel",    str(byd_val) + " L/100km",                    "Green Vehicle Guide"),
        ("[C2]",               "Annual Distance",      f"{ann_km:,.0f} km",                          "User input"),
        ("[V1]",               "% Saving",            f"{pct_saving:.1f}% cheaper",                 "Calculated"),
    ]
    if mode == "PHEV":
        assumption_rows.insert(4, ("[" + byd_cite + "]", byd_name + " Electricity", str(byd_wh_km) + " Wh/km", "Green Vehicle Guide"))
    for row in assumption_rows:
        for i, cell in enumerate(row):
            pdf.cell(col_w4[i], 5, cell, border=1)
        pdf.ln()
    pdf.ln(2)

    # ── Citation Key ──
    section_title("Citation & Formula Key")
    pdf.set_font("Helvetica", "", 7)
    cite_lines = [
        "[P1] Fuel price - user-set or ABS/DISER avg.   [P2] Electricity price - user-set or AEMO avg.",
        "[C1] ICE Annual = (km/100) x L/100km x Fuel Price   [C2] Annual km = Daily km x Days/wk x 52",
        "[S1] BYD Annual = (km/100) x Consumption x Energy Price   [S2] Monthly Saving = C1/12 - S1/12",
        "[V1] % Saving = (ICE Annual - BYD Annual) / ICE Annual x 100   [I1-I4] ICE averages - GVG",
    ]
    if mode == "PHEV":
        cite_lines.append("[S1] PHEV = km x (L/100km/100 x Fuel$ + Wh/km/1000 x Elec$)")
    if mode == "EV":
        cite_lines.append("  ".join("[D"+str(i)+"] "+v["name"]+": "+str(v["val"])+" kWh/100km"
                                    for i,(k,v) in enumerate(BYD_EV_MODELS.items(),1)))
    else:
        cite_lines.append("  ".join("[D"+str(i)+"] "+v["name"]+": "+str(v["val"])+"L+"+str(v["wh_km"])+"Wh/km"
                                    for i,(k,v) in enumerate(BYD_PHEV_MODELS.items(),1)))
    for line in cite_lines:
        pdf.set_x(12)
        pdf.multi_cell(W, 4, line)
    pdf.ln(2)

    # ── Disclaimer ──
    pdf.set_fill_color(240, 247, 255)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_x(12)
    pdf.multi_cell(W, 4,
        "GENERAL ESTIMATE ONLY. Indicative figures only - not financial advice. Based on user inputs "
        "and national averages. Individual results will vary. BYD data: greenvehicleguide.gov.au. "
        "Fuel default: ABS/DISER. Electricity default: AEMO.",
        border=1, fill=True)
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 6)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 4, "General estimates only. Not financial advice. Sources: ABS, DISER, AEMO, Green Vehicle Guide.", ln=True, align="C")

    return bytes(pdf.output())

# ── Hero ───────────────────────────────────────────────────────────────────────
segment_note_html = (
    "<br><strong>Segment note:</strong> For accurate comparisons, use vehicles of the same segment "
    "(e.g. small hatch vs. small hatch). Mixing segments will produce misleading results."
)

disclaimer_text = (
    '<strong>General Estimate Only.</strong> This calculator provides indicative figures and does not '
    'constitute financial advice. Results are based on user-provided inputs and national averages. '
    'Individual results will vary. Individual results may still vary based on driving habits. '
    'Not a substitute for professional financial or automotive advice.'
    + segment_note_html
)

hero_html = (
    '<div class="flashy-result">'
      '<p class="flash_label">Estimated Annual Savings</p>'
      '<div class="flash_number_row">'
        '<h1 class="flash_val">$' + f"{savings:,.2f}" + '<span style="font-size:1em;font-weight:900;opacity:0.75;margin-left:0.18em;">AUD</span><sup class="flash_cite"> *[P1]</sup></h1>'
        '<div class="flash_side">'
          '<span class="flash_unit">Indicative Estimate</span>'
          '<span class="flash_unit">AUD per Year</span>'
        '</div>'
      '</div>'
      '<div class="flash_disclaimer">' + disclaimer_text + '</div>'
    '</div>'
)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown(hero_html, unsafe_allow_html=True)

# ── Download Button — placed near the hero ─────────────────────────────────────
pdf_bytes = generate_pdf()
st.download_button(
    label="Download as PDF",
    data=pdf_bytes,
    file_name="BYD_Savings_Summary.pdf",
    mime="application/pdf"
)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ── Chart + Key Metrics — use title case names ─────────────────────────────────
col_chart, col_stats = st.columns([1.2, 1], gap="large")

with col_chart:
    st.markdown('<h3 style="color:#0d2a4a;font-weight:800;margin-bottom:4px;font-size:1.35rem;letter-spacing:-0.3px;">Cost Comparison</h3>', unsafe_allow_html=True)
    chart_df = pd.DataFrame({
        "Vehicle": [ice_name, byd_name],
        "Annual Cost (AUD)": [round(curr_ann, 2), round(new_ann, 2)]
    })
    LABEL_CLR = "#627386"
    GRID_CLR  = "#dce8f5"
    chart = alt.Chart(chart_df).mark_bar(
        cornerRadiusTopLeft=8, cornerRadiusTopRight=8, size=72
    ).encode(
        x=alt.X("Vehicle:N", axis=alt.Axis(
            labelAngle=0, title=None, labelFontSize=13, labelFont="Montserrat",
            labelColor=LABEL_CLR, tickColor="transparent", domainColor="transparent"
        )),
        y=alt.Y("Annual Cost (AUD):Q", axis=alt.Axis(
            title="Annual Cost (AUD)", titleFont="Montserrat", titleFontSize=11,
            titleColor=LABEL_CLR, labelFont="Montserrat", labelFontSize=11,
            labelColor=LABEL_CLR, gridColor=GRID_CLR,
            tickColor="transparent", domainColor="transparent"
        )),
        color=alt.Color("Vehicle:N",
            scale=alt.Scale(domain=[ice_name, byd_name], range=["#0d3d7a", "#29B5E8"]),
            legend=alt.Legend(title=None, labelFont="Montserrat", labelFontSize=12,
                labelColor=LABEL_CLR, symbolType="square", symbolSize=120,
                orient="bottom", columns=2)
        ),
        tooltip=[
            alt.Tooltip("Vehicle:N", title="Vehicle"),
            alt.Tooltip("Annual Cost (AUD):Q", title="Annual Cost (AUD)", format="$,.2f")
        ]
    ).properties(
        height=481, background="transparent",
        padding={"left": 8, "right": 36, "top": 8, "bottom": 8}
    )
    st.altair_chart(chart, use_container_width=True, theme=None)

with col_stats:
    st.markdown('<h3 style="color:#0d2a4a;font-weight:800;margin-bottom:4px;font-size:1.35rem;letter-spacing:-0.3px;">Key Metrics</h3>', unsafe_allow_html=True)
    metrics_html = (
        '<div class="metric-card">'
          '<p class="metric-label">Current Monthly</p>'
          '<p class="metric-value">$' + f"{curr_ann/12:,.2f}" + '<sup class="cite-tag">[C1]</sup></p>'
          '<p class="metric-sub">' + ice_name + ' · ' + str(ice_l100) + ' L/100km <sup>[' + ice_cite + ']</sup></p>'
        '</div>'
        '<div class="metric-card">'
          '<p class="metric-label">' + byd_name + ' Monthly</p>'
          '<p class="metric-value">$' + f"{new_ann/12:,.2f}" + '<sup class="cite-tag">[S1]</sup></p>'
          '<p class="metric-delta">&#8595; &minus;$' + f"{savings/12:,.2f}" + '/mo vs ICE <sup class="cite-tag">[S2]</sup></p>'
          '<p class="metric-sub">' + (str(byd_val) + ' L/100km + ' + str(byd_wh_km) + ' Wh/km' if mode == "PHEV" else str(byd_val) + ' ' + byd_unit) + ' <sup>[' + byd_cite + ']</sup></p>'
        '</div>'
        '<div class="metric-card">'
          '<p class="metric-label">Annual Distance</p>'
          '<p class="metric-value">' + ann_dist_display + '<sup class="cite-tag">[C2]</sup></p>'
          '<p class="metric-sub">' + str(days_per_week) + ' days/week &times; 52 weeks</p>'
        '</div>'
        '<div class="metric-card-green">'
          '<p class="metric-label" style="color:#137333;">Estimated Value</p>'
          '<p class="metric-value-green">' + f"{pct_saving:.1f}" + '% cheaper<sup class="cite-tag">[V1]</sup></p>'
          '<p class="metric-sub-green">vs ' + ice_name + '</p>'
        '</div>'
    )
    st.markdown(metrics_html, unsafe_allow_html=True)

# ── Assumptions — title case names ────────────────────────────────────────────
if mode == "PHEV":
    mode_rows = (
        '<tr>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">PHEV Fuel Consumption <sup>[' + byd_cite + ']</sup></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">' + byd_name + ': <strong>' + str(byd_val) + ' L/100km</strong></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></td>'
        '</tr>'
        '<tr>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">PHEV Electricity Consumption <sup>[' + byd_cite + ']</sup></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">' + byd_name + ': <strong>' + str(byd_wh_km) + ' Wh/km</strong></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></td>'
        '</tr>'
        '<tr>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">Electricity Price <sup>[P2]</sup></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><strong>$' + f"{elec_price:.2f}" + ' AUD/kWh</strong> (user-set; default: AEMO national avg.)</td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.aemo.com.au" target="_blank">AEMO</a></td>'
        '</tr>'
    )
else:
    mode_rows = (
        '<tr>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">EV Consumption <sup>[' + byd_cite + ']</sup></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">' + byd_name + ': <strong>' + str(byd_val) + ' kWh/100km</strong></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></td>'
        '</tr>'
        '<tr>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;">Electricity Price <sup>[P2]</sup></td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><strong>$' + f"{elec_price:.2f}" + ' AUD/kWh</strong> (user-set; default: AEMO national avg.)</td>'
        '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><a href="https://www.aemo.com.au" target="_blank">AEMO</a></td>'
        '</tr>'
    )

d_cite_rows = ""
if mode == "EV":
    for i, (k, v) in enumerate(BYD_EV_MODELS.items(), 1):
        d_cite_rows += (
            '<p class="cite-row"><span class="cite-key"><sup>[D' + str(i) + ']</sup></span> '
            + v["name"] + ' &mdash; ' + str(v["val"]) + ' kWh/100km. '
            'Source: <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
        )
else:
    for i, (k, v) in enumerate(BYD_PHEV_MODELS.items(), 1):
        d_cite_rows += (
            '<p class="cite-row"><span class="cite-key"><sup>[D' + str(i) + ']</sup></span> '
            + v["name"] + ' &mdash; ' + str(v["val"]) + ' L/100km + ' + str(v["wh_km"]) + ' Wh/km. '
            'Source: <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
        )

p2_row = ""
if mode == "EV":
    p2_row = (
        '<p class="cite-row"><span class="cite-key"><sup>[P2]</sup></span> '
        'Electricity price &mdash; user-set or AEMO national average. '
        'Source: <a href="https://www.aemo.com.au" target="_blank">AEMO</a></p>'
    )

assumptions_html = (
    '<div class="assumptions-section" id="citation-table">'
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
    '<td style="padding:7px 10px;border:1px solid #e0eaf3;"><strong>' + ice_name + ': ' + str(ice_l100) + ' L/100km</strong></td>'
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
    '<p class="cite-row"><span class="cite-key"><sup>[I1]</sup></span> Average Hatchback: 6.2 L/100km &mdash; <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
    '<p class="cite-row"><span class="cite-key"><sup>[I2]</sup></span> Average Sedan: 6.8 L/100km &mdash; <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
    '<p class="cite-row"><span class="cite-key"><sup>[I3]</sup></span> Average Small SUV: 7.5 L/100km &mdash; <a href="https://www.greenvehicleguide.gov.au" target="_blank">Green Vehicle Guide</a></p>'
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
