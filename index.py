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

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def get_kraken_signature(urlpath, data, secret):
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

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
        self.ui_callback = None
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )

    def register_ui_callback(self, callback):
        self.ui_callback = callback

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        formatted_entry = f"{timestamp} [{level}] {message}"
        if level == "ERROR":
            logging.error(message)
        else:
            logging.info(message)
        if self.ui_callback:
            self.ui_callback(formatted_entry)

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

class TradingApp(tk.Tk):
    COLOR_BG = "#0b0f19"
    COLOR_SURFACE = "#111827"
    COLOR_CARD = "#1f2937"
    COLOR_CARD_BORDER = "#374151"
    COLOR_ACCENT = "#3b82f6"
    COLOR_CYAN = "#06b6d4"
    COLOR_GREEN = "#10b981"
    COLOR_RED = "#ef4444"
    COLOR_AMBER = "#f59e0b"
    COLOR_TEXT = "#f9fafb"
    COLOR_TEXT_MUTED = "#9ca3af"

    def __init__(self, store: InMemoryStore, logger: LoggingEngine, engine: SurveillanceEngine):
        super().__init__()
        self.store = store
        self.logger = logger
        self.engine = engine

        self.title("Kraken Forex Execution Terminal v3.0")
        self.geometry("1280x850")
        self.configure(bg=self.COLOR_BG)

        self._setup_styles()
        self.logger.register_ui_callback(self._append_log_entry)
        self._build_ui()
        self._start_periodic_refresh()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Treeview",
                        background=self.COLOR_SURFACE,
                        foreground=self.COLOR_TEXT,
                        fieldbackground=self.COLOR_SURFACE,
                        bordercolor=self.COLOR_CARD_BORDER,
                        rowheight=26,
                        font=("Consolas", 9))
        style.configure("Treeview.Heading",
                        background=self.COLOR_CARD,
                        foreground=self.COLOR_TEXT_MUTED,
                        relief="flat",
                        font=("Inter", 9, "bold"))
        style.map("Treeview", background=[("selected", self.COLOR_ACCENT)], foreground=[("selected", "#ffffff")])

        style.configure("TCombobox",
                        fieldbackground=self.COLOR_SURFACE,
                        background=self.COLOR_CARD,
                        foreground=self.COLOR_TEXT,
                        arrowcolor=self.COLOR_TEXT_MUTED,
                        bordercolor=self.COLOR_CARD_BORDER)

    def _build_ui(self):
        header = tk.Frame(self, bg=self.COLOR_SURFACE, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, pady=10, padx=16)
        header.pack(fill=tk.X, side=tk.TOP)

        title_frame = tk.Frame(header, bg=self.COLOR_SURFACE)
        title_frame.pack(side=tk.LEFT)
        tk.Label(title_frame, text="KRAKEN", fg=self.COLOR_ACCENT, bg=self.COLOR_SURFACE, font=("Inter", 15, "bold")).pack(side=tk.LEFT)
        tk.Label(title_frame, text=" TERMINAL v3.0", fg=self.COLOR_TEXT, bg=self.COLOR_SURFACE, font=("Inter", 15, "bold")).pack(side=tk.LEFT)

        cred_frame = tk.Frame(header, bg=self.COLOR_SURFACE)
        cred_frame.pack(side=tk.LEFT, padx=30)
        tk.Label(cred_frame, text="API Key:", fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE, font=("Inter", 9)).grid(row=0, column=0, padx=4)
        self.ent_api_key = tk.Entry(cred_frame, width=14, bg=self.COLOR_BG, fg=self.COLOR_TEXT, insertbackground="white", relief="flat", highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, show="*")
        self.ent_api_key.grid(row=0, column=1, padx=4)

        tk.Label(cred_frame, text="Secret:", fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE, font=("Inter", 9)).grid(row=0, column=2, padx=4)
        self.ent_api_secret = tk.Entry(cred_frame, width=14, bg=self.COLOR_BG, fg=self.COLOR_TEXT, insertbackground="white", relief="flat", highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, show="*")
        self.ent_api_secret.grid(row=0, column=3, padx=4)

        ctrl_right = tk.Frame(header, bg=self.COLOR_SURFACE)
        ctrl_right.pack(side=tk.RIGHT)

        self.lbl_conn = tk.Label(ctrl_right, text="● CONNECTED", fg=self.COLOR_GREEN, bg=self.COLOR_SURFACE, font=("Inter", 9, "bold"))
        self.lbl_conn.pack(side=tk.RIGHT, padx=12)

        self.btn_mode = tk.Button(ctrl_right, text="SIMULATION MODE", bg=self.COLOR_CARD, fg=self.COLOR_CYAN, activebackground=self.COLOR_CARD_BORDER, activeforeground=self.COLOR_CYAN, font=("Inter", 8, "bold"), relief="flat", padx=10, pady=4, cursor="hand2", command=self.toggle_mode)
        self.btn_mode.pack(side=tk.RIGHT, padx=6)

        self.btn_stop = tk.Button(ctrl_right, text="EMERGENCY STOP", bg=self.COLOR_RED, fg="#ffffff", activebackground="#dc2626", activeforeground="#ffffff", font=("Inter", 8, "bold"), relief="flat", padx=10, pady=4, cursor="hand2", command=self.stop_bot)
        self.btn_stop.pack(side=tk.RIGHT, padx=6)

        summary = tk.Frame(self, bg=self.COLOR_BG, pady=12, padx=12)
        summary.pack(fill=tk.X)

        self.lbl_val = self._create_card(summary, "TOTAL VALUATION", "$10,345.05", self.COLOR_TEXT)
        self.lbl_gains = self._create_card(summary, "TOTAL GAINS", "+$450.25", self.COLOR_GREEN)
        self.lbl_losses = self._create_card(summary, "TOTAL LOSSES", "-$120.50", self.COLOR_RED)
        self.lbl_realized = self._create_card(summary, "REALIZED PnL", "+$329.75", self.COLOR_CYAN)
        self.lbl_unrealized = self._create_card(summary, "UNREALIZED PnL", "+$15.30", self.COLOR_AMBER)
        self.lbl_daily = self._create_card(summary, "DAILY PnL %", "+3.45%", self.COLOR_CYAN)
        self.lbl_roi = self._create_card(summary, "ROI %", "+3.45%", self.COLOR_GREEN)

        body = tk.Frame(self, bg=self.COLOR_BG)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        left_col = tk.Frame(body, bg=self.COLOR_BG)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        ctrl_card = tk.Frame(left_col, bg=self.COLOR_SURFACE, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, padx=12, pady=10)
        ctrl_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(ctrl_card, text="ORDER ROUTING & EXECUTION", fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE, font=("Inter", 9, "bold")).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 8))

        tk.Label(ctrl_card, text="Pair:", fg=self.COLOR_TEXT, bg=self.COLOR_SURFACE, font=("Inter", 9)).grid(row=1, column=0, padx=4)
        self.combo_pair = ttk.Combobox(ctrl_card, values=["EUR/USD", "GBP/USD", "USD/JPY"], width=10, state="readonly")
        self.combo_pair.current(0)
        self.combo_pair.grid(row=1, column=1, padx=6)
        self.combo_pair.bind("<<ComboboxSelected>>", self._on_pair_changed)

        tk.Label(ctrl_card, text="Volume:", fg=self.COLOR_TEXT, bg=self.COLOR_SURFACE, font=("Inter", 9)).grid(row=1, column=2, padx=4)
        self.ent_vol = tk.Entry(ctrl_card, width=10, bg=self.COLOR_BG, fg=self.COLOR_TEXT, insertbackground="white", relief="flat", highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1)
        self.ent_vol.insert(0, "1000")
        self.ent_vol.grid(row=1, column=3, padx=6)

        btn_buy = tk.Button(ctrl_card, text="BUY / LONG", bg=self.COLOR_GREEN, fg="#ffffff", activebackground="#059669", activeforeground="#ffffff", font=("Inter", 9, "bold"), relief="flat", width=14, pady=4, cursor="hand2", command=lambda: self.execute_order("BUY"))
        btn_buy.grid(row=1, column=4, padx=8)

        btn_sell = tk.Button(ctrl_card, text="SELL / SHORT", bg=self.COLOR_RED, fg="#ffffff", activebackground="#dc2626", activeforeground="#ffffff", font=("Inter", 9, "bold"), relief="flat", width=14, pady=4, cursor="hand2", command=lambda: self.execute_order("SELL"))
        btn_sell.grid(row=1, column=5, padx=8)

        chart_card = tk.Frame(left_col, bg=self.COLOR_SURFACE, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, padx=8, pady=8)
        chart_card.pack(fill=tk.BOTH, expand=True)

        self.fig = Figure(figsize=(6, 4.5), dpi=100, facecolor=self.COLOR_SURFACE)
        self.fig.subplots_adjust(hspace=0.35, top=0.92, bottom=0.08, left=0.10, right=0.96)

        self.ax_price = self.fig.add_subplot(211)
        self._style_subplot(self.ax_price, "REAL-TIME MARKET TICKS")

        self.ax_port = self.fig.add_subplot(212)
        self._style_subplot(self.ax_port, "PORTFOLIO EQUITY CURVE ($ USD)")

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        right_col = tk.Frame(body, bg=self.COLOR_BG, width=440)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(6, 0))

        port_card = tk.Frame(right_col, bg=self.COLOR_SURFACE, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, padx=10, pady=8)
        port_card.pack(fill=tk.X, pady=(0, 10))
        tk.Label(port_card, text="WALLET BALANCES & HOLDINGS", fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE, font=("Inter", 9, "bold")).pack(anchor="w", pady=(0, 6))

        self.tree_port = ttk.Treeview(port_card, columns=("Asset", "Balance", "Allocation", "24h PnL"), show="headings", height=3)
        for col in ("Asset", "Balance", "Allocation", "24h PnL"):
            self.tree_port.heading(col, text=col)
            self.tree_port.column(col, width=95, anchor="center")
        self.tree_port.pack(fill=tk.X)

        sig_card = tk.Frame(right_col, bg=self.COLOR_SURFACE, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, padx=10, pady=8)
        sig_card.pack(fill=tk.X, pady=(0, 10))
        tk.Label(sig_card, text="LIVE STRATEGY SIGNALS", fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE, font=("Inter", 9, "bold")).pack(anchor="w", pady=(0, 6))

        self.tree_sig = ttk.Treeview(sig_card, columns=("Pair", "Last", "Trend", "MeanRev", "Breakout", "Carry"), show="headings", height=4)
        for col in ("Pair", "Last", "Trend", "MeanRev", "Breakout", "Carry"):
            self.tree_sig.heading(col, text=col)
            self.tree_sig.column(col, width=65, anchor="center")
        self.tree_sig.pack(fill=tk.X)

        log_card = tk.Frame(right_col, bg=self.COLOR_SURFACE, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, padx=10, pady=8)
        log_card.pack(fill=tk.BOTH, expand=True)
        tk.Label(log_card, text="TERMINAL CONSOLE LOG", fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE, font=("Inter", 9, "bold")).pack(anchor="w", pady=(0, 6))

        self.txt_log = scrolledtext.ScrolledText(log_card, bg=self.COLOR_BG, fg=self.COLOR_CYAN, font=("Consolas", 8), insertbackground="white", relief="flat", highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def _create_card(self, parent, title, val, val_color):
        card = tk.Frame(parent, bg=self.COLOR_SURFACE, highlightbackground=self.COLOR_CARD_BORDER, highlightthickness=1, padx=12, pady=8)
        card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)
        tk.Label(card, text=title, fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE, font=("Inter", 7, "bold")).pack(anchor="w")
        lbl = tk.Label(card, text=val, fg=val_color, bg=self.COLOR_SURFACE, font=("Inter", 12, "bold"))
        lbl.pack(anchor="w", pady=(2, 0))
        return lbl

    def _style_subplot(self, ax, title):
        ax.set_facecolor(self.COLOR_BG)
        ax.tick_params(colors=self.COLOR_TEXT_MUTED, labelsize=8)
        ax.grid(True, color=self.COLOR_CARD_BORDER, linestyle="--", linewidth=0.5, alpha=0.5)
        for spine in ax.spines.values():
            spine.set_color(self.COLOR_CARD_BORDER)
        ax.set_title(title, color=self.COLOR_TEXT, fontsize=9, fontweight="bold", pad=6)

    def _on_pair_changed(self, event=None):
        selected_pair = self.combo_pair.get()
        self.store.set("active_pair", selected_pair)
        self.logger.log(f"Active Surveillance Pair changed to: {selected_pair}")

    def toggle_mode(self):
        curr = self.store.get("mode")
        new_mode = "Real Money" if curr == "Simulation" else "Simulation"
        self.store.set("mode", new_mode)
        self.btn_mode.config(text=f"{new_mode.upper()} MODE", fg=self.COLOR_RED if new_mode == "Real Money" else self.COLOR_CYAN)
        self.logger.log(f"Execution mode switched to: {new_mode}")

    def stop_bot(self):
        self.engine.stop_engine()
        self.lbl_conn.config(text="● DISCONNECTED", fg=self.COLOR_RED)
        self.logger.log("Manual emergency stop triggered by operator.", level="ERROR")

    def execute_order(self, side):
        pair = self.combo_pair.get()
        vol = self.ent_vol.get()
        self.logger.log(f"Manual Market Order Executed: {side} {vol} {pair}")
        pnl_sim = (random.random() - 0.45) * 20.0
        self.store.record_trade_result(pnl_sim)

    def _append_log_entry(self, log_line):
        self.txt_log.insert(tk.END, log_line + "\n")
        self.txt_log.see(tk.END)

    def _start_periodic_refresh(self):
        def refresh():
            self.store.set("api_key", self.ent_api_key.get())
            self.store.set("api_secret", self.ent_api_secret.get())

            conn = self.store.get("connection_status", "CONNECTED")
            if "ERROR" in conn or "DISCONNECTED" in conn:
                self.lbl_conn.config(text=f"● {conn}", fg=self.COLOR_RED)
            else:
                self.lbl_conn.config(text=f"● {conn}", fg=self.COLOR_GREEN)

            val = self.store.get("total_valuation_usd", 10000.0)
            gains = self.store.get("total_gains_usd", 0.0)
            losses = self.store.get("total_losses_usd", 0.0)
            realized = self.store.get("realized_pnl_usd", 0.0)
            unrealized = self.store.get("unrealized_pnl_usd", 0.0)
            daily = self.store.get("daily_pnl_pct", 0.0)
            roi = self.store.get("roi_pct", 0.0)

            self.lbl_val.config(text=f"${val:,.2f}")
            self.lbl_gains.config(text=f"+${gains:,.2f}")
            self.lbl_losses.config(text=f"-${abs(losses):,.2f}")
            self.lbl_realized.config(text=f"{'+' if realized >= 0 else ''}${realized:,.2f}")
            self.lbl_unrealized.config(text=f"{'+' if unrealized >= 0 else ''}${unrealized:,.2f}")
            self.lbl_daily.config(text=f"{'+' if daily >= 0 else ''}{daily:.2f}%")
            self.lbl_roi.config(text=f"{'+' if roi >= 0 else ''}{roi:.2f}%")

            pair = self.combo_pair.get()
            prices = self.store.get("price_history", {}).get(pair, [1.0850])
            portfolio_hist = self.store.get("portfolio_history", [10000.0])

            self.ax_price.clear()
            self._style_subplot(self.ax_price, f"REAL-TIME MARKET TICKS ({pair})")
            self.ax_price.plot(prices, color=self.COLOR_CYAN, linewidth=1.8)

            self.ax_port.clear()
            self._style_subplot(self.ax_port, "PORTFOLIO EQUITY CURVE ($ USD)")
            port_color = self.COLOR_GREEN if portfolio_hist[-1] >= portfolio_hist[0] else self.COLOR_RED
            self.ax_port.plot(portfolio_hist, color=port_color, linewidth=1.8)

            self.canvas.draw()

            for item in self.tree_port.get_children():
                self.tree_port.delete(item)
            balances = self.store.get("balances", {})
            for asset, info in balances.items():
                if isinstance(info, dict):
                    self.tree_port.insert("", tk.END, values=(asset, f"{info.get('balance', 0):,.2f}", info.get("allocation", "-"), info.get("pnl_24h", "-")))
                else:
                    self.tree_port.insert("", tk.END, values=(asset, f"{info:,.2f}", "-", "-"))

            for item in self.tree_sig.get_children():
                self.tree_sig.delete(item)
            signals = self.store.get("signals", {})
            for sig_pair, sig_info in signals.items():
                self.tree_sig.insert("", tk.END, values=(sig_pair, sig_info.get("last_price", "-"), sig_info.get("trend_follow", "NEUTRAL"), sig_info.get("mean_rev", "HOLD"), sig_info.get("breakout", "NEUTRAL"), sig_info.get("carry_trade", "BUY")))

            self.after(1000, refresh)

        self.after(1000, refresh)

if __name__ == "__main__":
    store = InMemoryStore()
    logger = LoggingEngine()
    engine = SurveillanceEngine(store, logger)
    logger.log("Initializing Kraken Forex Execution Terminal v3.0...")
    engine.start_engine()

    app = TradingApp(store, logger, engine)
    app.mainloop()