import json
import logging
import pandas as pd
from strategies import ForexAnalyzer, CryptoAnalyzer, GoldAnalyzer, StockAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MarketOrchestrator:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.analyzers = {
            'forex': ForexAnalyzer,
            'crypto': CryptoAnalyzer,
            'gold': GoldAnalyzer,
            'stocks': StockAnalyzer
        }

    def _load_config(self) -> dict:
        """Charge la configuration JSON depuis le disque."""
        try:
            with open(self.config_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Erreur lors du chargement de la configuration: {e}")
            raise

    def fetch_market_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Simule la récupération de données de marché OHLCV."""
        # À remplacer par l'appel API réel (ex: CCXT, MetaTrader, Interactive Brokers)
        data = {
            'close': [1.0850, 1.0860, 1.0855, 1.0870, 1.0890],
            'high': [1.0855, 1.0865, 1.0860, 1.0875, 1.0895],
            'low': [1.0845, 1.0850, 1.0850, 1.0865, 1.0885],
            'volume': [1000, 1200, 1100, 1500, 2000]
        }
        return pd.DataFrame(data)

    def run_selected_analyses(self) -> dict:
        """Exécute les analyses uniquement sur les marchés activés dans la configuration."""
        results = {}
        markets = self.config.get('markets', {})
        for market_name, market_config in markets.items():
            if not market_config.get('enabled', False):
                logging.info(f"Marché '{market_name}' désactivé. Passé.")
                continue

            logging.info(f"Lancement de l'analyse pour le marché: {market_name}")
            analyzer_class = self.analyzers.get(market_name)
            if not analyzer_class:
                logging.warning(f"Aucun analyseur trouvé pour le marché '{market_name}'.")
                continue

            assets = market_config.get('pairs') or market_config.get('symbols', [])
            timeframe = market_config.get('timeframe', '1h')
            params = market_config.get('strategy_params', {})
            results[market_name] = {}

            for asset in assets:
                df = self.fetch_market_data(asset, timeframe)
                analyzer = analyzer_class(data=df, params=params)
                signal = analyzer.generate_signals()
                results[market_name][asset] = signal
                logging.info(f"[{market_name.upper()}] {asset} ({timeframe}) -> Signal: {signal}")

        return results

if __name__ == '__main__':
    orchestrator = MarketOrchestrator('config/strategies.json')
    report = orchestrator.run_selected_analyses()
    print("\n--- RAPPORT FINAL DES SIGNAUX ---")
    print(json.dumps(report, indent=2))