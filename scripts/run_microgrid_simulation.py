import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def run_microgrid_simulation():
    print("Starting Microgrid Simulation...")

    # Define paths
    project_dir = "/home/ayunusc/Desktop/Microgrid_Project"
    analysis_dir = os.path.join(project_dir, "analysis")
    output_path = os.path.join(analysis_dir, "simulation_results.csv")

    # ==========================================
    # CACHE CHECK: DOES THE RESULT ALREADY EXIST?
    # ==========================================
    if os.path.exists(output_path):
        print("\n--- EXISTING SIMULATION FOUND ---")
        print(f"Loading 1-year data directly from: {output_path}")
        print("Skipping recalculation to save time...")
        # Read the already calculated data
        df = pd.read_csv(output_path, parse_dates=['Datetime'], index_col='Datetime')
        
    else:
        print("\n--- NO PREVIOUS SIMULATION FOUND. STARTING CALCULATION ---")
        # 1. LOAD AND MERGE RAW DATA
        data_dir = os.path.join(project_dir, "data")
        weather_path = os.path.join(data_dir, "weather_profile.csv")
        load_path = os.path.join(data_dir, "agricultural_load.csv")

        try:
            df_weather = pd.read_csv(weather_path, parse_dates=['Datetime'], index_col='Datetime')
            df_load = pd.read_csv(load_path, parse_dates=['Datetime'], index_col='Datetime')
            df = pd.concat([df_weather, df_load], axis=1)
            print("Raw data successfully loaded and merged.")
        except Exception as e:
            print(f"Error loading data: {e}")
            return

        # 2. SYSTEM PARAMETERS (HARDWARE SPECIFICATIONS)
        SOLAR_AREA_M2 = 50.0       # A: Total panel area in m^2
        PV_EFFICIENCY = 0.20       # ETA: 20% efficiency
        AIR_DENSITY = 1.225        # Rho: kg/m^3
        SWEPT_AREA_M2 = 20.0       # A: Rotor swept area in m^2
        POWER_COEFF = 0.35         # Cp: Power coefficient
        
        BATTERY_CAPACITY_KWH = 20.0       # Total battery capacity
        INITIAL_SOC = 1.0                 # Start at 100% full
        MIN_SOC = 0.20                    # Minimum safe state of charge (20%)
        MAX_SOC = 1.0                     # Maximum state of charge (100%)

        # 3. CALCULATE POWER GENERATION
        print("Calculating generation profiles...")
        df['Solar_Power_kW'] = (SOLAR_AREA_M2 * PV_EFFICIENCY * df['Solar_Radiation_W_m2']) / 1000.0
        df['Wind_Power_kW'] = (0.5 * AIR_DENSITY * SWEPT_AREA_M2 * POWER_COEFF * (df['Wind_Speed_10m_m_s']**3)) / 1000.0
        df['Net_Power_kW'] = df['Solar_Power_kW'] + df['Wind_Power_kW'] - df['Load_kW']
        
        # Add the specific requested metric: Total Generated Energy
        df['Total_Generated_Power_kW'] = df['Solar_Power_kW'] + df['Wind_Power_kW']

        # 4. ENERGY MANAGEMENT SYSTEM (EMS) - STATE MACHINE
        print("Running Energy Management System (Battery Logic)...")
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

        # Assign EMS results back to DataFrame
        df['Battery_Energy_kWh'] = battery_energy
        df['Battery_SoC_%'] = (df['Battery_Energy_kWh'] / BATTERY_CAPACITY_KWH) * 100
        df['Unmet_Load_kWh'] = unmet_load
        df['Dumped_Energy_kWh'] = dumped_energy

        # 5. SAVE THE CRITICAL DATA TO CSV
        os.makedirs(analysis_dir, exist_ok=True) # Create folder if it doesn't exist
        print(f"\nSaving simulation data to: {output_path}")
        print("Saved Critical Metrics: Battery_SoC_%, Total_Generated_Power_kW, Unmet_Load_kWh")
        df.to_csv(output_path)

    # ==========================================
    # VISUALIZATION (Executes whether data is fresh or cached)
    # ==========================================
    print("\nGenerating visualization for a sample summer week...")
    plot_start = '2023-07-01'
    plot_end = '2023-07-07'
    df_week = df.loc[plot_start:plot_end]

    plt.style.use('seaborn-whitegrid')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 9), sharex=True)
    
    # Bottom Graph 1: Power Balance (with area fill and step plot)
    ax1.fill_between(df_week.index.to_numpy(), 0, df_week['Solar_Power_kW'].to_numpy(), 
                     color='#ff9999', alpha=0.6, label='Solar Power')
    ax1.fill_between(df_week.index.to_numpy(), 0, df_week['Wind_Power_kW'].to_numpy(), 
                     color='#66b3ff', alpha=0.6, label='Wind Power')
    
    # Load data is plotted as a 'step' plot because it represents a motor turning on and off
    ax1.step(df_week.index.to_numpy(), df_week['Load_kW'].to_numpy(), 
             color='#2c3e50', linewidth=2, linestyle='--', where='post', label='Pump Load Demand')
    
    ax1.set_title('Microgrid Power Balance & Load Profile', fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('Power (kW)', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', frameon=True, shadow=True)
    ax1.set_ylim(bottom=0) 

    # Bottom Graph 2: Battery State of Charge (SoC)
    ax2.plot(df_week.index.to_numpy(), df_week['Battery_SoC_%'].to_numpy(), 
             color='#27ae60', linewidth=2.5, label='Battery SoC')
    
    # Red area fill for the danger zone (Critical Discharge)
    ax2.fill_between(df_week.index.to_numpy(), 0, 20.0, # Used hardcoded 20.0 to avoid MIN_SOC missing on cached run
                     color='#e74c3c', alpha=0.2, label='Critical Discharge Zone (<20%)')
    ax2.axhline(20.0, color='#c0392b', linestyle=':', linewidth=2)
    
    ax2.set_ylabel('State of Charge (%)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Date / Time', fontsize=12, fontweight='bold')
    ax2.legend(loc='lower right', frameon=True, shadow=True)
    ax2.set_ylim(0, 105)

    # Beautify the X-Axis Date Format
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%H:%M'))
    ax2.xaxis.set_major_locator(mdates.DayLocator())
    plt.xticks(rotation=0, fontsize=10)

    # Soften the plot frames
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='both', which='major', labelsize=11)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_microgrid_simulation()