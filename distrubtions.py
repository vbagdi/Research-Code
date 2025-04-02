import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson
import os

# Set your base path
base_path = "/Users/vinayakbagdi/Downloads/"
historical_path = os.path.join(base_path, "heat_wave_classification_all_years.csv")
future_path = os.path.join(base_path, "heat_wave_classification_all_years_ssp126.csv")

# Load the datasets
historical_df = pd.read_csv(historical_path)
future_df = pd.read_csv(future_path)

# Tag source
historical_df["Source"] = "Historical"
future_df["Source"] = "Future"
df = pd.concat([historical_df, future_df], ignore_index=True)

# Clean and extract year
df["time"] = pd.to_datetime(df["time"], errors="coerce")
df = df.dropna(subset=["time"])
df["Year"] = df["time"].dt.year

# Compute metrics per year
metrics = []

def extract_metrics(year_df):
    year = year_df["Year"].iloc[0]
    src = year_df["Source"].iloc[0]
    hw_days = year_df[year_df["Heat_Wave_Day"] == True]
    if hw_days.empty:
        return [year, src, 0, 0, 0]
    hw_days = hw_days.sort_values("time")
    hw_days["gap"] = (hw_days["time"] - hw_days["time"].shift()).dt.days > 1
    hw_days["wave_id"] = hw_days["gap"].cumsum()
    wave_groups = hw_days.groupby("wave_id")
    durations = wave_groups["time"].nunique()
    intensities = wave_groups["HI"].mean()
    count = len(durations)
    avg_duration = durations.mean()
    avg_intensity = intensities.mean()
    return [year, src, count, avg_duration, avg_intensity]

for (year, source), group in df.groupby(["Year", "Source"]):
    metrics.append(extract_metrics(group))

metrics_df = pd.DataFrame(metrics, columns=["Year", "Source", "Count", "Duration", "Intensity"])

# Bin into 10-year periods
metrics_df["Period"] = pd.cut(
    metrics_df["Year"],
    bins=list(range(1950, 2110, 10)),
    right=False,
    labels=[f"{y}-{y+9}" for y in range(1950, 2100, 10)]
)

# Summarize
summary = metrics_df.groupby(["Period", "Source"]).agg({
    "Count": ["mean", "sum", "count"],
    "Duration": "mean",
    "Intensity": ["mean", "std"]
}).reset_index()

summary.columns = ["Period", "Source", "Mean_Count", "Total_Heatwaves", "Years",
                   "Mean_Duration", "Mean_Intensity", "Std_Intensity"]

summary["Poisson_Lambda"] = summary["Total_Heatwaves"] / summary["Years"]

# Split summaries
historical_summary = summary[summary["Source"] == "Historical"]
future_summary = summary[summary["Source"] == "Future"]

# Plotting helper
def plot_metric(data, y, title, ylabel, color='blue', yerr=None):
    plt.figure(figsize=(12, 6))
    if yerr:
        plt.errorbar(data["Period"], data[y], yerr=data[yerr], fmt='o-', capsize=4, color=color)
    else:
        plt.plot(data["Period"], data[y], marker='o', linestyle='-', color=color)
    plt.title(title)
    plt.xlabel("10-Year Period")
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

# 🔹 Metric Visualizations

plot_metric(historical_summary, "Poisson_Lambda", "Poisson Mean (λ) - Historical", "Poisson Mean (λ)")
plot_metric(future_summary, "Poisson_Lambda", "Poisson Mean (λ) - Future", "Poisson Mean (λ)", color='orange')

plot_metric(historical_summary, "Mean_Duration", "Heatwave Duration - Historical", "Days")
plot_metric(future_summary, "Mean_Duration", "Heatwave Duration - Future", "Days", color='orange')

plot_metric(historical_summary, "Mean_Intensity", "Heatwave Intensity (±1 Std Dev) - Historical", "Heat Index", yerr="Std_Intensity")
plot_metric(future_summary, "Mean_Intensity", "Heatwave Intensity (±1 Std Dev) - Future", "Heat Index", color='orange', yerr="Std_Intensity")

# 🔸 Poisson Distributions for First 3 Valid Future Periods
x = np.arange(0, 20)

valid_rows = future_summary[future_summary["Years"] > 0].head(3)

for _, row in valid_rows.iterrows():
    lam = row["Poisson_Lambda"]
    if not np.isnan(lam):
        pmf = poisson.pmf(x, lam)

        plt.figure(figsize=(8, 4))
        plt.bar(x, pmf, color='orange', alpha=0.7)
        plt.title(f"Poisson Distribution for Heatwave Count\n{row['Period']} (λ = {lam:.2f})")
        plt.xlabel("Number of Heatwaves")
        plt.ylabel("Probability")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.show()

