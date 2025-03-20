from datetime import datetime
import pandas as pd

def calculate_returns(conn):
    # Get yesterday's and today's prices
    query = """
    SELECT Ticker, Date, Close 
    FROM historical_prices 
    WHERE Date IN (SELECT DISTINCT Date FROM historical_prices ORDER BY date DESC LIMIT 2)
    """
    df = pd.read_sql(query, conn)

    df = df.sort_values(by=["Ticker", "Date"]).drop_duplicates(subset=["Ticker", "Date"], keep="last")
    df_pivot = df.pivot(index="Ticker", columns="Date", values="Close")
    df_pivot["return"] = (df_pivot.iloc[:, 0] / df_pivot.iloc[:, 1] - 1).fillna(0)
    return df_pivot["return"].mean()

def update_index_performance(conn, daily_return):
    cursor = conn.cursor()
    today = datetime.today().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO index_performance (Date, daily_return) VALUES (?, ?)", (today, daily_return))
    print(pd.read_sql("select * from index_performance", conn))
    conn.commit()
