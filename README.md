# **Hedgineer Custom Index Tracker**

## **📌 Project Overview**
This project constructs and tracks an **equal-weighted custom index** comprising the **top 100 US stocks** based on their **market capitalization**. The index updates **daily** based on market cap changes, ensuring that each stock maintains an **equal nominal contribution** to the index.

## **📂 Folder Structure**
```
Hedgineer_Assignment/
├── data/                  # Stores database files
│   ├── stock_data.sqlite  # SQLite database
├── src/                   # Main source code files
│   ├── APIDataExtraction.py   # Fetches top 100 US stock tickers, Retrieves market cap for selected tickers and Fetches historical stock data
│   ├── Index_calculatory.py       # Index calculator
│   ├── Dashboard.py       # Streamlit dashboard
├── requirements.txt       # List of dependencies
├── README.md              # Project documentation (this file)
└── presentation.pptx      # Project presentation
```

## **⚡ How to Set Up & Run**

### **1️⃣ Install Dependencies**
Ensure you have **Python 3.8+** installed. Then, install the required dependencies:
```sh
pip install -r requirements.txt
```

### **2️⃣ Run the Project**
The **orchestrator** script will execute all key steps automatically:
```sh
python src/APIDataExtraction.py
```

### **3️⃣ Run the Dashboard**
To visualize the data in a Streamlit dashboard, run:
```sh
streamlit src/APIDataExtraction.py
```
This will launch an interactive **dashboard** in your browser.

---

## **🚀 Features & Functionality**

### **🔹 Data Fetching & Storage**
1. **Fetch Top 100 Stocks**: Uses **TwelveData API** to fetch US stock tickers.
2. **Market Cap Retrieval**: Uses **Yahoo Finance API** to get stock market capitalization.
3. **Historical Data Storage**: Stores historical prices using **Yahoo Finance**.
4. **Database Storage**: All stock data is stored in an **SQLite database**.

### **📊 Index Calculation**
- The index ensures **equal weighting** across **100 stocks**.
- **Daily rebalancing** occurs based on **market cap changes**.
- Calculates **cumulative returns** & **daily percentage changes**.

### **📈 Streamlit Dashboard**
- **Performance Chart**: Shows cumulative index performance over time.
- **Composition Overview**: Displays stock weights for any selected day.
- **Composition Changes**: Highlights days when stocks entered/exited the index.
- **Summary Metrics**: Displays cumulative returns, daily percentage changes, and number of index rebalances.

---

## **📊 Data Sources**
- **[TwelveData API](https://twelvedata.com/stocks)** - Fetches stock tickers.
- **[Yahoo Finance API](https://finance.yahoo.com/)** - Fetches stock prices & market cap.
- **SQLite Database** - Stores stock data.

---

## **🛠 Tech Stack**
- **Programming Language**: Python 3.8+
- **Data Processing**: Pandas, SQLite3
- **APIs Used**: TwelveData, Yahoo Finance
- **Visualization**: Streamlit

---

## **📌 Challenges & Solutions**
| **Challenge** | **Solution** |
|--------------|-------------|
| API limits on free tier | Implemented caching and reduced API calls |
| Handling missing market cap values | Used exception handling and fallback methods |
| Streamlit dashboard performance | Optimized queries and used caching |

---

## **📑 Future Enhancements**
- **Enhance data accuracy** with alternative API sources.
- **Support for multiple indices** beyond top 100 US stocks.
- **More robust error handling** for API failures.
- **User-configurable dashboard filters**.
