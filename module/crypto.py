import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    @staticmethod
    def calculate_rsi(series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @classmethod
    def get_market_signals(cls, config):
        # Simulation de données de marché avec gestion de la casse
        data = {
            'high': [102.0, 103.0, 102.5, 104.0, 103.5],
            'low': [99.0, 101.0, 100.0, 102.0, 101.5],
            'close': [100.0, 102.0, 101.0, 103.5, 103.0]
        }
        df = pd.DataFrame(data)
        
        # S'assurer que la colonne 'close' existe en minuscules
        df.columns = [col.lower() for col in df.columns]
        if 'close' not in df.columns:
            return {'signal': 'HOLD', 'close': 0.0}

        df['rsi'] = cls.calculate_rsi(df['close'])
        
        current_close = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        max_rsi = float(config.get('rsi_max', 70.0))

        if current_rsi < max_rsi:
            return {
                'signal': 'BUY',
                'close': current_close,
                'rsi': round(current_rsi, 2)
            }
        
        return {
            'signal': 'HOLD',
            'close': current_close,
            'rsi': round(current_rsi, 2)
        }

