import requests
import pandas as pd
import os
import json

def fetch_and_process_weather_data():
    # 1. API and Location Settings 39.74325489203136, 30.58907378694612
    LAT = 39.7433
    LON = 30.5891
    START_DATE = "20230101" # Start of 1-year data
    END_DATE = "20231231"   # End of 1-year data
    
    # Required parameters
    PARAMETERS = "ALLSKY_SFC_SW_DWN,WS10M,T2M"
    
    # NASA POWER API URL (Hourly, Point Data)
    URL = (
        f"https://power.larc.nasa.gov/api/temporal/hourly/point?"
        f"parameters={PARAMETERS}&community=RE&longitude={LON}&latitude={LAT}"
        f"&start={START_DATE}&end={END_DATE}&format=JSON"
    )

    print(f"Sending request to NASA POWER API... (Coordinates: {LAT}, {LON})")
    
    # 2. HTTP GET Request
    response = requests.get(URL)
    
    if response.status_code != 200:
        print(f"Error! Failed to fetch data. HTTP Status Code: {response.status_code}")
        return

    data = response.json()
    
    # 3. Converting JSON Response to Pandas DataFrame
    # The API stores data under properties -> parameter
    raw_parameters = data['properties']['parameter']
    
    # Convert dictionary structure to DataFrame
    df = pd.DataFrame(raw_parameters)
    
    # Convert index from YYYYMMDDHH string format to standard Datetime format
    df.index = pd.to_datetime(df.index, format='%Y%m%d%H')
    df.index.name = 'Datetime'
    
    print("Data successfully fetched. Proceeding to data cleaning...")

    # 4. Data Cleaning (Handling Missing Data)
    # NASA uses -999.0 for invalid/missing data. We convert these to NaN.
    df = df.replace(-999.0, pd.NA)
    
    # Fill missing data using linear interpolation (ideal for time series)
    # limit_direction='both' secures potential gaps at the beginning and end
    df = df.astype(float).interpolate(method='linear', limit_direction='both')
    
    # Make column names more readable (Optional but recommended)
    df = df.rename(columns={
        'ALLSKY_SFC_SW_DWN': 'Solar_Radiation_W_m2',
        'WS10M': 'Wind_Speed_10m_m_s',
        'T2M': 'Temperature_2m_C'
    })

    # 5. Saving the Cleaned Data as CSV
    # Create data/ directory if it doesn't exist
    output_dir = "/home/ayunusc/Desktop/Microgrid_Project/data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "weather_profile.csv")
    df.to_csv(output_path)
    
    print(f"Process completed! 1-year cleaned hourly data successfully saved to: {output_path}")
    
    # Print a brief summary of the dataset
    print("\nDataset Summary:")
    print(df.info())
    print("\nFirst 5 Rows:")
    print(df.head())

if __name__ == "__main__":
    fetch_and_process_weather_data()