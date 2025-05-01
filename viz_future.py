import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Load dataset
base_path = "/Users/vinayakbagdi/Downloads/boston/historical"
file_path = os.path.join(base_path, "heat_wave_classification_all_years_historical_boston.csv")
df = pd.read_csv(file_path)

df["time"] = pd.to_datetime(df["time"], errors="coerce")
df = df.dropna(subset=["time"])
df["Month"] = df["time"].dt.month
df["Year"] = df["time"].dt.year

# Only keep future years
df = df[df["Year"] >= 1950]

# Define future decades
future_decades = [(y, y+9) for y in range(1950, 2015, 10)]

metrics = []

# Metric extraction function
def extract_metrics(year_df):
    year = year_df["Year"].iloc[0]
    hw_days = year_df[year_df["Heat_Wave_Day"] == True]

    if hw_days.empty:
        return [year, 0, 0, 0, 0]

    hw_days = hw_days.sort_values("time")
    hw_days["gap"] = (hw_days["time"] - hw_days["time"].shift()).dt.days > 1
    hw_days["wave_id"] = hw_days["gap"].cumsum()

    wave_groups = hw_days.groupby("wave_id")
    durations = wave_groups["time"].nunique()
    intensities = wave_groups["HI"].mean()

    count = len(durations)
    avg_duration = durations.mean()
    avg_intensity = intensities.mean()
    season_length = (hw_days["time"].max() - hw_days["time"].min()).days

    return [year, count, avg_duration, avg_intensity, season_length]

# Apply metric extraction
for year in df["Year"].unique():
    year_df = df[df["Year"] == year]
    metrics.append(extract_metrics(year_df))

metrics_df = pd.DataFrame(metrics, columns=["Year", "Count", "Duration", "Intensity", "Season_Length"])

# Assign decade buckets
def assign_period(year):
    for start, end in future_decades:
        if start <= year <= end:
            return f"{start}-{end}"
    return "Other"

metrics_df["Period"] = metrics_df["Year"].apply(assign_period)
metrics_df = metrics_df[metrics_df["Period"] != "Other"]

# Generate box plots for each metric
metrics_to_plot = ["Count", "Duration", "Intensity", "Season_Length"]

for metric in metrics_to_plot:
    plt.figure(figsize=(10, 6))
    metrics_df.boxplot(column=metric, by="Period", grid=False)
    plt.title(f"{metric} by Decade (ssp126)")
    plt.suptitle("")
    plt.xlabel("Decade")
    plt.ylabel(metric)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()
