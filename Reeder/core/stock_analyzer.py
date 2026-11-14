import pandas as pd
from module.base_analyzer import TechnicalAnalyzer

class StockAnalyzer(TechnicalAnalyzer):
    def __init__(self, data: pd.DataFrame, ticker: str = "AAPL"):
        super().__init__(data)
        self.ticker = ticker

    def sma_crossover_strategy(self, short_period: int = 20, long_period: int = 50) -> str:
        short_sma = self.calculate_sma(short_period).iloc[-1]
        long_sma = self.calculate_sma(long_period).iloc[-1]

        if short_sma > long_sma:
            return f"BUY ({self.ticker} Bullish Cross)"
        elif short_sma < long_sma:
            return f"SELL ({self.ticker} Bearish Cross)"
        return f"NEUTRAL ({self.ticker} Range)"