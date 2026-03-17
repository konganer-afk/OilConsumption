
# ⛽ Dual Mode Fuel Savings Calculator

A high-performance, visually striking **Streamlit** dashboard designed to calculate and visualize annual fuel savings when switching from a standard internal combustion engine (ICE) to a dual-mode/hybrid vehicle.

## 🚀 Features
* **Dual-Unit Support:** Seamlessly toggle between Miles and Kilometers.
* **Dynamic UI:** Custom CSS styling featuring a high-contrast "Hero" section for immediate financial impact.
* **Real-time Logic:** Instant calculation of annual and monthly costs based on commute distance and fuel prices (AUD).
* **Visual Insights:** Interactive bar charts comparing current vs. new vehicle efficiency.
* **Efficiency Metrics:** Automatic calculation of percentage savings.

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
3.  **Delta Analysis:** Subtracts the new vehicle cost from the current cost to display total annual savings.

## 🏃 Getting Started

### Prerequisites
Ensure you have Python installed, then install the required dependencies:
```bash
pip install streamlit pandas
```

### Running the App
1. Clone this repository or save the code to `app.py`.
2. Launch the Streamlit server:
```bash
streamlit run app.py
```

## 📸 Dashboard Preview
The dashboard features a **Sidebar Control Panel** for user inputs and a **Main Stage** for high-level metrics, including:
* **Annual Savings Hero:** A gradient-styled card showing the total yearly benefit.
* **Cost Comparison Chart:** A visual breakdown of ICE vs. Dual Mode costs.
* **Key Metrics:** Monthly breakdowns and distance tracking.

---

### 📝 License
This project is open-source and available under the MIT License.

---
