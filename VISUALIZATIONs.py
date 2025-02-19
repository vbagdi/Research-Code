import pandas as pd
import matplotlib.pyplot as plt
import os

base_path = "/Users/vinayakbagdi/Downloads/"
file_path = os.path.join(base_path, "heat_wave_classification_all_years.csv")

df = pd.read_csv(file_path)

df["time"] = pd.to_datetime(df["time"])

plt.figure(figsize=(12, 6))
plt.plot(df["time"], df["T"], label="Temperature (F)", color='r')
plt.xlabel("Year")
plt.ylabel("Temperature (F)")
plt.title("Temperature Trend Over Time")
plt.xticks(rotation=45)
plt.legend()
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(df["time"], df["HI"], label="Heat Index (HI)", color='orange')
plt.xlabel("Year")
plt.ylabel("Heat Index")
plt.title("Heat Index Trend Over Time")
plt.xticks(rotation=45)
plt.legend()
plt.show()

plt.figure(figsize=(10, 5))
plt.hist(df["HI"], bins=30, color='orange', edgecolor='black', alpha=0.7)
plt.xlabel("Heat Index")
plt.ylabel("Frequency")
plt.title("Distribution of Heat Index")
plt.show()

hot_day_counts = df["Hot_Day"].value_counts()
plt.figure(figsize=(10, 5))
plt.bar(hot_day_counts.index.astype(str), hot_day_counts.values, color=['blue', 'red'])
plt.xlabel("Hot Day")
plt.ylabel("Count")
plt.title("Count of Hot Days")
plt.show()

heat_wave_counts = df["Heat_Wave_Day"].value_counts()
plt.figure(figsize=(10, 5))
plt.bar(heat_wave_counts.index.astype(str), heat_wave_counts.values, color=['blue', 'red'])
plt.xlabel("Heat Wave Day")
plt.ylabel("Count")
plt.title("Count of Heat Wave Days")
plt.show()

print("Visualizations generated successfully.")
