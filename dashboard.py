import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("🍇 Fermentation Log Analyzer")

uploaded_file = st.file_uploader("Upload your fermentation CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    for col in ['Temp', 'Brix', 'pH']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(inplace=True)

    st.subheader("📊 Summary Stats")
    st.dataframe(df.describe()[['Temp', 'Brix', 'pH']])

    st.subheader("📉 Flat Brix (Stuck Fermentation)")
    flat_brix = df['Brix'].diff().abs().rolling(3).sum() == 0
    st.dataframe(df[flat_brix])

    st.subheader("📈 Variable Trends")
    for col in ['Temp', 'Brix', 'pH']:
        st.write(f"**{col} Over Time**")
        fig, ax = plt.subplots()
        sns.lineplot(x='Date', y=col, data=df, marker='o', ax=ax)
        st.pyplot(fig)
