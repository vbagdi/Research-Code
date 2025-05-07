import pandas as pd
import os
from scipy.stats import theilslopes, kendalltau
import matplotlib.pyplot as plt
import numpy as np

# ========== CONFIG ==========
files = {
    "historical": "/Users/vinayakbagdi/Downloads/Research_Code/chicago/research data/heat_wave_classification_all_years_historical.csv",
    "ssp126": "/Users/vinayakbagdi/Downloads/Research_Code/chicago/research data/heat_wave_classification_all_years_ssp126.csv",
    "ssp245": "/Users/vinayakbagdi/Downloads/Research_Code/chicago/research data/heat_wave_classification_all_years_ssp245.csv",
    "ssp585": "/Users/vinayakbagdi/Downloads/Research_Code/chicago/research data/heat_wave_classification_all_years_ssp585.csv"
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

# ========== CALCULATE SEN'S SLOPE + P-VALUES ==========
results_for_csv = []
results_for_heatmap = {}
for label, group in final_df.groupby('scenario'):
    row = {'Scenario': label.upper()}
    for metric in metrics:
        slope, _, _, _ = theilslopes(group[metric], group['decade'])
        _, p_value = kendalltau(group['decade'], group[metric])
        slope_p = f"{slope:.3f} (p={p_value:.3f})"
        row[metric.replace("avg_", "").replace("_", " ").title()] = slope_p
        results_for_heatmap[f"{metric}_{label}"] = f"{slope:.3f}\n(p={p_value:.3f})"
    results_for_csv.append(row)

# Save to CSV
summary_df = pd.DataFrame(results_for_csv)
summary_df.to_csv(os.path.join(output_dir, "sens_slope_ci_summary.csv"), index=False)

# ========== PLOT HEATMAP (WITH SLOPE + P-VALUE) ==========
def plot_slope_pvalue_heatmap(results_dict, title, filename):
    records = []
    for k, v in results_dict.items():
        metric, scenario = k.split("_", 1)
        records.append({'Metric': metric, 'Scenario': scenario.upper(), 'Value': v})
    df = pd.DataFrame(records)
    df['Metric'] = df['Metric'].str.replace("avg_", "").str.replace("_", " ").str.title()
    heatmap_df = df.pivot(index='Metric', columns='Scenario', values='Value')

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(np.zeros_like(heatmap_df.values, dtype=float), cmap="Greys", vmin=0, vmax=1)

    ax.set_xticks(np.arange(len(heatmap_df.columns)))
    ax.set_yticks(np.arange(len(heatmap_df.index)))
    ax.set_xticklabels(heatmap_df.columns)
    ax.set_yticklabels(heatmap_df.index)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    for i in range(len(heatmap_df.index)):
        for j in range(len(heatmap_df.columns)):
            text = heatmap_df.iloc[i, j]
            ax.text(j, i, text, ha="center", va="center", color="black", fontsize=10)

    ax.set_title(title)
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, filename))
    plt.show()

# Create the heatmap
plot_slope_pvalue_heatmap(results_for_heatmap, "Sen's Slope Trends with p-values", "sens_slope_heatmap_pvals.png")
