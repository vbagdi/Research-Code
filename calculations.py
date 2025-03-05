import pandas as pd
import numpy as np
import os

# File path
base_path = "/Users/vinayakbagdi/Downloads/"
file_path = os.path.join(base_path, "heat_wave_classification_all_years.csv")

# Load the data
df = pd.read_csv(file_path)

# Convert time to datetime with error handling
df["time"] = pd.to_datetime(df["time"], errors="coerce")
df = df.dropna(subset=["time"])  # Remove invalid dates

df["Year"] = df["time"].dt.year
df["Month"] = df["time"].dt.month
df["Week"] = df["time"].dt.isocalendar().week
df["Julian_Date"] = df["time"].dt.dayofyear

# Count heatwaves per year
heatwave_counts = df.groupby("Year")["Heat_Wave_Day"].sum()

# Compute average duration of heatwaves
def compute_heatwave_durations(df):
    durations = []
    current_duration = 0
    for index, row in df.iterrows():
        if row["Heat_Wave_Day"]:
            current_duration += 1
        else:
            if current_duration > 0:
                durations.append(current_duration)
            current_duration = 0
    if current_duration > 0:
        durations.append(current_duration)
    return durations

heatwave_durations = df.groupby("Year").apply(compute_heatwave_durations)
avg_duration = heatwave_durations.apply(lambda x: np.mean(x) if len(x) > 0 else 0)

# Compute heatwave intensity using degree days approach
intensity_per_year = {}

def calculate_degree_days(heatwave_df, threshold):
    return (heatwave_df["HI"] - threshold).clip(lower=0).sum()

for year in df["Year"].unique():
    year_df = df[df["Year"] == year]
    if year_df["Heat_Wave_Day"].sum() > 0:
        threshold_95th = np.percentile(year_df["HI"].dropna(), 95)  # 95th percentile HI threshold
        heatwave_days = year_df[year_df["Heat_Wave_Day"]]
        intensity_per_year[year] = calculate_degree_days(heatwave_days, threshold_95th)
    else:
        intensity_per_year[year] = 0

# The intensity of a heatwave is measured as the total excess heat index (HI) above the 95th percentile threshold.
# Degree Days Calculation:
# Each day's HI is compared to the 95th percentile HI for that year.
# The difference (excess HI) is summed over all heatwave days.
# This metric accounts for both the magnitude and duration of extreme heat.
# A higher value indicates stronger and more prolonged heatwaves

# Compute the length of the heatwave season
first_heatwave = df[df["Heat_Wave_Day"]].groupby("Year")["Julian_Date"].min()
last_heatwave = df[df["Heat_Wave_Day"]].groupby("Year")["Julian_Date"].max()
season_length = (last_heatwave - first_heatwave).fillna(0)

# Create summary DataFrame
summary_df = pd.DataFrame({
    "Heatwave_Count": heatwave_counts,
    "Avg_Duration": avg_duration,
    "Avg_Intensity": pd.Series(intensity_per_year),
    "Season_Length": season_length
})

# Save results
output_file = os.path.join(base_path, "heatwave_analysis_summary.csv")
summary_df.to_csv(output_file)

print(f"Heatwave analysis complete. Results saved to {output_file}")
