import sys
import time
import threading
import logging
import asyncio

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

import yfinance as yf

try:
    from ib_insync import IB, Stock, MarketOrder, util
    util.patchAsyncio()
except ImportError:
    IB = None

class InMemoryStore:
    def __init__(self):
        self._lock = threading.Lock()
        self.ib = IB() if IB else None
        self.ib_connected = False
        self.auto_update = False
        self.bot_running = True
        self.advanced_mode = False
        self._data = {
            "balances": [
                {"asset": "USD", "balance": "10,329.75", "allocation": "80%", "pnl": "+$250.00"},
                {"asset": "EUR", "balance": "1,500.00", "allocation": "15%", "pnl": "+$65.00"},
                {"asset": "AAPL", "balance": "10.00", "allocation": "5%", "pnl": "+$14.75"},
            ],
            "signals": [
                {"pair": "EURUSD=X", "last": "1.0852", "trend": "BUY", "mean_rev": "HOLD", "breakout": "BUY", "carry": "BUY"},
                {"pair": "GBPUSD=X", "last": "1.2640", "trend": "SELL", "mean_rev": "BUY", "breakout": "NEUTRAL", "carry": "HOLD"},
                {"pair": "USDJPY=X", "last": "154.20", "trend": "BUY", "mean_rev": "HOLD", "breakout": "BUY", "carry": "BUY"},
            ],
            "advanced_metrics": {
                "sharpe_ratio": "2.45",
                "max_drawdown": "1.42%",
                "win_rate": "72.4%",
                "profit_factor": "2.18",
                "rsi": "64.2 (Bullish)",
                "var_95": "$115.20",
                "sortino_ratio": "3.12",
                "calmar_ratio": "3.65",
                "alpha": "+5.8%",
                "beta": "0.78",
                "volatility_ann": "9.8%",
                "avg_trade_pnl": "+$54.20"
            },
            "strategies": {
                "Mean Reversion Alpha": {"tp": "1.5", "sl": "0.8", "max_pos": "5000"},
                "Trend Following Momentum": {"tp": "3.0", "sl": "1.2", "max_pos": "10000"},
                "Breakout Volatility": {"tp": "2.5", "sl": "1.0", "max_pos": "7500"},
                "Carry Trade FX": {"tp": "1.2", "sl": "0.5", "max_pos": "15000"}
            }
        }
        self.market_ticks = []

    def start_auto_update(self):
        with self._lock:
            self.auto_update = True

    def stop_auto_update(self):
        with self._lock:
            self.auto_update = False

    def set_auto_update(self, enabled: bool):
        if enabled:
            self.start_auto_update()
        else:
            self.stop_auto_update()

    def is_auto_update_enabled(self):
        with self._lock:
            return self.auto_update

    def connect_ib(self, host="127.0.0.1", port=7497, client_id=1):
        if not self.ib:
            return False, "ib_insync non disponible"
        try:
            self.ib.connect(host, port, clientId=client_id)
            self.ib_connected = True
            return True, "Connecté à Interactive Brokers TWS/Gateway"
        except Exception as e:
            self.ib_connected = False
            return False, f"Échec de connexion IB: {e}"

    def fetch_yahoo_ticks(self, ticker="EURUSD=X"):
        try:
            data = yf.Ticker(ticker).history(period="1d", interval="1m")
            if not data.empty:
                prices = data["Close"].tolist()
                with self._lock:
                    self.market_ticks = prices[-20:]
                return prices[-1]
        except Exception as e:
            logging.error(f"Erreur Yahoo Finance: {e}")
            return None

    def place_ib_order(self, symbol, action, quantity):
        if not self.ib_connected or not self.ib:
            return False, "IB Non Connecté. Ordre simulé exécuté avec succès."
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            order = MarketOrder(action, quantity)
            trade = self.ib.placeOrder(contract, order)
            return True, f"Ordre IB transmis: {action} {quantity} {symbol} (ID: {trade.order.orderId})"
        except Exception as e:
            return False, f"Erreur lors de l'exécution de l'ordre IB: {e}"

    def get_balances(self):
        with self._lock:
            return self._data["balances"]

    def get_signals(self):
        with self._lock:
            return self._data["signals"]

    def get_advanced_metrics(self):
        with self._lock:
            return self._data["advanced_metrics"]

    def get_strategy_config(self, strategy_name):
        with self._lock:
            return self._data["strategies"].get(strategy_name, {"tp": "1.0", "sl": "1.0", "max_pos": "1000"})

    def save_strategy_config(self, strategy_name, tp, sl, max_pos):
        with self._lock:
            self._data["strategies"][strategy_name] = {"tp": tp, "sl": sl, "max_pos": max_pos}
            return True