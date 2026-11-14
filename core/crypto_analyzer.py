import pandas as pd
from module.base_analyzer import TechnicalAnalyzer

class CryptoAnalyzer(TechnicalAnalyzer):
    def __init__(self, data: pd.DataFrame, coin: str = "BTC"):
        super().__init__(data)
        self.coin = coin

    def volume_breakout_strategy(self, volume_period: int = 20, multiplier: float = 1.5) -> str:
        avg_volume = self.data['Volume'].rolling(window=volume_period).mean().iloc[-1]
        current_volume = self.data['Volume'].iloc[-1]
        price_change = self.data['Close'].iloc[-1] - self.data['Open'].iloc[-1]

        if current_volume > avg_volume * multiplier:
            if price_change > 0:
                return "BUY (Volume Spike Upward)"
            else:
                return "SELL (Volume Spike Downward)"
        return "NEUTRAL (Normal Volume)"