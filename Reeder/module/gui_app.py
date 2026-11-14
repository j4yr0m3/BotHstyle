import queue
import tkinter as tk
from tkinter import ttk, scrolledtext
from InMemoryStore import InMemoryStore
from logger_config import setup_logging
from surveillance_engine import SurveillanceEngine

class TradingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Terminal de Trading Multi-Threaded")
        self.geometry("900x600")
        
        self.store = InMemoryStore()
        self.msg_queue = queue.Queue()
        self.surveillance = SurveillanceEngine(self.store, self.msg_queue)
        
        self.setup_ui()
        self.after(100, self.process_queue)

    def setup_ui(self):
        self.btn_start = ttk.Button(self, text="Démarrer Surveillance", command=self.start_engine)
        self.btn_start.pack(pady=10)
        
        self.log_widget = scrolledtext.ScrolledText(self, width=100, height=25)
        self.log_widget.pack(padx=10, pady=10)

    def start_engine(self):
        setup_logging()
        active_markets = ["Crypto", "Stock", "Forex"]
        self.surveillance.start_surveillance(active_markets)
        self.log_widget.insert(tk.END, "Moteur de surveillance lancé en arrière-plan.\n")

    def process_queue(self):
        while not self.msg_queue.empty():
            try:
                msg = self.msg_queue.get_nowait()
                if msg.get("type") == "SIGNAL":
                    data = msg["data"]
                    text = f"[{data['timestamp']}] {data['market']} - Action: {data['action']} @ {data['price']}\n"
                    self.log_widget.insert(tk.END, text)
                    self.log_widget.see(tk.END)
            except queue.Empty:
                break
        self.after(100, self.process_queue)