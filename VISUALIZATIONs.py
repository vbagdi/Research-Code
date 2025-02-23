import pandas as pd
import matplotlib.pyplot as plt
import os

base_path = "/Users/vinayakbagdi/Downloads/"
file_path = os.path.join(base_path, "heat_wave_classification_all_years.csv")

df = pd.read_csv(file_path)

df["time"] = pd.to_datetime(df["time"], errors="coerce")
df = df.dropna(subset=["time"])  # Remove invalid dates

df["Month"] = df["time"].dt.month
df["Year"] = df["time"].dt.year

plt.figure(figsize=(12, 6))
years = sorted(df["Year"].unique())
first_year = years[0]

year_labels = []
label_positions = []  

for year in years:
    yearly_data = df[df["Year"] == year]
    monthly_avg_hi = yearly_data.groupby("Month")["HI"].mean()
    plt.plot(monthly_avg_hi.index, monthly_avg_hi.values, label=str(year), alpha=0.7)
    
    if (year - first_year) % 10 == 0:
        y_pos = monthly_avg_hi.values[-1]
        
        while any(abs(y_pos - existing) < 1.5 for existing in label_positions):
            y_pos += 1.5  
        
        plt.text(12.1, y_pos, str(year), verticalalignment='center')
        label_positions.append(y_pos)
        year_labels.append(year)

plt.xlabel("Month")
plt.ylabel("Average Heat Index (HI)")
plt.title("Yearly Heat Index Trends Over 12-Month Period")
plt.xticks(range(1, 13), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
plt.legend(loc='upper left', fontsize=8, ncol=2, title="Year", bbox_to_anchor=(1,1))
plt.grid(True, linestyle='--', alpha=0.5)
plt.show()

print("Yearly HI trends visualization generated successfully.")
