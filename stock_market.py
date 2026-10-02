import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import os

# Gemini Client Initialization with Fallback
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

client = None
if GEMINI_API_KEY:
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        client = None

def render_stock_page():
    st.title("📈 Stock Market Analysis")

    # Popular Stock Options (Company Name -> Ticker Symbol)
    stock_options = {
        "Reliance Industries": "RELIANCE.NS",
        "TCS (Tata Consultancy Services)": "TCS.NS",
        "Infosys": "INFY.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "Tata Motors": "TATAMOTORS.NS",
        "Apple Inc.": "AAPL",
        "Tesla Inc.": "TSLA",
        "Microsoft": "MSFT",
        "Google (Alphabet)": "GOOGL",
        "🔍 Type Custom Ticker...": "CUSTOM"
    }

    selected_option = st.selectbox(
        "Select Stock Company or Custom Ticker:",
        options=list(stock_options.keys())
    )

    # Custom ticker handler
    if stock_options[selected_option] == "CUSTOM":
        ticker_symbol = st.text_input(
            "Enter Any Stock Ticker (e.g. WIPRO.NS, NVDA, AMZN):", 
            value=""
        ).strip().upper()
    else:
        ticker_symbol = stock_options[selected_option]

    if ticker_symbol:
        st.write("")

        # Timeframe Options Mapping (Period, Interval)
        tf_options = {
            "1D": ("1d", "5m"),     
            "1W": ("5d", "15m"),    
            "1M": ("1mo", "1d"),    
            "1Y": ("1y", "1d"),     
            "3Y": ("3y", "1wk")     
        }

        st.markdown("##### ⏱️ Select Timeframe:")
        try:
            selected_tf = st.segmented_control(
                "Timeframe", 
                options=list(tf_options.keys()), 
                default="1Y",
                label_visibility="collapsed"
            )
        except AttributeError:
            selected_tf = st.radio(
                "Timeframe", 
                options=list(tf_options.keys()), 
                index=3, 
                horizontal=True,
                label_visibility="collapsed"
            )

        # Fix for KeyError: If selected_tf is None or invalid, default to '1Y'
        if not selected_tf or selected_tf not in tf_options:
            selected_tf = "1Y"

        period, interval = tf_options[selected_tf]

        try:
            with st.spinner(f"Fetching data for {ticker_symbol}..."):
                stock = yf.Ticker(ticker_symbol)
                df = stock.history(period=period, interval=interval)

                # Fallback if 1D interval is empty (e.g. market closed)
                if df.empty and selected_tf == "1D":
                    df = stock.history(period="5d", interval="1d").tail(1)

            if not df.empty:
                df = df.reset_index()
                date_col = 'Datetime' if 'Datetime' in df.columns else 'Date'

                # KPI METRIC CARDS
                latest_close = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2] if len(df) > 1 else latest_close
                price_change = latest_close - prev_close
                pct_change = (price_change / prev_close) * 100 if prev_close != 0 else 0

                high_price = df['High'].max()
                low_price = df['Low'].min()
                total_volume = df['Volume'].sum()
                latest_open = df['Open'].iloc[-1]

                currency_symbol = "₹" if ".NS" in ticker_symbol or ".BO" in ticker_symbol else "$"

                st.subheader("📊 Key Performance Metrics")
                col1, col2, col3, col4, col5 = st.columns(5)

                col1.metric("Last Close", f"{currency_symbol}{latest_close:,.2f}", f"{pct_change:+.2f}%")
                col2.metric("Open Price", f"{currency_symbol}{latest_open:,.2f}")
                col3.metric("Period High", f"{currency_symbol}{high_price:,.2f}")
                col4.metric("Period Low", f"{currency_symbol}{low_price:,.2f}")
                col5.metric("Total Volume", f"{total_volume:,.0f}")

                st.divider()

                # CLOSING PRICE CHART
                st.subheader(f"📈 {ticker_symbol} - Closing Price ({selected_tf})")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df[date_col], 
                    y=df['Close'], 
                    mode='lines', 
                    name='Close Price',
                    line=dict(color='#FF7A45', width=2)
                ))
                
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=10, r=10, t=20, b=20),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)"),
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)

                st.divider()

                # GEMINI AI STOCK INSIGHTS
                st.subheader("🤖 AI Stock Analysis")
                if st.button("✨ Generate Gemini AI Stock Report", key="ai_stock_btn"):
                    if not GEMINI_API_KEY or not client:
                        st.warning("⚠️ Streamlit Secrets me `GEMINI_API_KEY` add nahi kiya hai. Settings -> Secrets me key set karein.")
                    else:
                        with st.spinner("Analyzing stock trends with Gemini AI..."):
                            try:
                                sample_stock_data = df.tail(15)[[date_col, 'Open', 'High', 'Low', 'Close', 'Volume']].to_string(index=False)
                                prompt = f"""
                                You are a professional Stock Market Financial Analyst.
                                Analyze the following recent stock data for {ticker_symbol}:
                                {sample_stock_data}

                                Provide a short, structured summary:
                                1. Recent Price Trend & Volatility
                                2. Volume Trend Analysis
                                3. Short-term Market Outlook
                                4. Important Observations
                                Keep it clear, concise, and professional.
                                """
                                response = client.models.generate_content(
                                    model="gemini-2.5-flash",
                                    contents=prompt
                                )
                                st.markdown(response.text)
                            except Exception as ai_err:
                                st.error(f"Error generating AI analysis: {ai_err}")

                st.divider()

                # STOCK DATA TABLE
                st.subheader("📋 Stock Data Table")
                st.dataframe(df, use_container_width=True)

            else:
                st.error(f"❌ Invalid ticker symbol '{ticker_symbol}' or no data available. Indian stocks ke liye aage `.NS` lagayein (jaise `WIPRO.NS`).")

        except Exception as e:
            st.error(f"⚠️ Error fetching stock data: {e}")
    else:
        st.info("👆 Above selectbox me se company select karein ya ticker enter karein.")
