import pandas as pd
import numpy as np

class BaseAnalyzer:
    """Classe de base pour tous les analyseurs de marché."""
    def __init__(self, data: pd.DataFrame, params: dict):
        self.data = data
        self.params = params

    def calculate_indicators(self):
        raise NotImplementedError("La méthode doit être implémentée.")

    def generate_signals(self) -> str:
        raise NotImplementedError("La méthode doit être implémentée.")


class ForexAnalyzer(BaseAnalyzer):
    """Analyseur dédié au marché Forex (Stratégie SMA Crossover + RSI)."""
    def calculate_indicators(self):
        fast_p = self.params.get('fast_period', 14)
        slow_p = self.params.get('slow_period', 50)
        rsi_p = self.params.get('rsi_period', 14)
        
        # Calcul des moyennes mobiles
        self.data['sma_fast'] = self.data['close'].rolling(window=fast_p).mean()
        self.data['sma_slow'] = self.data['close'].rolling(window=slow_p).mean()
        
        # Calcul du RSI
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_p).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_p).mean()
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))

    def generate_signals(self) -> str:
        self.calculate_indicators()
        last_row = self.data.iloc[-1]
        prev_row = self.data.iloc[-2]
        
        # Logique de signal BUY
        if prev_row['sma_fast'] <= prev_row['sma_slow'] and last_row['sma_fast'] > last_row['sma_slow']:
            if last_row['rsi'] < self.params.get('overbought', 70):
                return 'BUY'
        # Logique de signal SELL
        elif prev_row['sma_fast'] >= prev_row['sma_slow'] and last_row['sma_fast'] < last_row['sma_slow']:
            if last_row['rsi'] > self.params.get('oversold', 30):
                return 'SELL'
        return 'HOLD'


class CryptoAnalyzer(BaseAnalyzer):
    """Analyseur dédié au marché des Cryptomonnaies (Breakout Momentum)."""
    def calculate_indicators(self):
        rsi_p = self.params.get('rsi_period', 14)
        self.data['vol_sma'] = self.data['volume'].rolling(window=20).mean()
        self.data['high_max'] = self.data['high'].rolling(window=20).max()

    def generate_signals(self) -> str:
        self.calculate_indicators()
        last_row = self.data.iloc[-1]
        if last_row['close'] >= last_row['high_max'] and last_row['volume'] > last_row['vol_sma'] * 1.5:
            return 'BUY'
        return 'HOLD'


class GoldAnalyzer(BaseAnalyzer):
    """Analyseur dédié au marché de l'Or."""
    def calculate_indicators(self):
        window = self.params.get('window', 14)
        self.data['min_low'] = self.data['low'].rolling(window=window).min()
        self.data['max_high'] = self.data['high'].rolling(window=window).max()

    def generate_signals(self) -> str:
        self.calculate_indicators()
        last_row = self.data.iloc[-1]
        if last_row['close'] <= last_row['min_low']:
            return 'BUY'
        elif last_row['close'] >= last_row['max_high']:
            return 'SELL'
        return 'HOLD'


class StockAnalyzer(BaseAnalyzer):
    """Analyseur dédié au marché des Actions (RSI Mean Reversion)."""
    def calculate_indicators(self):
        rsi_p = self.params.get('rsi_period', 14)
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_p).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_p).mean()
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))

    def generate_signals(self) -> str:
        self.calculate_indicators()
        last_row = self.data.iloc[-1]
        if last_row['rsi'] < self.params.get('oversold', 30):
            return 'BUY'
        elif last_row['rsi'] > self.params.get('overbought', 70):
            return 'SELL'
        return 'HOLD'