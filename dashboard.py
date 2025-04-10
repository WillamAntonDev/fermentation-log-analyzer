# 📦 Imports
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import os
import gspread
from google.oauth2.service_account import Credentials

# 📡 Load data from Google Sheets
def load_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_path = st.secrets["gspread_creds_path"]
    sheet_key = st.secrets["sheet_key"]
    creds = Credentials.from_service_account_file(creds_path, scopes=scope)
    client = gspread.authorize(creds)
    st.success("✅ Google Sheets API authorized.")

    try:
        st.write("🔑 Opening spreadsheet...")
        sheet = client.open_by_key(sheet_key)
        st.write("✅ Spreadsheet opened.")
        sheet1 = sheet.worksheet("Sheet1")
        st.write("📄 Worksheet found:", sheet1.title)
        data = sheet1.get_all_records()
        st.write("🧪 First 3 rows:", data[:3])
        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ Failed to open spreadsheet: {e}")
        raise

# 🎯 Page Title
st.title("🍇 Fermentation Log Analyzer")

# 🧪 Load fermentation data
try:
    df = load_sheet()
    st.write("✅ DataFrame loaded:", df.head())
except Exception as e:
    st.error(f"❌ Failed to load sheet: {e}")
    st.stop()

# 📥 Sample File Download
sample_file_path = "data/sample_fermentation_log.csv"
if os.path.exists(sample_file_path):
    with open(sample_file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="sample_fermentation_log.csv">📥 Download Sample Fermentation Log</a>'
        st.markdown(href, unsafe_allow_html=True)

# 🧹 Normalize and clean
df.columns = df.columns.str.strip().str.lower()
required_columns = {'date', 'time', 'lot', 'temp', 'brix', 'ph'}
if not required_columns.issubset(df.columns):
    st.error("❌ Sheet is missing one or more required columns: Date, Time, Lot, Temp, Brix, pH")
    st.stop()

df['date'] = pd.to_datetime(df['date'], errors='coerce')
for col in ['temp', 'brix', 'ph']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df.dropna(inplace=True)

df['datetime'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['time'])
df.sort_values(by=['lot', 'datetime'], inplace=True)

# 🚨 Brix drop detection
BRIX_DROP_THRESHOLD = 8.0
df['brix_drop'] = df.groupby('lot')['brix'].diff()
df['brix_drop_flag'] = df['brix_drop'] < -BRIX_DROP_THRESHOLD

st.subheader("📉 Rapid Brix Drop Check")
flagged = df[df['brix_drop_flag']]
if not flagged.empty:
    st.warning("⚠️ Warning: Sudden Brix drops greater than 8.0 detected!")
    st.dataframe(flagged[['datetime', 'lot', 'brix', 'brix_drop']])
else:
    st.success("✅ No Brix drops over 8.0 detected.")

# 🍷 Lot selector
lot_options = ["All Lots"] + sorted(df['lot'].unique())
selected_lot = st.selectbox("Select a wine lot to analyze", lot_options)

# 📊 Lot details
if selected_lot == "All Lots":
    lot_df = df.copy()
    st.subheader("📦 Overview: All Lots Combined")
else:
    lot_df = df[df['lot'] == selected_lot]
    st.subheader(f"📌 Lot Details: {selected_lot}")
    st.table({
        "Lot": [selected_lot],
        "Start Date": [lot_df['date'].min().strftime('%Y-%m-%d')],
        "End Date": [lot_df['date'].max().strftime('%Y-%m-%d')],
        "Duration (days)": [(lot_df['date'].max() - lot_df['date'].min()).days]
    })

# 📊 Summary
if selected_lot == "All Lots":
    st.subheader("📊 Summary by Lot (Averages)")
    st.dataframe(df.groupby('lot')[['temp', 'brix', 'ph']].mean().round(2))
else:
    st.subheader(f"📊 Summary Stats for {selected_lot}")
    summary = lot_df.describe()[['temp', 'brix', 'ph']]
    st.dataframe(summary)
    st.download_button(
        "📥 Download Summary CSV",
        summary.to_csv().encode('utf-8'),
        f"{selected_lot}_summary.csv",
        "text/csv"
    )

st.divider()

# 🧪 Flat Brix check
if selected_lot != "All Lots":
    st.subheader("🛑 Flat Brix (Stuck Fermentation)")
    flat_brix = lot_df['brix'].diff().abs().rolling(3).sum() == 0
    if lot_df[flat_brix].empty:
        st.success("✅ No stuck fermentation detected.")
    else:
        st.warning("⚠️ Potential stuck fermentation detected!")
        st.dataframe(lot_df[flat_brix])
    st.divider()

# 📈 Plots
st.subheader("📈 Variable Trends")
for col in ['temp', 'brix', 'ph']:
    st.write(f"**{col.capitalize()} Over Time**")
    fig, ax = plt.subplots()
    sns.lineplot(data=lot_df, x='date', y=col, hue='lot' if selected_lot == "All Lots" else None, marker='o', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)
