# 📦 Imports
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 🎯 Page Title
st.title("🍇 Fermentation Log Analyzer")

# 📂 File Upload
uploaded_file = st.file_uploader("Upload your fermentation CSV", type=["csv"])

# 🔄 Run only if file is uploaded
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 🧹 Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # ✅ Check for required columns
    required_columns = {'date', 'lot', 'temp', 'brix', 'ph'}
    if not required_columns.issubset(df.columns):
        st.error("❌ Uploaded file is missing one or more required columns: Date, Lot, Temp, Brix, pH")
        st.stop()

    # 🧼 Data Cleaning
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    for col in ['temp', 'brix', 'ph']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    # 🍷 Select the wine lot
    selected_lot = st.selectbox("Select a wine lot to analyze", sorted(df['lot'].unique()))
    lot_df = df[df['lot'] == selected_lot]
    
    st.markdown(f"### 📌 Analyzing Lot: `{selected_lot}`")

    first_date = lot_df['date'].min().strftime('%Y-%m-%d')
    last_date = lot_df['date'].max().strftime('%Y-%m-%d')
    st.markdown(f"📅 Date Range: `{first_date}` to `{last_date}`")


    # 📊 Summary Statistics
    st.subheader(f"📊 Summary Stats for {selected_lot}")
    summary = lot_df.describe()[['temp', 'brix', 'ph']]
    st.dataframe(summary)

    # 💾 Downloadable Summary
    summary_csv = summary.to_csv().encode('utf-8')
    st.download_button(
        "📥 Download Summary CSV",
        summary_csv,
        f"{selected_lot}_summary_stats.csv",
        "text/csv"
    )
    st.divider()

    # ⚠️ Flat Brix / Stuck Fermentation Detection
    st.subheader("📉 Flat Brix (Stuck Fermentation)")
    flat_brix = lot_df['brix'].diff().abs().rolling(3).sum() == 0

    if lot_df[flat_brix].empty:
        st.success("✅ No stuck fermentation detected.")
    else:
        st.warning("⚠️ Potential stuck fermentation detected!")
        st.dataframe(lot_df[flat_brix])
    st.divider()

    # 📈 Plotting Temp, Brix, pH Over Time
    st.subheader("📈 Variable Trends")
    for col in ['temp', 'brix', 'ph']:
        st.write(f"**{col.capitalize()} Over Time for {selected_lot}**")
        fig, ax = plt.subplots()
        sns.lineplot(x='date', y=col, data=lot_df, marker='o', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
