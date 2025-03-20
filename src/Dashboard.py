import sqlite3
import streamlit as st
import pandas as pd

def show_dashboard():
    conn = sqlite3.connect("../data/stock_data.sqlite")
    st.title("Equal-Weighted Index Dashboard")

    # Performance Chart
    perf_df = pd.read_sql("SELECT * FROM index_performance", conn)
    print(perf_df)
    perf_df["Date"] = pd.to_datetime(perf_df["Date"])

    # ✅ Set Date as Index
    perf_df.set_index("Date", inplace=True)

    # ✅ Plot Line Chart
    st.line_chart(perf_df)

    composition_df = pd.read_sql("SELECT Date, Symbol, MarketCap FROM stocks", conn)
    # market_cap_df = pd.read_sql("SELECT Date, Symbol, MarketCap FROM stocks", conn)
    # historical_prices_df = pd.read_sql("SELECT * FROM historical_prices", conn)
    # historical_prices_df.rename(columns={"Ticker": "Symbol"}, inplace=True)

    # composition_df = pd.merge(market_cap_df, historical_prices_df, on=['Date', 'Symbol'], how="right")

    # Ensure Date column is in datetime format
    composition_df["Date"] = pd.to_datetime(composition_df["Date"] ,errors="coerce")

    # Select unique dates for dropdown
    unique_dates = composition_df["Date"].dt.date.unique()

    # **User selects a date**
    selected_date = st.selectbox("📅 Select a Date", unique_dates)

    # **Filter data for selected date**
    filtered_df = composition_df[composition_df["Date"].dt.date == selected_date]

    # **Normalize MarketCap to show weights (percentage)**
    filtered_df["Weight (%)"] = (filtered_df["MarketCap"] / filtered_df["MarketCap"].sum()) * 100

    # **Display Data as a Table**
    st.subheader("📊 Index Composition")
    st.dataframe(filtered_df.sort_values(by="MarketCap", ascending=False))

    # **Display Bar Chart**
    st.subheader("📈 Market Cap Distribution")
    st.bar_chart(filtered_df.set_index("Symbol")["MarketCap"])

    perf_df["Cumulative Return"] = (1 + perf_df["daily_return"]).cumprod() - 1

    # **Compute Daily Percentage Changes**
    perf_df["Daily Change (%)"] = perf_df["daily_return"] * 100  # Convert to %

    # **Find Composition Changes**
    comp_changes = []
    prev_day_composition = set()

    for date in composition_df["Date"].unique():
        current_day_composition = set(composition_df[composition_df["Date"] == date]["Symbol"])

        # Identify changes
        added_stocks = current_day_composition - prev_day_composition
        removed_stocks = prev_day_composition - current_day_composition

        if added_stocks or removed_stocks:
            comp_changes.append({"Date": date, "Changes": len(added_stocks) + len(removed_stocks)})

        prev_day_composition = current_day_composition

    comp_changes_df = pd.DataFrame(comp_changes)

    # **Calculate Total Composition Changes**
    total_changes = comp_changes_df["Changes"].sum() if not comp_changes_df.empty else 0

    # **Display Summary Metrics**
    st.subheader("📊 Index Summary Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("📈 Cumulative Return", f"{perf_df['Cumulative Return'].iloc[-1]:.2%}")
    col2.metric("📊 Average Daily Change", f"{perf_df['Daily Change (%)'].mean():.2f}%")
    col3.metric("🔄 Total Composition Changes", f"{total_changes}")

    # **Plot Cumulative Returns**
    st.subheader("📈 Cumulative Performance Over Time")
    print(perf_df.reset_index().columns)
    perf_df.reset_index(inplace=True)
    st.line_chart(perf_df.set_index('Date')["Cumulative Return"])

    # Composition Changes
    changes_df = pd.read_sql("SELECT * FROM historical_prices", conn)
    st.write("Composition Changes:", changes_df)
    import os
    # Export to Excel
    if st.button("Export to Excel"):
        # perf_df.to_excel("index_performance.xlsx", index=False
        file_path = os.path.join(os.getcwd(), "index_performance.xlsx")
        perf_df.to_excel(file_path, index=False)
        st.success(f"Excel file saved at: {file_path}")
