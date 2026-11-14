import sys
import time
import json
import urllib.request
import urllib.parse
import hashlib
import hmac
import base64
import threading
import logging
import random
from datetime import datetime
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "actif"})

def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()
    return "BotHstyle Est Actif"

def query_kraken_private(api_key, api_secret, urlpath, data=None):
    if data is None:
        data = {}
    api_key = api_key.strip()
    api_secret = api_secret.strip()
    data['nonce'] = int(1000 * time.time())
    headers = {
        'API-Key': api_key,
        'API-Sign': get_kraken_signature(urlpath, data, api_secret),
        'User-Agent': 'Kraken Execution Terminal'
    }
    req = urllib.request.Request(
        f"https://api.kraken.com{urlpath}",
        data=urllib.parse.urlencode(data).encode(),
        headers=headers
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

class InMemoryStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {
            "mode": "Simulation",
            "connection_status": "CONNECTED / SIMULATION",
            "api_key": "",
            "api_secret": "",
            "total_valuation_usd": 10345.05,
            "starting_balance_usd": 10000.00,
            "total_gains_usd": 450.25,
            "total_losses_usd": -120.50,
            "realized_pnl_usd": 329.75,
            "unrealized_pnl_usd": 15.30,
            "daily_pnl_pct": 3.45,
            "roi_pct": 3.45,
            "active_pair": "EUR/USD",
            "order_volume": 1000,
            "balances": {
                "ZUSD": {"balance": 10329.75, "allocation": "80%", "pnl_24h": "+$250.00"},
                "ZEUR": {"balance": 1500.00, "allocation": "15%", "pnl_24h": "+$65.00"},
                "XXBT": {"balance": 0.05, "allocation": "5%", "pnl_24h": "+$14.75"}
            },
            "signals": {
                "EUR/USD": {"last_price": 1.0850, "trend_follow": "BUY", "mean_rev": "HOLD", "breakout": "BUY", "carry_trade": "BUY"},
                "GBP/USD": {"last_price": 1.2640, "trend_follow": "SELL", "mean_rev": "BUY", "breakout": "NEUTRAL", "carry_trade": "HOLD"},
                "USD/JPY": {"last_price": 154.20, "trend_follow": "BUY", "mean_rev": "HOLD", "breakout": "BUY", "carry_trade": "BUY"}
            },
            "price_history": {
                "EUR/USD": [1.0840, 1.0842, 1.0845, 1.0848, 1.0852, 1.0849, 1.0850],
                "GBP/USD": [1.2630, 1.2635, 1.2638, 1.2642, 1.2640, 1.2639, 1.2640],
                "USD/JPY": [154.00, 154.05, 154.12, 154.18, 154.22, 154.19, 154.20]
            },
            "portfolio_history": [10000.00, 10050.00, 10120.00, 10090.00, 10210.00, 10280.00, 10345.05],
            "logs": []
        }

    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)

    def set(self, key, value):
        with self._lock:
            self._data[key] = value

    def update_balance(self, asset, amount):
        with self._lock:
            if asset in self._data["balances"] and isinstance(self._data["balances"][asset], dict):
                self._data["balances"][asset]["balance"] = amount
            else:
                self._data["balances"][asset] = amount

    def append_price(self, pair, price):
        with self._lock:
            if pair not in self._data["price_history"]:
                self._data["price_history"][pair] = []
            self._data["price_history"][pair].append(price)
            if len(self._data["price_history"][pair]) > 100:
                self._data["price_history"][pair].pop(0)

    def append_portfolio_valuation(self, valuation):
        with self._lock:
            self._data["portfolio_history"].append(valuation)
            if len(self._data["portfolio_history"]) > 100:
                self._data["portfolio_history"].pop(0)

    def record_trade_result(self, pnl):
        with self._lock:
            if pnl >= 0:
                self._data["total_gains_usd"] += pnl
            else:
                self._data["total_losses_usd"] += pnl
            self._data["realized_pnl_usd"] += pnl
            start = self._data["starting_balance_usd"]
            curr_val = start + self._data["realized_pnl_usd"] + self._data["unrealized_pnl_usd"]
            self._data["total_valuation_usd"] = curr_val
            self._data["roi_pct"] = round(((curr_val - start) / start) * 100, 2)
            self._data["portfolio_history"].append(curr_val)
            if len(self._data["portfolio_history"]) > 100:
                self._data["portfolio_history"].pop(0)

    def set_signal(self, pair, strategy, value):
        with self._lock:
            if pair not in self._data["signals"]:
                self._data["signals"][pair] = {}
            self._data["signals"][pair][strategy] = value

