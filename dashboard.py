# 📦 Imports
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
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
    
    try:
        sheet = client.open_by_key(sheet_key).worksheet("Sheet1")
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Failed to load Google Sheet: {e}")
        raise

# 🎯 Page Title
st.title("🍇 Fermentation Log Analyzer")

# 📥 Sample File Download
sample_file_path = "data/sample_fermentation_log.csv"
if os.path.exists(sample_file_path):
    with open(sample_file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="sample_fermentation_log.csv">📥 Download Sample Fermentation Log</a>'
        st.markdown(href, unsafe_allow_html=True)

# 📤 Choose Data Source
source = st.radio("📤 Choose Data Source", ["Google Sheets", "Manual CSV Upload"])
df = None

if source == "Google Sheets":
    try:
        df = load_sheet()
        st.write("🕵️‍♂️ Columns at load:", df.columns.tolist())
        st.success("✅ Google Sheet loaded successfully.")
    except Exception:
        st.stop()
else:
    uploaded_file = st.file_uploader("Upload your fermentation CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("✅ CSV file loaded.")
    else:
        st.warning("📭 Please upload a CSV file.")
        st.stop()

# 🧹 Normalize and clean
df.columns = df.columns.str.strip().str.lower()

required_columns = {
    'date', 'time', 'lot', 'temp', 'brix', 'ph',
    'va', 'ta', 'alcohol', 'so2', 'mlf', 'notes'
}
missing = required_columns - set(df.columns)
if missing:
    st.error(f"❌ Missing required columns: {', '.join(missing)}")
    st.stop()

# 🗓️ Date + Time handling
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['datetime'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['time'])

# 🔢 Convert numeric fields
numeric_cols = ['temp', 'brix', 'ph', 'va', 'ta', 'alcohol', 'so2']
for col in numeric_cols:
    df[col] = df[col].replace(r'^\s*$', pd.NA, regex=True)
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 🧪 Show nulls before dropna (debugging)
st.subheader("🧹 Nulls per numeric column (before cleaning)")
st.dataframe(df[numeric_cols].isnull().sum())
st.write(f"❗Total rows before cleaning: {len(df)}")

# 🧹 Drop rows missing ONLY critical values
required_clean_cols = ['date', 'time', 'lot', 'brix', 'temp']
df.dropna(subset=required_clean_cols, inplace=True)

# ✅ Report post-cleaning status
st.success(f"✅ Cleaned data — rows remaining: {len(df)}")
st.dataframe(df.head(5))  # Optional preview

# Sort by time
df.sort_values(by=['lot', 'datetime'], inplace=True)

# 🗓️ Date + Time handling
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['datetime'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['time'])

# 🔢 Convert numeric fields
numeric_cols = ['temp', 'brix', 'ph', 'va', 'ta', 'alcohol', 'so2']
for col in numeric_cols:
    df[col] = df[col].replace(r'^\s*$', pd.NA, regex=True)  # Replace empty strings
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 🔍 Show null counts before cleaning
null_preview = df[numeric_cols].isnull().sum()
st.subheader("🧹 Nulls per numeric column (pre-cleaning)")
st.dataframe(null_preview)

st.write(f"❗Total rows before cleaning: {len(df)}")

# ✅ Drop rows missing only critical fields
required_clean_cols = ['date', 'time', 'lot', 'temp', 'brix', 'ph']
df.dropna(subset=required_clean_cols, inplace=True)

# ✅ Report what's left
st.success(f"✅ Rows after smart clean: {len(df)}")
st.dataframe(df.head(10))

# 📦 Sort by time again just in case
df.sort_values(by=['lot', 'datetime'], inplace=True)


# 🚨 Brix drop detection
df['brix_drop'] = df.groupby('lot')['brix'].diff()
df['brix_drop_flag'] = df['brix_drop'] < -8.0

# 📉 Brix warning
st.subheader("📉 Rapid Brix Drop Check")
flagged = df[df['brix_drop_flag']]
if not flagged.empty:
    st.warning("⚠️ Sudden Brix drops > 8.0 detected!")
    st.dataframe(flagged[['datetime', 'lot', 'brix', 'brix_drop']])
else:
    st.success("✅ No large Brix drops detected.")

# 🍷 Lot selector
lot_options = ["All Lots"] + sorted(df['lot'].unique())
selected_lot = st.selectbox("Select a wine lot to analyze", lot_options)

# 📊 Filter selected lot
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

# 📊 Summary Stats
if selected_lot == "All Lots":
    st.subheader("📊 Summary by Lot (Averages)")
    st.dataframe(df.groupby('lot')[numeric_cols].mean().round(2))
else:
    st.subheader(f"📊 Summary Stats for {selected_lot}")
    summary = lot_df.describe()[numeric_cols]
    st.dataframe(summary)
    st.download_button(
        "📥 Download Summary CSV",
        summary.to_csv().encode('utf-8'),
        f"{selected_lot}_summary.csv",
        "text/csv"
    )

st.divider()

# 🧪 Flat Brix Check
if selected_lot != "All Lots":
    st.subheader("🛑 Flat Brix (Stuck Fermentation)")
    flat_brix = lot_df['brix'].diff().abs().rolling(3).sum() == 0
    if lot_df[flat_brix].empty:
        st.success("✅ No stuck fermentation detected.")
    else:
        st.warning("⚠️ Potential stuck fermentation detected!")
        st.dataframe(lot_df[flat_brix])
    st.divider()

# 📈 Variable Trends (numeric only)
st.subheader("📈 Variable Trends")
for col in numeric_cols:
    if lot_df[col].notna().sum() == 0:
        st.warning(f"⚠️ No data to plot for `{col}` — skipping.")
        continue

    st.write(f"**{col.upper()} Over Time**")
    fig, ax = plt.subplots()
    sns.lineplot(
        data=lot_df,
        x='datetime',
        y=col,
        hue='lot' if selected_lot == "All Lots" else None,
        marker='o',
        ax=ax
    )
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))  # Pretty dates
    fig.autofmt_xdate()
    st.pyplot(fig)

