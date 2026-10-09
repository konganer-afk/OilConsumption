# BYD Savings Calculator

# ⛽ BYD Savings Calculator
A free, browser-based savings calculator for BYD Australia sales consultants. Shows customers how much they could save annually by switching from their current petrol or diesel vehicle to a BYD electric (EV) or plug-in hybrid (PHEV) model.

**Live app:** [bydsavingscalculator.streamlit.app](https://bydsavingscalculator.streamlit.app)

## 🚀 Features
* **Dual-Unit Support:** Seamlessly toggle between Miles and Kilometers.
* **Dynamic UI:** Custom CSS styling featuring a high-contrast "Hero" section for immediate financial impact.
* **Real-time Logic:** Instant calculation of annual and monthly costs based on commute distance and fuel prices (AUD).
* **Visual Insights:** Interactive bar charts comparing current vs. new vehicle efficiency.
* **Efficiency Metrics:** Automatic calculation of percentage savings.
* **EV and PHEV Modes:** Compare your current petrol vehicle against a BYD battery-electric or plug-in hybrid.
* **Dropdown Selectors:** Pick the current ICE segment and the target BYD model from drop-down menus.
* **PDF Report:** Download a summary with the full assumptions and citation key.
* **Anonymous Usage Tracking:** Optional Google Sheets log of `app_visit` and `pdf_download` events with a per-tab `session_id` (columns: `timestamp`, `event`, `session_id`).

## 📚 Data Sources
All vehicle data lives in the dictionaries at the top of `streamlit_app.py`; the assumptions table, PDF and citation numbers are generated from them. New entries must be appended in order so the citation numbers stay in sync.

| Dictionary | Entries | Source |
|---|---|---|
| `ICE_SEGMENTS` | 12 average segments: Light, Small, Medium, Large, Upper Large, Small SUV, Medium SUV, Large SUV, People Mover, Small Van, Large Van, Ute (5.9-9.6 L/100km WLTP) | Electric Vehicle Council, *Lifecycle Emissions Calculator Explainer*, Table 1, Nov 2023 (I1-I12) |
| `BYD_EV_MODELS` | Atto 1, Atto 2, Atto 3, Atto 3 EVO Dynamic*, Atto 3 EVO Premium, Dolphin, Seal, Sealion 7 (kWh/100km) | Green Vehicle Guide (D1-D8) |
| `BYD_PHEV_MODELS` | Sealion 5, 6, 8, Shark 6, Seal 6, Seal 6 Touring, Atto 2 DM-i Premium / Essential, M9 Premium / Dynamic (L/100km + Wh/km) | Green Vehicle Guide; Seal 6 models from BYD AU brochures (D1-D10) |

\* The Atto 3 EVO Dynamic figure is on the NEDC test cycle; all other figures are WLTP.
---

## What it does

## 📊 How It Works
The app calculates savings using the following logic:
1.  **Distance Normalization:** Converts all inputs to an annual kilometer total ($AKM$).
2.  **Consumption Formula:** Calculates fuel cost based on $L/100km$ efficiency:
    $$\text{Annual Cost} = \left( \frac{AKM}{100} \right) \times \text{Efficiency} \times \text{Fuel Price}$$
3.  **PHEV Formula:** PHEVs use both fuel and electricity per km driven:
    $$\text{Annual Cost} = AKM \times \left( \frac{L/100km}{100} \times \text{Fuel Price} + \frac{Wh/km}{1000} \times \text{Electricity Price} \right)$$
    EV consumption is stored as kWh/100km (Green Vehicle Guide Wh/km ÷ 10).
4.  **Delta Analysis:** Subtracts the new vehicle cost from the current cost to display total annual savings.
The consultant enters three pieces of information from the customer:

1. How far they drive each day (km or miles)
2. How many days a week they drive
3. What type of vehicle they currently drive

### Prerequisites
Ensure you have Python installed, then install the required dependencies:
```bash
pip install -r requirements.txt
The calculator instantly shows the estimated annual fuel cost saving, a monthly breakdown, a cost comparison chart, and a downloadable PDF the customer can take home.

---

## Features

- **EV and PHEV modes** — toggle between ICE-to-EV and ICE-to-PHEV comparison
- **5 ICE segment options** — Average Light Car, Small Car, Medium Car, Small SUV, Ute — all sourced from the Electric Vehicle Council
- **6 BYD EV models** — Atto 1, Atto 2, Atto 3, Dolphin, Seal, Sealion 7 — consumption data from Green Vehicle Guide
- **4 BYD PHEV models** — Sealion 5, Sealion 6, Sealion 8, Shark 6 — dual fuel + electricity calculation
- **Slider + number input** — drag or type the exact value
- **Editable price inputs** — fuel and electricity prices default to national averages but can be overridden
- **PDF download** — generates a real server-side PDF with all inputs, results, assumptions and citations
- **Dark mode** — full dark mode support
- **Mobile responsive** — works on tablets and phones for dealership use

---

## Data sources

| Data | Source |
|---|---|
| ICE segment fuel consumption (L/100km, WLTP) | Electric Vehicle Council, *Lifecycle Emissions Calculator Explainer*, Table 1, Nov 2023 |
| BYD EV consumption (kWh/100km) | Green Vehicle Guide (greenvehicleguide.gov.au) |
| BYD PHEV consumption (L/100km + Wh/km) | Green Vehicle Guide (greenvehicleguide.gov.au) |
| Fuel price default ($1.85 AUD/L) | ABS / DISER national average |
| Electricity price default ($0.30 AUD/kWh) | AEMO national average |

### ICE segment figures

| Segment | L/100km (WLTP) | EVC Segment |
|---|---|---|
| Average Light Car | 5.9 | Light |
| Average Small Car | 7.5 | Small |
| Average Medium Car | 7.9 | Medium |
| Average Small SUV | 7.3 | Small SUV |
| Average Ute | 9.3 | Ute |

### BYD EV models

| Model | kWh/100km |
|---|---|
| BYD Atto 1 | 15.5 |
| BYD Atto 2 | 17.0 |
| BYD Atto 3 | 14.8 |
| BYD Dolphin | 12.6 |
| BYD Seal | 13.8 |
| BYD Sealion 7 | 17.9 |

### BYD PHEV models

| Model | L/100km | Wh/km |
|---|---|---|
| BYD Sealion 5 | 1.2 | 120 |
| BYD Sealion 6 | 1.1 | 169 |
| BYD Sealion 8 | 1.1 | 150 |
| BYD Shark 6 | 2.0 | 212 |

---

## Calculation methodology

**EV annual cost:**
```
Annual Cost = (Annual km / 100) × kWh/100km × Electricity Price
```

**PHEV annual cost (combined fuel + electricity):**
```
Annual Cost = Annual km × (L/100km / 100 × Fuel Price + Wh/km / 1000 × Electricity Price)
```

**Annual distance:**
```
Annual km = Daily km × Days per week × 52 weeks
```

**Annual saving:**
```
Saving = ICE Annual Cost − BYD Annual Cost
```

---

## Tech stack

- **Python** + **Streamlit** — app framework
- **Altair** — bar chart
- **fpdf2** — server-side PDF generation
- **Montserrat** (Google Fonts) — typography

---

## Installation

### Running the App
1. Clone this repository.
2. Launch the Streamlit server:
```bash
```bash
git clone https://github.com/konganer-afk/oilconsumption.git
cd oilconsumption
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Usage tracking is optional: it needs a `gcp_service_account` entry in Streamlit secrets and is skipped otherwise.

**requirements.txt:**
```
streamlit
pandas
altair
fpdf2
```

---

## Deployment

Deployed on [Streamlit Community Cloud](https://streamlit.io/cloud) from the `main` branch. Every push to `main` triggers an automatic redeploy.

---

## Disclaimer

This calculator provides indicative figures only and does not constitute financial advice. Results are based on user-provided inputs and national averages. Individual results will vary depending on driving habits, vehicle condition, and local fuel and electricity prices. Not a substitute for professional financial or automotive advice.

---

## Licence

Internal tool — BYD Australia. Not for public redistribution.
