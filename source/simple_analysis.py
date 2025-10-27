import pandas as pd
from pathlib import Path

# ------------------------
# I. DATA LOADING
# ------------------------

def main() -> None:
    """
    This script loads weather data from a 'dataset.csv' file, cleans and 
    prepares the 'HRM %', 'TM °C', and 'Data' columns, and then performs 
    a basic analysis. The analysis includes:
    1. Counting the total number of unique weather stations.
    2. Counting the number of 'Comarques' (regions) with stations.
    3. Calculating the number of unique stations per 'Comarca'.
    4. Identifying the top 5 warmest days (based on mean temperature) and 
       the corresponding station and region.
    5. Identifying the top 5 most humid days (based on mean humidity) and
       the corresponding station and region.
    Finally, it prints all the calculated results.
    """
    try:
        # Load the data from the CSV file
        df = pd.read_csv('../dataset/dataset.csv', sep=';', decimal='.')      
        print("Data loaded successfully.")
    except FileNotFoundError:
        print("Error: The file 'dataset.csv' was not found.")

    # ------------------------
    # II. SELECTION AND CLEANING
    # ------------------------
    # Column names in the dataframe
    COL_COMARCA = 'Comarca'
    COL_ESTACIO = 'Estació [Codi]'
    COL_HRM = 'HRM %'
    COL_TEMPERATURA = 'TM °C'  # Mean Temperature
    COL_DATA = 'Data'

    # DATA CLEANING
    # Convert 'HRM %' and 'TM °C' columns to 'float'
    # Convert 'Data' column to 'datetime'
    # Any invalid value will be converted to NaN.
    df[COL_HRM] = pd.to_numeric(
        df[COL_HRM],
        errors='coerce', # Use errors='coerce' to turn non-numeric values into NaN
        downcast='float'
    )
    df[COL_TEMPERATURA] = pd.to_numeric(
        df[COL_TEMPERATURA],
        errors='coerce', # Use errors='coerce' to turn non-numeric values into NaN
        downcast='float'
    )
    df[COL_DATA] = pd.to_datetime(
        df[COL_DATA],
        format='%d.%m.%Y',
        errors='coerce' # Use errors='coerce' to handle invalid date formats
    )

    # ------------------------
    # III. ANALYSIS
    # ------------------------
    # 1. Total number of stations
    numero_estaciones_unicas = df[COL_ESTACIO].nunique()

    # 2. 'Comarques' (regions) with stations
    comarques_amb_estacions = df[COL_COMARCA].nunique()

    # 3. Number of stations per 'Comarca'
    #    Count how many unique stations we have for each region using .nunique()
    estacions_per_comarca = df.groupby(COL_COMARCA)[COL_ESTACIO].nunique().sort_values(ascending=False)

    # 4. Warmest station and day
    # 4.1. Group by day and station and calculate the mean daily temperature
    temp_mitjana_diaria = df.groupby([COL_DATA, COL_ESTACIO, COL_COMARCA])[COL_TEMPERATURA].mean().rename('TEMP_mean_daily')
    top_temp = temp_mitjana_diaria.sort_values(ascending=False).head()

    # 5. Most humid stations
    hrm_mitjana_diaria = df.groupby([COL_DATA, COL_ESTACIO, COL_COMARCA])[COL_HRM].mean().rename('HRM_mean_daily')
    top_hrm = hrm_mitjana_diaria.sort_values(ascending=False).head()

    # ------------------------
    # IV. RESULTS
    # ------------------------
    print("\nCOUNT OF STATIONS ACROSS CATALONIA")
    print(numero_estaciones_unicas)

    print("\nCOUNT OF REGIONS ('COMARQUES') WITH A STATION")
    print(comarques_amb_estacions)

    print("\nCOUNT OF STATIONS PER REGION ('COMARCA')")
    print(estacions_per_comarca)

    print("\nWARMEST DAYS BY STATION")
    print(top_temp)

    print("\nMOST HUMID DAYS BY STATION")
    print(top_hrm)

if __name__ == "__main__":
    main()