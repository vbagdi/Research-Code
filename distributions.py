import pandas as pd
import os
from scipy.stats import theilslopes
import matplotlib.pyplot as plt
import numpy as np

# ========== CONFIG ==========
files = {
    "historical": "/Users/vinayakbagdi/Downloads/Research_Code/Full Research Data/research data/heat_wave_classification_all_years_historical.csv",
    "ssp126": "/Users/vinayakbagdi/Downloads/Research_Code/Full Research Data/research data/heat_wave_classification_all_years_ssp126.csv",
    "ssp245": "/Users/vinayakbagdi/Downloads/Research_Code/Full Research Data/research data/heat_wave_classification_all_years_ssp245.csv",
    "ssp585": "/Users/vinayakbagdi/Downloads/Research_Code/Full Research Data/research data/heat_wave_classification_all_years_ssp585.csv"
}

metrics = ['avg_duration', 'avg_intensity', 'avg_yearly_frequency', 'avg_yearly_season_length']
output_dir = "/Users/vinayakbagdi/Downloads/"
os.makedirs(output_dir, exist_ok=True)

# ========== HELPER FUNCTIONS ==========
def find_heatwaves(df):
    heatwaves = []
    current_hw = []
    for _, row in df.iterrows():
        if row['Heat_Wave_Day'] == 1:
            current_hw.append(row)
        else:
            if current_hw:
                heatwaves.append(pd.DataFrame(current_hw))
                current_hw = []
    if current_hw:
        heatwaves.append(pd.DataFrame(current_hw))
    return heatwaves

def process_scenario(df, label):
    df['Year'] = df['Year'].astype(int)
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df = df.dropna(subset=['time'])

    df['decade'] = (df['Year'] // 10) * 10
    df.loc[df['Year'] == 2100, 'decade'] = 2090

    results = []
    for decade, group in df.groupby('decade'):
        heatwaves = find_heatwaves(group)
        durations = [len(hw) for hw in heatwaves] if heatwaves else [0]
        intensities = [hw['HI'].mean() for hw in heatwaves if 'HI' in hw.columns] if heatwaves else [0]

        yearly_frequencies = []
        yearly_season_lengths = []
        for year, year_group in group.groupby('Year'):
            year_heatwaves = find_heatwaves(year_group)
            frequency = len(year_heatwaves) if year_heatwaves else 0

            hot_days = year_group[year_group['Hot_Day'] == 1]['time']
            season_length = (hot_days.max() - hot_days.min()).days if not hot_days.empty else 0

            yearly_frequencies.append(frequency)
            yearly_season_lengths.append(season_length)

        results.append({
            'scenario': label,
            'decade': decade,
            'avg_duration': sum(durations) / len(durations),
            'avg_intensity': sum(intensities) / len(intensities),
            'avg_yearly_frequency': sum(yearly_frequencies) / len(yearly_frequencies),
            'avg_yearly_season_length': sum(yearly_season_lengths) / len(yearly_season_lengths)
        })

    return pd.DataFrame(results)

# ========== PROCESS ALL SCENARIOS ==========
all_results = []
for label, path in files.items():
    df = pd.read_csv(path)
    result = process_scenario(df, label)
    all_results.append(result)

final_df = pd.concat(all_results, ignore_index=True)

# ========== SEN'S SLOPE + VARIABILITY ==========
sen_slopes = {}
variability = {}
for label, group in final_df.groupby('scenario'):
    for metric in metrics:
        slope, intercept, _, _ = theilslopes(group[metric], group['decade'])
        sen_slopes[f'{label}_{metric}_slope'] = slope
        variability[f'{label}_{metric}_std'] = group[metric].std()

# Save summary tables
pd.DataFrame([sen_slopes]).to_csv(os.path.join(output_dir, "sens_slope_summary.csv"), index=False)
pd.DataFrame([variability]).to_csv(os.path.join(output_dir, "std_dev_summary.csv"), index=False)

# ========== PLOTTING: METRIC TRENDS ==========
for metric in metrics:
    plt.figure(figsize=(10, 6))
    for scenario in files:
        subset = final_df[final_df['scenario'] == scenario]
        plt.plot(subset['decade'], subset[metric], marker='o', label=scenario.upper())
    plt.xlabel("Decade")
    plt.ylabel(metric.replace('_', ' ').title())
    plt.title(f"Trend Comparison: {metric.replace('_', ' ').title()}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}trend_{metric}.png")
    plt.close()  # This ensures plots don’t overlap


# ========== PLOTTING: HEATMAPS W/ MATPLOTLIB ==========
def plot_heatmap(data_dict, title, filename, fmt=".3f", cmap="coolwarm"):
    df = pd.DataFrame(data_dict, index=[0]).T.reset_index()
    df.columns = ['metric_scenario', 'value']
    df[['scenario', 'metric']] = df['metric_scenario'].str.extract(r'^(.*?)_(avg_.*?)_(?:slope|std)')
    pivot = df.pivot(index='metric', columns='scenario', values='value')

    fig, ax = plt.subplots(figsize=(10, 6))
    cax = ax.imshow(pivot.values, cmap=cmap, aspect='auto')
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticklabels([label.replace('_', ' ').title() for label in pivot.index])
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            ax.text(j, i, format(value, fmt), ha="center", va="center", color="black")

    ax.set_title(title)
    fig.colorbar(cax)
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, filename))
    plt.show()

# Plot both heatmaps
plot_heatmap(sen_slopes, "Sen's Slope (Trend Strength)", "sens_slope_heatmap.png", fmt=".3f", cmap="coolwarm")
plot_heatmap(variability, "Standard Deviation (Inter-Decadal Variability)", "std_dev_heatmap.png", fmt=".2f", cmap="YlGnBu")

# ========== FINAL SAVE ==========
final_df.to_csv(os.path.join(output_dir, "heatwave_decadal_comparison.csv"), index=False)
