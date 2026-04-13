# BYD Savings Calculator

A free, browser-based savings calculator for BYD Australia sales consultants. Shows customers how much they could save annually by switching from their current petrol or diesel vehicle to a BYD electric (EV) or plug-in hybrid (PHEV) model.

**Live app:** [bydsavingscalculator.streamlit.app](https://bydsavingscalculator.streamlit.app)

---

## What it does

The consultant enters three pieces of information from the customer:

1. How far they drive each day (km or miles)
2. How many days a week they drive
3. What type of vehicle they currently drive

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

```bash
git clone https://github.com/konganer-afk/oilconsumption.git
cd oilconsumption
pip install -r requirements.txt
streamlit run streamlit_app.py
```

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
