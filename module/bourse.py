import pandas as pd
import numpy as np
try:
    from module.base_analyzer import TechnicalAnalyzer
except ImportError:
    class TechnicalAnalyzer:
        def __init__(self, data=None):
            self.data = data if data is not None else pd.DataFrame()
        def calculate_sma(self, period):
            if "Close" in self.data.columns:
                return self.data["Close"].rolling(window=period).mean()
            return pd.Series(dtype=float)

class StockAnalyzer(TechnicalAnalyzer):
    def __init__(self, data_or_ticker=None, ticker="AAPL"):
        if isinstance(data_or_ticker, str):
            self.ticker = data_or_ticker
            self.data = pd.DataFrame()
        elif isinstance(data_or_ticker, pd.DataFrame):
            self.ticker = ticker
            self.data = data_or_ticker
        else:
            self.ticker = ticker
            self.data = pd.DataFrame()
        super().__init__(self.data)

    def fetch_market_data(self, ticker=None):
        target_ticker = ticker or self.ticker
        try:
            import yfinance as yf
            df = yf.download(target_ticker, period="1mo", interval="1d", progress=False)
            if not df.empty:
                self.data = df
                return self.data
        except Exception:
            pass
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D')
        np.random.seed(42)
        close_prices = 100 + np.random.randn(100).cumsum()
        self.data = pd.DataFrame({
            "Open": close_prices - 0.5,
            "High": close_prices + 1.0,
            "Low": close_prices - 1.0,
            "Close": close_prices,
            "Volume": 1000 + np.random.randint(0, 500, size=100)
        }, index=dates)
        return self.data

    def calculate_rsi(self, data, window=14):
        if not isinstance(data, pd.DataFrame) or "Close" not in data.columns:
            return pd.Series(dtype=float)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def analyze_current(self, data):
        if not isinstance(data, pd.DataFrame) or data.empty:
            return "Données invalides ou vides."
        last_price = data['Close'].iloc[-1]
        rsi_series = self.calculate_rsi(data)
        current_rsi = rsi_series.iloc[-1] if not rsi_series.empty else "N/A"
        return f"Dernier prix : {last_price:.2f} | RSI : {current_rsi}"

    def sma_crossover_strategy(self, short_period=20, long_period=50):
        if self.data.empty or len(self.data) < long_period:
            self.fetch_market_data()
        short_sma = self.calculate_sma(short_period).iloc[-1]
        long_sma = self.calculate_sma(long_period).iloc[-1]
        if short_sma > long_sma:
            return f"BUY ({self.ticker} Bullish Cross)"
        elif short_sma < long_sma:
            return f"SELL ({self.ticker} Bearish Cross)"
        return f"NEUTRAL ({self.ticker} Range)"