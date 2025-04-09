# 📦 Imports
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
import os

# 🎯 Page Title
st.title("🍇 Fermentation Log Analyzer")

# 📥 Sample File Download
sample_file_path = "data/sample_fermentation_log.csv"
if os.path.exists(sample_file_path):
    with open(sample_file_path, "rb") as f:
        sample_data = f.read()
        b64 = base64.b64encode(sample_data).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="sample_fermentation_log.csv">📥 Download Sample Fermentation Log</a>'
        st.markdown(href, unsafe_allow_html=True)

# 📂 File Upload
uploaded_file = st.file_uploader("Upload your fermentation CSV", type=["csv"])

# Brix drop threshold
BRIX_DROP_THRESHOLD = 8.0

# 🔄 Run everything only if file is uploaded
if uploaded_file:
    # 🧹 Read and clean data
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()

    # 🔎 Preview and validate columns
    st.write("🔎 Preview of uploaded data:", df.head())
    st.write("🍷 Lots detected in your file:", df['lot'].unique())

    required_columns = {'date', 'time', 'lot', 'temp', 'brix', 'ph'}
    if not required_columns.issubset(df.columns):
        st.error("❌ Uploaded file is missing one or more required columns: Date, Time, Lot, Temp, Brix, pH")
        st.stop()

    # 🧼 Clean types
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    for col in ['temp', 'brix', 'ph']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    # 🕒 Combine date and time
    df['datetime'] = pd.to_datetime(df['date'].dt.strftime('%Y-%m-%d') + ' ' + df['time'])
    df.sort_values(by=['lot', 'datetime'], inplace=True)

    # ⚠️ Check for rapid Brix drops
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

    # 🔀 Subset
    if selected_lot == "All Lots":
        lot_df = df.copy()
        st.subheader("📦 Overview: All Lots Combined")
    else:
        lot_df = df[df['lot'] == selected_lot]
        st.subheader(f"📌 Lot Details: {selected_lot}")
        first_date = lot_df['date'].min().strftime('%Y-%m-%d')
        last_date = lot_df['date'].max().strftime('%Y-%m-%d')
        duration = (lot_df['date'].max() - lot_df['date'].min()).days
        st.table({
            "Lot": [selected_lot],
            "Start Date": [first_date],
            "End Date": [last_date],
            "Duration (days)": [duration]
        })

    # 📊 Summary
    if selected_lot == "All Lots":
        st.subheader("📊 Summary by Lot (Averages)")
        summary = df.groupby('lot')[['temp', 'brix', 'ph']].mean().round(2)
        st.dataframe(summary)
    else:
        st.subheader(f"📊 Summary Stats for {selected_lot}")
        summary = lot_df.describe()[['temp', 'brix', 'ph']]
        st.dataframe(summary)

        # 💾 Download summary
        summary_csv = summary.to_csv().encode('utf-8')
        st.download_button(
            "📥 Download Summary by Lot",
            summary_csv,
            "all_lots_summary.csv",
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
        if selected_lot == "All Lots":
            sns.lineplot(data=lot_df, x='date', y=col, hue='lot', marker='o', ax=ax)
        else:
            sns.lineplot(data=lot_df, x='date', y=col, marker='o', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
