# Hybrid Microgrid Sizing Optimization and EMS Simulation

This project is an end-to-end engineering tool developed to perform hourly simulation, Energy Management System (EMS) modeling, and Capital Expenditure (CAPEX)-focused hardware capacity optimization for an off-grid hybrid microgrid system.

The system consists of Solar Panels (PV), a Wind Turbine, and a Battery Energy Storage System (BESS). It is designed to meet the 1-year (8760 hours) electrical load of a typical agricultural irrigation pump in the Black Sea region with near-zero power outages.

## 🛠️ Technological Infrastructure and Software Architecture

The project features a hybrid architecture combining the strengths of two different platforms:
1. **Python (Data and Simulation Engine):** Utilizing Pandas and NumPy, the 8760-hour meteorological data and load profiles are processed, and generation models are simulated using vectorized physics equations.
2. **GNU Octave / MATLAB (Optimization Engine):** A custom Grid Search algorithm tests dozens of different hardware combinations to determine the "Golden Ratio" that sustains the system at the lowest possible cost.

---

## 📊 Mathematical Infrastructure and Modeling

### 1. Power Generation Models
* **Solar Power Output (kW):**
  $$P_{pv} = \frac{A \cdot \eta \cdot G}{1000}$$
  *(A: Panel Area [m²], $\eta$: Panel Efficiency [20%], G: Solar Radiation [W/m²])*

* **Wind Power Output (kW):**
  $$P_{wind} = \frac{0.5 \cdot \rho \cdot A_{swept} \cdot C_p \cdot v^3}{1000}$$
  *($\rho$: Air Density [1.225 kg/m³], $A_{swept}$: Swept Area [20 m²], $C_p$: Power Coefficient [0.35], v: Wind Speed [m/s])*

### 2. Reliability Metric (LPSP)
The electrical reliability of the system is measured by the Loss of Power Supply Probability (LPSP):
$$LPSP = \frac{\sum P_{unmet}}{\sum P_{load}}$$

---

## 🚀 Folder Structure

```text
Microgrid_Project/
├── analysis/          # Simulation outputs, logs, and 3D surface plots
├── data/              # Weather and agricultural load data profiles
├── docs/              # Project technical reports and presentation documents
├── scripts/           # Python simulation and Octave optimization scripts
└── README.md          # Main project documentation

```

## 📈 Optimization Results (The Golden Ratio)

In the initial design (Baseline), randomly selected hardware sizes led to high outage rates (18.9% LPSP) and high unit costs. As a result of the CAPEX-Focused Grid Search Algorithm run on Octave, the **Golden Ratio** was discovered, maintaining the system at the highest reliability with the minimum possible budget:

| Metric / Hardware | Initial Design (Baseline) | Optimized System (Optimum) |
| --- | --- | --- |
| **Solar Panel Area** | 50 m² | **75 m²** |
| **Battery Capacity** | 20 kWh | **40 kWh** |
| **Annual Outage Rate (LPSP)** | 18.94% | **0.64% (Excellent)** |
| **Initial Investment (CAPEX)** | $20,500 | **$30,250** |

### Optimization Decision Surfaces

The cost and reliability variations across the system's search space were analyzed using 3D surface plots:

* **CAPEX Surface:** Demonstrates that the cost increases linearly as the hardware size grows.
* **LPSP Cliff:** Visualizes how the high risk of outage at small capacities plunges to zero once the optimum point is reached.

*The graphical output is located at `analysis/optimization_surfaces.png`.*

---

## 💻 Installation and Usage

### Prerequisites

* Python 3.10+ (Pandas, NumPy, Matplotlib)
* GNU Octave (or MATLAB)

### Execution Steps

1. **Run the Simulation:** First, execute the Python script to generate the baseline generation profiles:
```bash
python scripts/generate_final_engineering_report.py

```


2. **Run the Optimization:** Feed the generated data into the Octave matrix engine to perform the cost-focused capacity scan:
```bash
cd scripts
octave microgrid_optimizer.m

```


---

## 📄 License

This project is an engineering study developed for educational and research purposes.
