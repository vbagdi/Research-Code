import pandas as pd
import numpy as np
import os

# File paths
base_path = "/Users/vinayakbagdi/Downloads/"
tas_file = os.path.join(base_path, "converted_tas.csv")
hurs_file = os.path.join(base_path, "combined_hurs.csv")

# Load the data
tas_df = pd.read_csv(tas_file)
hurs_df = pd.read_csv(hurs_file)

# Ensure both dataframes have the same date column and correct variables
tas_df = tas_df.rename(columns={"tas_F": "T"})  # Using tas_F for temperature
hurs_df = hurs_df.rename(columns={"hurs": "RH"})  # Using hurs for relative humidity

# Merge data on time
merged_df = pd.merge(tas_df, hurs_df, on=["time", "Year"])

# Compute Heat Index (HI) only when T > 80
def calculate_hi(row):
    T = row["T"]
    RH = row["RH"]
    
    if T <= 80:
        return np.nan  # Ignore HI calculation for temperatures <= 80
    
    HI = (-42.379 + 2.04901523 * T + 10.14333127 * RH - 0.22475541 * T * RH 
          - 0.00683783 * T * T - 0.05481717 * RH * RH + 0.00122874 * T * T * RH 
          + 0.00085282 * T * RH * RH - 0.00000199 * T * T * RH * RH)
    
    # Adjustment for low RH and high temperature
    if RH < 13 and 80 <= T <= 112:
        adjustment = ((13 - RH) / 4) * np.sqrt((17 - abs(T - 95)) / 17)
        HI -= adjustment
    
    # Adjustment for high RH and moderate temperature
    if RH > 85 and 80 <= T <= 87:
        adjustment = ((RH - 85) / 10) * ((87 - T) / 5)
        HI += adjustment
    
    return HI

merged_df["HI"] = merged_df.apply(calculate_hi, axis=1)

# Drop rows where HI is NaN (temperatures <= 80)
merged_df = merged_df.dropna(subset=["HI"])

# Process each year separately
output_files = []
all_years_df = []
for year in range(1950, 2015):
    year_df = merged_df[merged_df["Year"] == year].copy()
    if not year_df.empty:
        hi_98th = np.percentile(year_df["HI"], 98)
        year_df["Hot_Day"] = year_df["HI"] >= hi_98th

        # Identify Heat Wave Days
        def classify_heat_wave(days):
            heat_wave = [False] * len(days)
            for i in range(len(days) - 3):  # Check 4-day periods
                if sum(days[i:i+4]) >= 3:
                    heat_wave[i:i+4] = [True] * 4
            return heat_wave

        year_df["Heat_Wave_Day"] = classify_heat_wave(year_df["Hot_Day"].tolist())

        # Save results
        output_file = os.path.join(base_path, f"heat_wave_classification_{year}.csv")
        year_df.to_csv(output_file, index=False)
        output_files.append(output_file)
        all_years_df.append(year_df)
        print(f"Classification complete for {year}. Results saved to {output_file}")

# Merge all yearly files into one
final_df = pd.concat(all_years_df, ignore_index=True)
final_output_file = os.path.join(base_path, "heat_wave_classification_all_years.csv")
final_df.to_csv(final_output_file, index=False)

print(f"All years merged. Final dataset saved to {final_output_file}")
print("Processing complete for all years.")
