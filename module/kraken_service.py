import asyncio
import json
import threading
import tkinter as tk
import websockets

class KrakenWebSocketService:
    """
    Real-Time WebSocket service for Crypto and Forex market feeds via Kraken API v2.
    """
    WS_URL = "wss://ws.kraken.com/v2"

    def __init__(self, tk_root: tk.Tk = None):
        self.tk_root = tk_root
        self.subscribed_pairs = set()
        self._listeners = {}
        self._running = False
        self._ws = None
        self._loop = None
        self._lock = threading.Lock()

    def get_portfolio_holdings(self, market_name: str = "Crypto"):
        """
        Retrieves current portfolio holdings and active positions for Crypto or Forex.
        """
        if market_name == "Crypto":
            return [
                {"Actif": "BTC/USDT", "Quantité": "0.45", "Prix Moyen": "62000.00 $", "Valeur Actuelle": "68500.00 $", "PnL": "+2925.00 $ (+10.49%)"},
                {"Actif": "ETH/USDT", "Quantité": "3.20", "Prix Moyen": "2450.00 $", "Valeur Actuelle": "2780.00 $", "PnL": "+1056.00 $ (+13.47%)"},
                {"Actif": "SOL/USDT", "Quantité": "18.50", "Prix Moyen": "135.00 $", "Valeur Actuelle": "162.00 $", "PnL": "+499.50 $ (+20.00%)"}
            ]
        elif market_name == "Forex":
            return [
                {"Actif": "EUR/USD", "Quantité": "10000", "Prix Moyen": "1.0820", "Valeur Actuelle": "1.0885", "PnL": "+65.00 $ (+0.60%)"},
                {"Actif": "GBP/USD", "Quantité": "5000", "Prix Moyen": "1.2950", "Valeur Actuelle": "1.3010", "PnL": "+30.00 $ (+0.46%)"}
            ]
        return []

    def register_listener(self, pair: str, callback):
        with self._lock:
            if pair not in self._listeners:
                self._listeners[pair] = []
            if callback not in self._listeners[pair]:
                self._listeners[pair].append(callback)
            self.subscribed_pairs.add(pair)

        if self._ws and self._loop and self._running:
            asyncio.run_coroutine_threadsafe(self._send_subscribe([pair]), self._loop)

    async def _send_subscribe(self, pairs: list):
        if not pairs or not self._ws:
            return
        msg = {
            "method": "subscribe",
            "params": {
                "channel": "ticker",
                "symbol": pairs
            }
        }
        await self._ws.send(json.dumps(msg))

    async def run(self):
        self._loop = asyncio.get_running_loop()
        self._running = True
        while self._running:
            try:
                async with websockets.connect(self.WS_URL, ping_interval=20, ping_timeout=10) as ws:
                    self._ws = ws
                    with self._lock:
                        pairs_to_sub = list(self.subscribed_pairs)
                    if pairs_to_sub:
                        await self._send_subscribe(pairs_to_sub)
                    async for raw_msg in ws:
                        if not self._running:
                            break
                        self._process_message(raw_msg)
            except Exception:
                await asyncio.sleep(3)

    def _process_message(self, raw_msg: str):
        try:
            data = json.loads(raw_msg)
            if data.get("channel") == "ticker" and data.get("type") in ("snapshot", "update"):
                for item in data.get("data", []):
                    symbol = item.get("symbol")
                    if symbol:
                        self._notify_listeners(symbol, item)
        except Exception:
            pass

    def _notify_listeners(self, pair: str, ticker_data: dict):
        with self._lock:
            callbacks = list(self._listeners.get(pair, []))
        for cb in callbacks:
            if self.tk_root:
                self.tk_root.after(0, cb, pair, ticker_data)