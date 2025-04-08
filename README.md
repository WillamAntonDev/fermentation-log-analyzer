# 🍇 Fermentation Log Analyzer

[![Streamlit App](https://img.shields.io/badge/Live_App-Streamlit-brightgreen?logo=streamlit)](https://fermentation-log-analyzer-eeajwtajgbzevolp7urnmo.streamlit.app/)

Track, analyze, and visualize your wine fermentation data — all in one clean, interactive dashboard.

This app was built by a winemaker-turned-software-developer to make fermentation logs *actually useful*. Upload your CSV, pick a lot, and get insights on temperature, Brix, pH trends, stuck fermentations, and more.

---

## 🔍 Features

- 📂 Upload your own CSV fermentation logs
- 🍷 Select a specific wine lot to analyze
- 📊 View clean, sortable summary stats for Temp, Brix, and pH
- 📅 See the fermentation date range for each lot
- 📉 Detect potential stuck fermentations (flat Brix over time)
- 📈 Interactive line plots for each variable
- 💾 Download a per-lot summary CSV for your records
- 💻 Deployed live on Streamlit Cloud

---

## 🚀 Try It Live

👉 **[Launch the Fermentation Log Analyzer](https://fermentation-log-analyzer-eeajwtajgbzevolp7urnmo.streamlit.app/)** 
No installation needed. Just upload your `.csv` and explore.

---

## 📋 CSV Format (Required Columns)

Your fermentation log should look like this:

| Date       | Lot                     | Temp | Brix | pH  |
|------------|--------------------------|------|------|-----|
| 2025-04-01 | 24-CS-Napa-Beckstoffer  | 24.5 | 21.2 | 3.42 |
| 2025-04-02 | 24-CS-Napa-Beckstoffer  | 25.1 | 20.5 | 3.40 |
| 2025-04-01 | 24-PN-Willamette        | 22.0 | 23.1 | 3.50 |

- `Date` must be in a recognizable date format
- `Lot` is used to filter and group fermentations
- `Temp`, `Brix`, and `pH` must be numeric

---

## 🧠 Built With

- Python
- pandas
- Streamlit
- seaborn + matplotlib
- Real-life winery headaches

---

## 👤 About the Creator

**William Anton**  
Former winemaker turned software engineer.  
Now building tools that combine domain expertise with clean code and practical design.

📍 [LinkedIn](https://www.linkedin.com/in/willantonvino/)  
💻 [GitHub](https://github.com/willamantondev)

> _“I built the tool I wish I had back in the cellar.”_

---

## 🛠 Local Dev Instructions (Optional)

```bash
git clone https://github.com/WillamAntonDev/fermentation-log-analyzer.git
cd fermentation-log-analyzer
pip install -r requirements.txt
streamlit run dashboard.py
