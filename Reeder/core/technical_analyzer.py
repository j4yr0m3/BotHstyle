import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def calculate_sma(self, period: int = 20) -> pd.Series:
        return self.data['Close'].rolling(window=period).mean()

    def calculate_ema(self, period: int = 20) -> pd.Series:
        return self.data['Close'].ewm(span=period, adjust=False).mean()

    def calculate_rsi(self, period: int = 14) -> pd.Series:
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2):
        sma = self.calculate_sma(period)
        rolling_std = self.data['Close'].rolling(window=period).std()
        upper_band = sma + (rolling_std * std_dev)
        lower_band = sma - (rolling_std * std_dev)
        return upper_band, sma, lower_band