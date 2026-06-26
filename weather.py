import os
os.environ['MPLBACKEND'] = 'Agg'
import pandas as pd
import requests
from datetime import date
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
LATITUDE = 36.0511
LONGITUDE = -112.1214
LOCATION_NAME = "Grand Canyon"
CAMP_MONTH = 7
CAMP_START_DAY = 1
CAMP_END_DAY = 25
FORECAST_TIME = 7
DATA_TYPE = "temperature_2m_max,temperature_2m_min"
today = date.today()
current_year = today.year
all_data = []
def get_historical_weather(lat, lon, start_date, end_date, data_type):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": data_type,
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    return response.json()
def get_forecast(lat, lon, data_type, forecast_days):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": data_type,
        "timezone": "auto",
        "forecast_days": forecast_days
    }
    response = requests.get(url, params=params)
    return response.json()
def get_current_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    return response.json()
def generate_dashboard():
    df = pd.read_csv("daily_log.csv", skipinitialspace=True)
    df["datetime"] = pd.to_datetime(df["time"])
    df = df.sort_values("datetime")
    fig, ax = plt.subplots(figsize=(10, 5))  # ← just added
    ax.plot(df["datetime"], df["temp_f"], color="steelblue", linewidth=2, marker='o', markersize=5, label="Temp (°F)") 
    max_idx = df["temp_f"].idxmax()
    min_idx = df["temp_f"].idxmin()
    ax.scatter(df.loc[max_idx, "datetime"], df.loc[max_idx, "temp_f"], color="red", zorder=5, label=f"Max: {df.loc[max_idx, 'temp_f']}°F")
    ax.scatter(df.loc[min_idx, "datetime"], df.loc[min_idx, "temp_f"], color="blue", zorder=5, label=f"Min: {df.loc[min_idx, 'temp_f']}°F")
    ax.annotate(f"Max: {df.loc[max_idx, 'temp_f']}°F",
        xy=(df.loc[max_idx, "datetime"], df.loc[max_idx, "temp_f"]),
        xytext=(10, 10), textcoords="offset points",
        color="red", fontsize=9)
    ax.annotate(f"Min: {df.loc[min_idx, 'temp_f']}°F",
        xy=(df.loc[min_idx, "datetime"], df.loc[min_idx, "temp_f"]),
        xytext=(10, -15), textcoords="offset points",
        color="blue", fontsize=9)
    ax.set_ylim(df["temp_f"].min() - 5, df["temp_f"].max() + 8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
    plt.xticks(rotation=45)
    ax.set_title("My City Temperature Dashboard")
    ax.set_ylabel("Temperature (°F)")
    ax.legend()
    plt.tight_layout()
    plt.savefig("dashboard.png", dpi=150)
    plt.close()
current_data = get_current_weather(LATITUDE, LONGITUDE)
current_temp = current_data["current"]["temperature_2m"]
current_time = current_data["current"]["time"]
all_data = []
for year in range(current_year - 5, current_year):
    start = date(year, CAMP_MONTH, CAMP_START_DAY)
    end = date(year, CAMP_MONTH, CAMP_END_DAY)
    data = get_historical_weather(LATITUDE, LONGITUDE, start, end, DATA_TYPE)
    all_data.append(data)
    print(f"Fetched data for {year}")
dfs = []
for year_data in all_data:
    df = pd.DataFrame({
        "date": year_data["daily"]["time"],
        "max_temp": year_data["daily"]["temperature_2m_max"],
        "min_temp": year_data["daily"]["temperature_2m_min"]
    })
    dfs.append(df)
historical_df = pd.concat(dfs, ignore_index=True)
datar = get_forecast(LATITUDE, LONGITUDE, DATA_TYPE, FORECAST_TIME)
forecast_df = pd.DataFrame({
    "date": datar["daily"]["time"],
    "max_temp": datar["daily"]["temperature_2m_max"],
    "min_temp": datar["daily"]["temperature_2m_min"]
})
temp_c = current_temp
temp_f = round(temp_c * 9/5 + 32, 1)
log_df = pd.DataFrame({
    "date": [str(today)],
    "time": [current_time],
    "temperature_2m": [temp_c],
    "temp_f": [temp_f]
})
log_file = "daily_log.csv"
historical_df = pd.concat(dfs, ignore_index=True)
forecast_df.to_csv("forecast_weather.csv")
historical_df.to_csv("historical_weather.csv")
log_df.to_csv(log_file, mode='a', header=not os.path.isfile(log_file), index=False)
generate_dashboard()
print(f"Weather analysis for {LOCATION_NAME}")
print("=" * 40)
print("\n--- Historical Averages (last 5 years, your camping dates) ---")
print(historical_df)
print(f"\nAverage High: {historical_df['max_temp'].mean():.1f}°C")
print(f"Average Low: {historical_df['min_temp'].mean():.1f}°C")
print("\n--- 7-Day Forecast ---")
print(forecast_df)