class LoggingEngine:
    def __init__(self, log_file="kraken_terminal.log"):
        self.log_file = log_file
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        formatted_entry = f"{timestamp} [{level}] {message}"
        if level == "ERROR":
            logging.error(message)
        else:
            logging.info(message)
        print(formatted_entry)

class SurveillanceEngine(threading.Thread):
    def __init__(self, store: InMemoryStore, logger: LoggingEngine):
        super().__init__()
        self.store = store
        self.logger = logger
        self.daemon = True
        self.running = False
        self.poll_interval = 2.5

    def start_engine(self):
        self.running = True
        self.start()
        self.logger.log("Automated surveillance & strategy engine STARTED.")

    def stop_engine(self):
        self.running = False
        self.logger.log("Automated strategy execution engine STOPPED.")

    def run(self):
        while self.running:
            try:
                self._fetch_market_data()
                self._evaluate_strategies()
                self._update_simulation_metrics()
                self._check_account_status()
            except Exception as e:
                self.logger.log(f"SurveillanceEngine Exception: {e}", level="ERROR")
            time.sleep(self.poll_interval)

    def _fetch_market_data(self):
        pair = self.store.get("active_pair", "EUR/USD")
        history = self.store.get("price_history", {}).get(pair, [1.0850])
        last_price = history[-1]
        scale = 0.0004 if "USD" in pair and "JPY" not in pair else 0.05
        delta = (random.random() - 0.485) * scale
        digits = 4 if "JPY" not in pair else 2
        new_price = round(last_price + delta, digits)
        self.store.append_price(pair, new_price)

    def _evaluate_strategies(self):
        pair = self.store.get("active_pair", "EUR/USD")
        prices = self.store.get("price_history", {}).get(pair, [])
        if len(prices) < 3:
            return
        sma_short = sum(prices[-3:]) / 3
        sma_long = sum(prices) / len(prices)
        trend = "BUY" if sma_short > sma_long else "SELL"
        mean_rev = "BUY" if prices[-1] < sma_long else "HOLD"
        breakout = "BUY" if prices[-1] == max(prices) else ("SELL" if prices[-1] == min(prices) else "NEUTRAL")
        carry = "BUY"
        self.store.set_signal(pair, "last_price", prices[-1])
        self.store.set_signal(pair, "trend_follow", trend)
        self.store.set_signal(pair, "mean_rev", mean_rev)
        self.store.set_signal(pair, "breakout", breakout)
        self.store.set_signal(pair, "carry_trade", carry)

    def _update_simulation_metrics(self):
        if random.random() < 0.25:
            pnl_delta = round((random.random() - 0.47) * 14.50, 2)
            self.store.record_trade_result(pnl_delta)

    def _check_account_status(self):
        mode = self.store.get("mode")
        if mode == "Real Money":
            api_key = self.store.get("api_key", "").strip()
            api_secret = self.store.get("api_secret", "").strip()
            if not api_key or not api_secret:
                self.logger.log("Private API Key or Secret missing.", level="ERROR")
                self.store.set("connection_status", "DISCONNECTED / ERROR")
            else:
                try:
                    res = query_kraken_private(api_key, api_secret, '/0/private/Balance')
                    if res.get('error'):
                        self.logger.log(f"Kraken API Error: {res['error']}", level="ERROR")
                        self.store.set("connection_status", "DISCONNECTED / ERROR")
                    else:
                        balances_data = res.get('result', {})
                        new_balances = {}
                        for asset, bal in balances_data.items():
                            val = float(bal)
                            new_balances[asset] = {
                                "balance": val,
                                "allocation": "-",
                                "pnl_24h": "-"
                            }
                        self.store.set("balances", new_balances)
                        self.store.set("connection_status", "CONNECTED / REAL MONEY")
                except Exception as e:
                    self.logger.log(f"Kraken Balance Query Exception: {e}", level="ERROR")
                    self.store.set("connection_status", "DISCONNECTED / ERROR")
        else:
            self.store.set("connection_status", "CONNECTED / SIMULATION")

if __name__ == "__main__":
    store = InMemoryStore()
    logger = LoggingEngine()
    engine = SurveillanceEngine(store, logger)
    logger.log("Initializing Kraken Forex Execution Terminal v3.0 (Headless Mode)...")
    engine.start_engine()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop_engine()
        logger.log("Terminal stopped by operator.")
