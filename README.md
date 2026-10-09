
# ⛽ BYD Savings Calculator

A high-performance, visually striking **Streamlit** dashboard designed to calculate and visualize annual fuel savings when switching from a standard internal combustion engine (ICE) to a dual-mode/hybrid vehicle.

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

## 🛠️ Tech Stack
* **Python 3.x**
* **Streamlit:** For the web interface and dashboard layout.
* **Pandas:** For data handling and chart generation.
* **Custom CSS:** Injected via `st.markdown` for professional branding and typography.

## 📊 How It Works
The app calculates savings using the following logic:
1.  **Distance Normalization:** Converts all inputs to an annual kilometer total ($AKM$).
2.  **Consumption Formula:** Calculates fuel cost based on $L/100km$ efficiency:
    $$\text{Annual Cost} = \left( \frac{AKM}{100} \right) \times \text{Efficiency} \times \text{Fuel Price}$$
3.  **PHEV Formula:** PHEVs use both fuel and electricity per km driven:
    $$\text{Annual Cost} = AKM \times \left( \frac{L/100km}{100} \times \text{Fuel Price} + \frac{Wh/km}{1000} \times \text{Electricity Price} \right)$$
    EV consumption is stored as kWh/100km (Green Vehicle Guide Wh/km ÷ 10).
4.  **Delta Analysis:** Subtracts the new vehicle cost from the current cost to display total annual savings.

## 🏃 Getting Started

### Prerequisites
Ensure you have Python installed, then install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the App
1. Clone this repository.
2. Launch the Streamlit server:
```bash
streamlit run streamlit_app.py
```
Usage tracking is optional: it needs a `gcp_service_account` entry in Streamlit secrets and is skipped otherwise.

## 📸 Dashboard Preview
The dashboard features a **Sidebar Control Panel** for user inputs and a **Main Stage** for high-level metrics, including:
* **Annual Savings Hero:** A gradient-styled card showing the total yearly benefit.
* **Cost Comparison Chart:** A visual breakdown of ICE vs. Dual Mode costs.
* **Key Metrics:** Monthly breakdowns and distance tracking.

---

### 📝 License
This project is open-source and available under the MIT License.

---
