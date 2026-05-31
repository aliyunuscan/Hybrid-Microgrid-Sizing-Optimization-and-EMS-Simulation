import pandas as pd
import numpy as np
import os

def generate_agricultural_load():
    # 1. Define Time Range (1 Year, Hourly = 8760 hours)
    # We use 2023 to match the weather data from the previous script
    # This creates an index from Jan 1st 00:00 to Dec 31st 23:00
    date_rng = pd.date_range(start='2023-01-01 00:00:00', end='2023-12-31 23:00:00', freq='h')
    
    # Initialize DataFrame
    df = pd.DataFrame(index=date_rng)
    df.index.name = 'Datetime'

    # 2. Define Pump Parameters
    PUMP_POWER_KW = 5.0  # 5 kW nominal power draw
    
    # Initialize the load column with zeros (pump is off by default)
    df['Load_kW'] = 0.0

    # 3. Apply Usage Scenario
    # Morning irrigation: 06:00 to 08:59 (hours 6, 7, 8)
    # Evening irrigation: 18:00 to 20:59 (hours 18, 19, 20)
    active_hours = [6, 7, 8, 18, 19, 20]
    
    # Pandas makes it easy to filter by hour of the day
    # Whenever the index's hour is in our active_hours list, set the load to 5.0 kW
    df.loc[df.index.hour.isin(active_hours), 'Load_kW'] = PUMP_POWER_KW

    # 4. Save to CSV
    output_dir = "/home/ayunusc/Desktop/Microgrid_Project/data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "agricultural_load.csv")
    df.to_csv(output_path)
    
    print(f"Load profile successfully generated and saved to: {output_path}")
    
    # Print a brief summary
    print("\nDataset Summary:")
    print(df.info())
    
    # Calculate total annual energy consumption
    # Since each row represents 1 hour, Sum of kW = Total kWh
    total_kwh = df['Load_kW'].sum()
    print(f"\nTotal annual energy consumption: {total_kwh:,.0f} kWh")
    
    # Display a sample day to verify the logic worked
    print("\nSample Day Profile (July 15th):")
    print(df.loc['2023-07-15 05:00:00':'2023-07-15 10:00:00'])

if __name__ == "__main__":
    generate_agricultural_load()