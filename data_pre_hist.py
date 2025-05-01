import pandas as pd
import numpy as np
import os

base_path = "/Users/vinayakbagdi/Downloads/boston/ssp585"
tas_file = os.path.join(base_path, "converted_ssp585_tas_boston.csv")
hurs_file = os.path.join(base_path, "combined_ssp585_hurs_boston.csv")

tas_df = pd.read_csv(tas_file)
hurs_df = pd.read_csv(hurs_file)

tas_df = tas_df.rename(columns={"tas_F": "T"})  
hurs_df = hurs_df.rename(columns={"hurs": "RH"})  

merged_df = pd.merge(tas_df, hurs_df, on=["time", "Year"])
print(tas_df)
def calculate_hi(row):
    T = row["T"]
    RH = row["RH"]
    
    HI_simple = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (RH * 0.094))
    HI = (HI_simple + T) / 2
    
    if HI < 80:
        return HI
    
    HI = (-42.379 + 2.04901523 * T + 10.14333127 * RH - 0.22475541 * T * RH 
          - 0.00683783 * T * T - 0.05481717 * RH * RH + 0.00122874 * T * T * RH 
          + 0.00085282 * T * RH * RH - 0.00000199 * T * T * RH * RH)
    
    if RH < 13 and 80 <= T <= 112:
        adjustment = ((13 - RH) / 4) * np.sqrt((17 - abs(T - 95)) / 17)
        HI -= adjustment
    
    if RH > 85 and 80 <= T <= 87:
        adjustment = ((RH - 85) / 10) * ((87 - T) / 5)
        HI += adjustment
    
    return HI

merged_df["HI"] = merged_df.apply(calculate_hi, axis=1)

merged_df = merged_df.dropna(subset=["HI"])

output_files = []
all_years_df = []
for year in range(2015, 2101):
    year_df = merged_df[merged_df["Year"] == year].copy()
    if not year_df.empty:
        hi_98th = np.percentile(year_df["HI"], 98)
        year_df["Hot_Day"] = year_df["HI"] >= hi_98th

        def classify_heat_wave(days):
            heat_wave = [False] * len(days)
            for i in range(len(days) - 3):  
                if sum(days[i:i+4]) >= 3:
                    heat_wave[i:i+4] = [True] * 4
            return heat_wave

        year_df["Heat_Wave_Day"] = classify_heat_wave(year_df["Hot_Day"].tolist())

        output_file = os.path.join(base_path, f"heat_wave_classification_{year}.csv")
        year_df.to_csv(output_file, index=False)
        output_files.append(output_file)
        all_years_df.append(year_df)
        print(f"Classification complete for {year}. Results saved to {output_file}")

final_df = pd.concat(all_years_df, ignore_index=True)
final_output_file = os.path.join(base_path, "heat_wave_classification_all_years_ssp585_boston.csv")
final_df.to_csv(final_output_file, index=False)

print(f"All years merged. Final dataset saved to {final_output_file}")
print("Processing complete for all years.")