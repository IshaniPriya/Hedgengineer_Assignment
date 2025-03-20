import requests
import os
import sqlite3
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from index_calculator import calculate_returns, update_index_performance
from Dashboard import show_dashboard

pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)  # Prevent line breaks
pd.set_option('display.max_colwidth', None)  # Show full content in each cell

# Your Twelve Data API Key
TWELVE_API_KEY = "<<API KEY>>"

# SQLite Database Path
DB_PATH = "../data/stock_data.sqlite"

# Number of Top Stocks to Track
TOP_N_STOCKS = 100


# ==========================================================
# STEP 1: Fetch Stock Tickers from Twelve Data
# ==========================================================
def get_tickers(api_key):
    url = "https://api.twelvedata.com/stocks"
    params = {"exchange": "NASDAQ", "apikey": api_key}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        df = pd.json_normalize(data['data'])
        return df
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


# ==========================================================
# STEP 2: Fetch Market Cap & Price Data
# ==========================================================
def get_market_cap(ticker_list):
    top_tickers = ticker_list[:TOP_N_STOCKS]
    data = []

    for ticker in top_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if "marketCap" in info and "currentPrice" in info:
                data.append({
                    "symbol": ticker,
                    "market_cap": info["marketCap"],
                    "price": info["currentPrice"]
                })
        except Exception as ex:
            print(f"⚠️ Error fetching market cap for {ticker}: {ex}")

    return pd.DataFrame(data)


# ==========================================================
# STEP 3: Create Database Tables
# ==========================================================
def create_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            Date DATE,
            Symbol TEXT,
            MarketCap REAL,
            Price REAL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS historical_prices (
            Date TEXT,
            Ticker TEXT,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Volume INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS index_performance (
            Date DATE,
            daily_return REAL
        )
    """)


# ==========================================================
# STEP 4: Store Market Cap Data in Database
# ==========================================================
def update_market_cap_data(df, conn):
    df.rename(columns={"market_cap" : "MarketCap"}, inplace=True)

    df["Date"] = datetime.today().strftime("%Y-%m-%d")

    # ✅ Drop duplicate tickers
    df.drop_duplicates(subset=["Date", "symbol"], keep="last", inplace=True)

    # ✅ Save data safely
    df.to_sql("stocks", conn, if_exists="append", index=False)


# ==========================================================
# STEP 5: Fetch & Store Historical Stock Data
# ==========================================================
def fetch_historical_data(tickers, conn):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)

    for ticker in tickers:
        try:
            print(f"📊 Fetching historical data for {ticker}...")
            stock = yf.Ticker(ticker)
            stock_data = stock.history(start=start_date, end=end_date)

            if stock_data.empty:
                print(f"⚠️ No data found for {ticker}. Skipping.")
                continue

            stock_data["Ticker"] = ticker
            stock_data.drop(columns=["Dividends", "Stock Splits"], inplace=True)
            stock_data.to_sql("historical_prices", conn, if_exists="append", index=True)

            print(f"✅ {ticker} data saved successfully.")

        except Exception as e:
            print(f"❌ Error fetching data for {ticker}: {e}")

    print("🚀 Historical stock data fetching completed!")


# ==========================================================
# STEP 6: Orchestrator Function to Run Everything
# ==========================================================
def orchestrator():
    print("🚀 Starting Orchestration Process...")

    DB_PATH = "../data/stock_data.sqlite"

    # ✅ Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    print("✅ Database connected successfully!")
    # exit()

    # Step 2: Fetch Stock Tickers
    print("📥 Fetching stock tickers...")
    result_tickers = get_tickers(TWELVE_API_KEY)

    if result_tickers is None:
        print("❌ Error: Could not retrieve tickers.")
        return

    # Step 3: Create Database Tables
    create_tables(conn)

    # Step 4: Fetch Market Cap Data
    print("📊 Fetching market cap data...")
    ticker_list = result_tickers['symbol'].tolist()
  
    # ticker_list = [
    #     "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B", "JPM", "V",
    #     "UNH", "JNJ", "PG", "HD", "MA", "DIS", "PYPL", "NFLX", "ADBE", "PFE",
    #     "KO", "MRNA", "PEP", "CRM", "TMO", "ABT", "BMY", "NKE", "XOM", "T",
    #     "COST", "LLY", "MCD", "HON", "IBM", "GS", "TXN", "ORCL", "CVX", "QCOM",
    #     "AMGN", "INTC", "MDT", "LMT", "NOW", "DHR", "UNP", "SBUX", "ISRG", "AVGO",
    #     "LOW", "DOW", "BLK", "AMD", "CAT", "ZTS", "RTX", "CVS", "MO", "SPGI",
    #     "MMM", "BA", "C", "TGT", "CSCO", "GE", "USB", "GILD", "FDX", "PGR",
    #     "MET", "ADP", "SO", "SCHW", "DUK", "BDX", "LRCX", "AON", "ATVI", "NSC",
    #     "CCI", "AEP", "ITW", "PLD", "TJX", "ICE", "FIS", "EQIX", "WM", "CL",
    #     "VRTX", "APD", "REGN", "AIG", "EOG", "MS", "HCA", "COP", "MMC", "FISV"
    # ]
    df_market_cap = get_market_cap(ticker_list)
    df_market_cap.drop_duplicates(inplace=True)

    # Step 5: Store Market Cap Data in Database
    update_market_cap_data(df_market_cap, conn)

    # Step 6: Fetch Historical Stock Data
    print("📈 Fetching historical stock data...")
    fetch_historical_data(ticker_list, conn)

    # Step 7: Calculate Index Performance
    print("📊 Calculating Index Performance...")
    daily_returns = calculate_returns(conn)
    update_index_performance(conn, daily_returns)
    print(pd.read_sql("SELECT * FROM index_performance", conn))

    # Step 8: Display Dashboard
    print("📊 Launching Dashboard...")
    show_dashboard()

    # Step 9: Close Database Connection
    conn.close()
    print("✅ Orchestration Completed!")


# ==========================================================
# Run the Orchestrator
# ==========================================================
if __name__ == "__main__":
    orchestrator()
