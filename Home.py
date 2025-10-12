import streamlit as st
import pandas as pd
import plotly.express as px

from services.calculations import calculate_metrics
from services.db import create_tables, fetch_all_properties

st.set_page_config(page_title="Real Estate Analyzer", layout="wide")
st.title("🏠 Real Estate Investment Analyzer")

create_tables()

st.title("📊 Portfolio Overview")

props = fetch_all_properties()

if props:
    data = []
    for prop in props:
        metrics = calculate_metrics(prop)
        data.append({"Address": prop.address, **metrics})

    df = pd.DataFrame(data)

    # Summary Metrics
    total_cash_flow = df["Monthly Cash Flow"].sum()
    avg_cap_rate = df["Cap Rate (%)"].mean()
    avg_coc_return = df["Cash-on-Cash Return (%)"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("🏦 Total Monthly Cash Flow", f"${total_cash_flow:,.2f}")
    col2.metric("📈 Avg Cap Rate", f"{avg_cap_rate:.2f}%")
    col3.metric("💰 Avg Cash-on-Cash Return", f"{avg_coc_return:.2f}%")

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.bar(df, x="Address", y="Monthly Cash Flow", title="Monthly Cash Flow by Property", text_auto=".2f")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.bar(df, x="Address", y="Cap Rate (%)", title="Cap Rate by Property", color="Cap Rate (%)", text_auto=".2f")
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df.set_index("Address"), use_container_width=True)

else:
    st.info("No properties found yet. Add one below!")

st.sidebar.divider()
st.sidebar.info("Real Estate Analyzer • by Cameron Pokorny")