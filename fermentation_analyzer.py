# 1️⃣ Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys  # <-- NEW: for command-line file input

# 2️⃣ File input (existing sample file or user-supplied file)
if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    file_path = 'sample_data/sample_log.csv'  # default fallback

# 3️⃣ Load data
df = pd.read_csv(file_path)

# 4️⃣ Clean and format
if 'Date' not in df.columns:
    st.error("❌ Your file is missing a required column: 'Date'")
    st.stop()
else:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

df = df.dropna(subset=['Date'])

for col in ['Temp', 'Brix', 'pH']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df = df.dropna(subset=['Temp', 'Brix', 'pH'])

# 5️⃣ Summary stats (terminal)
print("\n📊 Summary:")
summary = df.describe()[['Temp', 'Brix', 'pH']]
print(summary)

# 6️⃣ 🆕 Export summary to CSV
os.makedirs("outputs", exist_ok=True)
summary.to_csv("outputs/summary_stats.csv")
print("📤 Summary exported to outputs/summary_stats.csv")

# 7️⃣ 🆕 Detect high temperatures
high_temp_df = df[df['Temp'] > 35]
if not high_temp_df.empty:
    print("\n🔥 High Temperatures (>35°C):")
    print(high_temp_df)
    high_temp_df.to_csv("outputs/high_temps.csv", index=False)
else:
    print("\n✅ No dangerously high temps detected.")

# 8️⃣ Flat Brix detection
flat_brix = df['Brix'].diff().abs().rolling(3).sum() == 0
print("\n📉 Flat Brix values (Stuck fermentation):")
print(df[flat_brix])

# 9️⃣ Plot and save graphs
sns.set(style="whitegrid")
for col in ['Temp', 'Brix', 'pH']:
    plt.figure(figsize=(8, 4))
    sns.lineplot(x='Date', y=col, data=df, marker='o')
    plt.title(f"{col} Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"outputs/{col.lower()}_plot.png")
    plt.close()

print("\n✅ Plots saved in the outputs folder.")