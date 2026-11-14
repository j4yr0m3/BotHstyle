import pandas as pd
from module.base_analyzer import TechnicalAnalyzer

class ForexAnalyzer(TechnicalAnalyzer):
    def __init__(self, data: pd.DataFrame, currency_pairs=None):
        super().__init__(data)
        self.currency_pairs = currency_pairs if currency_pairs is not None else ["EUR/USD", "GBP/USD", "USD/JPY"]

    def trend_following_strategy(self, short_period: int = 50, long_period: int = 200) -> str:
        short_sma = self.calculate_sma(short_period).iloc[-1]
        long_sma = self.calculate_sma(long_period).iloc[-1]

        if short_sma > long_sma:
            return "BUY (Bullish Trend)"
        elif short_sma < long_sma:
            return "SELL (Bearish Trend)"
        return "NEUTRAL"