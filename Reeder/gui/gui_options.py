import tkinter as tk
from tkinter import ttk, messagebox

class OptionsDashboardModule(ttk.Frame):
    """
    Module dédié à la négociation d'options (Calls / Puts, Strikes, Échéances).
    """
    def __init__(self, parent, ibkr_service=None):
        super().__init__(parent)
        self.parent = parent
        self.ibkr_service = ibkr_service
        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self, text="MODULE TRADING D'OPTIONS (Calls / Puts)", font=("Helvetica", 14, "bold"))
        header.pack(pady=10)

        order_frame = ttk.LabelFrame(self, text=" Ordre d'Option ")
        order_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(order_frame, text="Sous-jacent:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_underlying = ttk.Entry(order_frame, width=10)
        self.entry_underlying.insert(0, "AAPL")
        self.entry_underlying.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(order_frame, text="Type:").grid(row=0, column=2, padx=5, pady=5)
        self.combo_type = ttk.Combobox(order_frame, values=["CALL", "PUT"], width=6, state="readonly")
        self.combo_type.set("CALL")
        self.combo_type.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(order_frame, text="Strike ($):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_strike = ttk.Entry(order_frame, width=10)
        self.entry_strike.insert(0, "180.00")
        self.entry_strike.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(order_frame, text="Type Ordre:").grid(row=0, column=6, padx=5, pady=5)
        self.combo_ord_type = ttk.Combobox(order_frame, values=["Au Marché", "Limité"], width=10, state="readonly")
        self.combo_ord_type.set("Au Marché")
        self.combo_ord_type.grid(row=0, column=7, padx=5, pady=5)

        ttk.Button(order_frame, text="Acheter", command=self._buy_option).grid(row=0, column=8, padx=5, pady=5)
        ttk.Button(order_frame, text="Vendre", command=self._sell_option).grid(row=0, column=9, padx=5, pady=5)

        tree_frame = ttk.LabelFrame(self, text=" Positions Options Actives ")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("contract", "underlying", "type", "strike", "expiry", "qty", "avg_cost", "mkt_price", "pnl")
        self.tree_options = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        self.tree_options.heading("contract", text="Contrat")
        self.tree_options.heading("underlying", text="Sous-jacent")
        self.tree_options.heading("type", text="Type")
        self.tree_options.heading("strike", text="Strike ($)")
        self.tree_options.heading("expiry", text="Échéance")
        self.tree_options.heading("qty", text="Contrats")
        self.tree_options.heading("avg_cost", text="Prime Moy. ($)")
        self.tree_options.heading("mkt_price", text="Prix Mkt ($)")
        self.tree_options.heading("pnl", text="P&L ($)")

        for col in columns:
            self.tree_options.column(col, width=100, anchor="center")

        self.tree_options.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_options.insert("", "end", values=("AAPL 180C 18DEC26", "AAPL", "CALL", "180.00", "2026-12-18", "5", "4.20", "5.80", "+$800.00 (+38.1%)"))

    def _buy_option(self):
        messagebox.showinfo("Ordre d'Option", f"Achat de contrat {self.combo_type.get()} sur {self.entry_underlying.get()} Strike ${self.entry_strike.get()} ({self.combo_ord_type.get()}) transmis.")

    def _sell_option(self):
        messagebox.showinfo("Ordre d'Option", f"Vente de contrat {self.combo_type.get()} sur {self.entry_underlying.get()} Strike ${self.entry_strike.get()} ({self.combo_ord_type.get()}) transmise.")