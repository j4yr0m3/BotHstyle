import tkinter as tk
from tkinter import ttk, messagebox
from gui.context_menu import TradingContextMenu

class CryptoDashboardModule(ttk.Frame):
    """
    Tableau de bord dédié au marché des Cryptomonnaies.
    """
    def __init__(self, parent, ibkr_service=None):
        super().__init__(parent)
        self.parent = parent
        self.ibkr_service = ibkr_service
        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self, text="TABLEAU DE BORD DÉDIÉ (Crypto)", font=("Helvetica", 14, "bold"))
        header.pack(pady=10)

        tree_frame = ttk.LabelFrame(self, text=" Holdings Cryptomonnaies ")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("symbol", "quantity", "avg_price", "current_value", "pnl")
        self.tree_crypto = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        self.tree_crypto.heading("symbol", text="Crypto")
        self.tree_crypto.heading("quantity", text="Quantité")
        self.tree_crypto.heading("avg_price", text="Prix Moyen ($)")
        self.tree_crypto.heading("current_value", text="Valeur Actuelle ($)")
        self.tree_crypto.heading("pnl", text="P&L ($)")

        self.tree_crypto.column("symbol", width=120, anchor="center")
        self.tree_crypto.column("quantity", width=120, anchor="center")
        self.tree_crypto.column("avg_price", width=120, anchor="center")
        self.tree_crypto.column("current_value", width=140, anchor="center")
        self.tree_crypto.column("pnl", width=140, anchor="center")

        self.tree_crypto.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree_crypto.insert("", "end", values=("BTC/USD", "0.50", "62 000.00", "34 500.00", "+3 500.00 (+11.29%)"))
        self.tree_crypto.insert("", "end", values=("ETH/USD", "4.00", "3 100.00", "13 600.00", "+1 200.00 (+9.68%)"))

        self.ctx_menu = TradingContextMenu(
            parent=self, 
            treeview=self.tree_crypto, 
            asset_type="CRYPTO", 
            ibkr_client=self.ibkr_service
        )