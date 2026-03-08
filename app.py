
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TQQQ Strategy Calc", page_icon="📈")

st.title("TQQQ Strategy Calculator")
st.write("This tool uses live data to backtest your buy-on-dip strategy.")

# User Inputs
ticker = st.sidebar.text_input("Ticker", value="TQQQ")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2010-02-11"))
investment = st.sidebar.number_input("Investment per Signal ($)", value=100)
threshold = st.slider("Drawdown Threshold (%)", -70, -10, -20) / 100

# Logic
@st.cache_data
def get_data(symbol, start):
    df = yf.download(symbol, start=start)
    # Fix for the yfinance update: flatten the nested columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

data = get_data(ticker, start_date)

def run_backtest(df, thresh, invest):
    df['Peak'] = df['Close'].cummax()
    df['Drawdown'] = (df['Close'] - df['Peak']) / df['Peak']
    trades, total_invested, units_held, waiting = 0, 0, 0, False
    
    for i in range(len(df)):
        price = df['Close'].iloc[i]
        dd = df['Drawdown'].iloc[i]
        if dd <= thresh and not waiting:
            trades += 1
            total_invested += invest
            units_held += (invest / price)
            waiting = True
        if waiting and dd == 0:
            waiting = False
            
    final_val = units_held * df['Close'].iloc[-1]
    roi = ((final_val - total_invested) / total_invested * 100) if total_invested > 0 else 0
    return trades, total_invested, final_val, roi

trades, invested, wealth, roi = run_backtest(data.copy(), threshold, investment)

# UI Display
c1, c2 = st.columns(2)
c1.metric("Total Invested", f"${invested:,.0f}")
c2.metric("Total Trades", f"{trades}")
c3, c4 = st.columns(2)
c3.metric("Final Wealth", f"${wealth:,.0f}")
c4.metric("ROI", f"{roi:,.1f}%")

st.line_chart(data['Close'])
