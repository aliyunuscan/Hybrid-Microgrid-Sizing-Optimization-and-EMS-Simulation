import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def generate_final_engineering_report():
    print("Starting Final Optimized Microgrid Simulation...")

    # Define paths
    project_dir = "/home/ayunusc/Desktop/Microgrid_Project"
    data_dir = os.path.join(project_dir, "data")
    analysis_dir = os.path.join(project_dir, "analysis")
    
    # NEW FILE NAME: To prevent overwriting and mixing with old baseline data
    output_path = os.path.join(analysis_dir, "optimized_simulation_results.csv")

    # 1. LOAD DATA
    weather_path = os.path.join(data_dir, "weather_profile.csv")
    load_path = os.path.join(data_dir, "agricultural_load.csv")

    try:
        df_weather = pd.read_csv(weather_path, parse_dates=['Datetime'], index_col='Datetime')
        df_load = pd.read_csv(load_path, parse_dates=['Datetime'], index_col='Datetime')
        df = pd.concat([df_weather, df_load], axis=1)
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # =======================================================
    # 2. THE GOLDEN RATIO PARAMETERS (From Octave Optimization)
    # =======================================================
    SOLAR_AREA_M2 = 75.0              # Optimized Panel Area
    BATTERY_CAPACITY_KWH = 40.0       # Optimized Battery Capacity
    
    PV_EFFICIENCY = 0.20       
    AIR_DENSITY = 1.225        
    SWEPT_AREA_M2 = 20.0       
    POWER_COEFF = 0.35         
    
    INITIAL_SOC = 1.0                 
    MIN_SOC = 0.20                    
    MAX_SOC = 1.0                     

    # 3. CALCULATE POWER GENERATION
    print("Calculating optimized generation profiles...")
    df['Solar_Power_kW'] = (SOLAR_AREA_M2 * PV_EFFICIENCY * df['Solar_Radiation_W_m2']) / 1000.0
    df['Wind_Power_kW'] = (0.5 * AIR_DENSITY * SWEPT_AREA_M2 * POWER_COEFF * (df['Wind_Speed_10m_m_s']**3)) / 1000.0
    df['Net_Power_kW'] = df['Solar_Power_kW'] + df['Wind_Power_kW'] - df['Load_kW']
    df['Total_Generated_Power_kW'] = df['Solar_Power_kW'] + df['Wind_Power_kW']

    # 4. ENERGY MANAGEMENT SYSTEM (EMS)
    print("Running Energy Management System...")
    battery_energy = np.zeros(len(df))
    unmet_load = np.zeros(len(df))
    dumped_energy = np.zeros(len(df))
    current_energy = BATTERY_CAPACITY_KWH * INITIAL_SOC
    
    for i, p_net in enumerate(df['Net_Power_kW']):
        current_energy += p_net
        if current_energy > (BATTERY_CAPACITY_KWH * MAX_SOC):
            dumped_energy[i] = current_energy - (BATTERY_CAPACITY_KWH * MAX_SOC)
            current_energy = BATTERY_CAPACITY_KWH * MAX_SOC
            unmet_load[i] = 0.0
        elif current_energy < (BATTERY_CAPACITY_KWH * MIN_SOC):
            unmet_load[i] = (BATTERY_CAPACITY_KWH * MIN_SOC) - current_energy
            current_energy = BATTERY_CAPACITY_KWH * MIN_SOC
            dumped_energy[i] = 0.0
        else:
            unmet_load[i] = 0.0
            dumped_energy[i] = 0.0
        battery_energy[i] = current_energy

    df['Battery_Energy_kWh'] = battery_energy
    df['Battery_SoC_%'] = (df['Battery_Energy_kWh'] / BATTERY_CAPACITY_KWH) * 100
    df['Unmet_Load_kWh'] = unmet_load
    df['Dumped_Energy_kWh'] = dumped_energy

    # Save the optimized results
    os.makedirs(analysis_dir, exist_ok=True)
    df.to_csv(output_path)
    print("Optimized Data Saved.")

    # =======================================================
    # 5. FINAL ENGINEERING VISUALIZATIONS
    # =======================================================
    print("\nGenerating Final Engineering Reports...")
    plt.style.use('seaborn-whitegrid')

    # --- GRAPH 1: 1-YEAR BATTERY STRESS TEST (SoC Curve) ---
    fig1, ax1 = plt.subplots(figsize=(16, 5))
    ax1.plot(df.index.to_numpy(), df['Battery_SoC_%'].to_numpy(), color='#27ae60', linewidth=0.5)
    ax1.fill_between(df.index.to_numpy(), 0, 20.0, color='#e74c3c', alpha=0.3, label='Critical Zone (<20%)')
    ax1.axhline(20.0, color='#c0392b', linestyle=':', linewidth=1.5)
    
    ax1.set_title('Annual Battery State of Charge (SoC) - Seasonal Stress Analysis', fontsize=14, fontweight='bold')
    ax1.set_ylabel('State of Charge (%)', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, 105)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%B')) # Display only month names
    ax1.legend(loc='lower right')
    fig1.tight_layout()

    soc_graph_path = os.path.join(analysis_dir, "annual_soc_curve.png")
    fig1.savefig(soc_graph_path, dpi=300, bbox_inches='tight')
    print(f"SUCCESS: SoC Curve saved to -> {soc_graph_path}")

    # --- GRAPH 2: ENERGY DISTRIBUTION (Stacked Area Chart) - Mid-Winter (January Example) ---
    # A full 1-year stacked area chart is unreadable; displaying a 1-week sample of system stress is academic standard.
    plot_start = '2023-01-10'
    plot_end = '2023-01-17'
    df_week = df.loc[plot_start:plot_end]

    fig2, ax2 = plt.subplots(figsize=(16, 7))
    
    # Prepare data for Stacked Area
    x_axis = df_week.index.to_numpy()
    solar = df_week['Solar_Power_kW'].to_numpy()
    wind = df_week['Wind_Power_kW'].to_numpy()
    load = df_week['Load_kW'].to_numpy()

    # Stack Wind and Solar generations (Stackplot)
    ax2.stackplot(x_axis, wind, solar, labels=['Wind Generation', 'Solar Generation'], colors=['#3498db', '#f1c40f'], alpha=0.7)
    
    # Show Pump Load Demand with sharp step lines
    ax2.step(x_axis, load, color='#2c3e50', linewidth=2.5, linestyle='--', where='post', label='Agricultural Pump Load')

    ax2.set_title('Microgrid Energy Distribution and Load Fulfillment (Winter Period)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Power (kW)', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper left', frameon=True, shadow=True)
    ax2.set_ylim(bottom=0)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M'))
    
    fig2.tight_layout()

    energy_dist_path = os.path.join(analysis_dir, "winter_energy_distribution.png")
    fig2.savefig(energy_dist_path, dpi=300, bbox_inches='tight')
    print(f"SUCCESS: Energy Distribution saved to -> {energy_dist_path}")

    # Display the graphs
    plt.show()

if __name__ == "__main__":
    generate_final_engineering_report()