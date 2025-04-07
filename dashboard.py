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
    
    # 🧹 Data Cleaning
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    for col in ['Temp', 'Brix', 'pH']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    # ✅ Check for required columns
    required_columns = {'Date', 'Temp', 'Brix', 'pH'}
    if not required_columns.issubset(df.columns):
        st.error("❌ Uploaded file is missing one or more required columns: Date, Temp, Brix, pH")
        st.stop()

    # 📊 Summary Statistics
    st.subheader("📊 Summary Stats")
    summary = df.describe()[['Temp', 'Brix', 'pH']]
    st.dataframe(summary)

    # 💾 Downloadable Summary
    summary_csv = summary.to_csv().encode('utf-8')
    st.download_button(
        "📥 Download Summary CSV",
        summary_csv,
        "summary_stats.csv",
        "text/csv"
    )
    st.divider()

    # ⚠️ Flat Brix / Stuck Fermentation Detection
    st.subheader("📉 Flat Brix (Stuck Fermentation)")
    flat_brix = df['Brix'].diff().abs().rolling(3).sum() == 0

    if df[flat_brix].empty:
        st.success("✅ No stuck fermentation detected.")
    else:
        st.warning("⚠️ Potential stuck fermentation detected!")
        st.dataframe(df[flat_brix])
    st.divider()

    # 📈 Plotting Temp, Brix, pH Over Time
    st.subheader("📈 Variable Trends")
    for col in ['Temp', 'Brix', 'pH']:
        st.write(f"**{col} Over Time**")
        fig, ax = plt.subplots()
        sns.lineplot(x='Date', y=col, data=df, marker='o', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
