import tkinter as tk
from tkinter import ttk, messagebox
from gui.context_menu import TradingContextMenu

class ForexDashboardModule(ttk.Frame):
    """
    Tableau de bord dédié aux paires Forex.
    """
    def __init__(self, parent, ibkr_service=None):
        super().__init__(parent)
        self.parent = parent
        self.ibkr_service = ibkr_service
        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self, text="TABLEAU DE BORD DÉDIÉ (Forex)", font=("Helvetica", 14, "bold"))
        header.pack(pady=10)

        tree_frame = ttk.LabelFrame(self, text=" Positions Forex Actives ")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("pair", "units", "entry_rate", "current_rate", "pnl")
        self.tree_forex = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        self.tree_forex.heading("pair", text="Paire")
        self.tree_forex.heading("units", text="Lots / Unités")
        self.tree_forex.heading("entry_rate", text="Taux Entrée")
        self.tree_forex.heading("current_rate", text="Taux Actuel")
        self.tree_forex.heading("pnl", text="P&L ($)")

        self.tree_forex.column("pair", width=120, anchor="center")
        self.tree_forex.column("units", width=120, anchor="center")
        self.tree_forex.column("entry_rate", width=120, anchor="center")
        self.tree_forex.column("current_rate", width=120, anchor="center")
        self.tree_forex.column("pnl", width=140, anchor="center")

        self.tree_forex.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree_forex.insert("", "end", values=("EUR/USD", "100 000", "1.0850", "1.0910", "+600.00 USD"))
        self.tree_forex.insert("", "end", values=("GBP/USD", "50 000", "1.2620", "1.2685", "+325.00 USD"))

        self.ctx_menu = TradingContextMenu(
            parent=self, 
            treeview=self.tree_forex, 
            asset_type="FOREX", 
            ibkr_client=self.ibkr_service
        )