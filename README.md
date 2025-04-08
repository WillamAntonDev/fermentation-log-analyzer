# 🍇 Fermentation Log Analyzer

Track, analyze, and visualize your wine fermentation data with this simple, interactive Streamlit app. Built by a winemaker turned developer, this tool helps you catch stuck fermentations, spot high temps, and make smarter decisions based on real-time metrics.

## 🔍 Features

- Upload your CSV log and get instant analysis
- Detect potential stuck fermentations (flat Brix)
- Flag dangerously high fermentation temperatures (>35°C)
- View summary statistics for Temp, Brix, and pH
- Download analysis reports
- Interactive line charts for each variable

## 📊 Sample Log Format

Your CSV should have these exact columns:

| Date       | Temp | Brix | pH  |
|------------|------|------|-----|
| 2025-04-01 | 24.5 | 21.5 | 3.4 |
| 2025-04-02 | 25.2 | 20.8 | 3.38 |

> ✅ **Tip**: A sample CSV is included in this repo.

## 🚀 How to Use

### Run Locally

1. Clone the repo  
   `git clone https://github.com/WillamAntonDev/fermentation-log-analyzer.git
2. Install dependencies  
   `pip install -r requirements.txt`
3. Start the app  
   `streamlit run dashboard.py`

### Use Online (via Streamlit Cloud)

➡️ [Launch the app here](https://fermentation-app.streamlit.app) *(Link goes here once deployed)*

## 🧠 Built With

- Python
- pandas
- Streamlit
- matplotlib + seaborn

## 🧑‍💻 About the Creator

William Anton is a former winemaker and manufacturing specialist turned software developer, focused on building tools that solve real-world problems through code and data.

> *“I built the tool I wish I had back in the cellar.”*

