import pandas as pd
from module.base_analyzer import TechnicalAnalyzer

class GoldAnalyzer(TechnicalAnalyzer):
    def __init__(self, data: pd.DataFrame):
        super().__init__(data)

    def rsi_strategy(self, period: int = 14, overbought: float = 70.0, oversold: float = 30.0) -> str:
        rsi = self.calculate_rsi(period).iloc[-1]

        if rsi < oversold:
            return f"BUY (Oversold RSI: {rsi:.2f})"
        elif rsi > overbought:
            return f"SELL (Overbought RSI: {rsi:.2f})"

        return f"NEUTRAL (RSI: {rsi:.2f})"