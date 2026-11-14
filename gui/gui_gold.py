import tkinter as tk
from tkinter import ttk, messagebox
from gui.context_menu import TradingContextMenu

class GoldDashboardModule(ttk.Frame):
    """
    Tableau de bord dédié au marché de l'Or / Métaux.
    """
    def __init__(self, parent, ibkr_service=None):
        super().__init__(parent)
        self.parent = parent
        self.ibkr_service = ibkr_service
        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self, text="TABLEAU DE BORD DÉDIÉ (Gold)", font=("Helvetica", 14, "bold"))
        header.pack(pady=10)

        tree_frame = ttk.LabelFrame(self, text=" Positions Or & Métaux ")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("asset", "quantity", "avg_price", "current_value", "pnl")
        self.tree_gold = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        self.tree_gold.heading("asset", text="Actif")
        self.tree_gold.heading("quantity", text="Quantité (Oz)")
        self.tree_gold.heading("avg_price", text="Prix Moyen ($)")
        self.tree_gold.heading("current_value", text="Valeur Actuelle ($)")
        self.tree_gold.heading("pnl", text="P&L ($)")

        self.tree_gold.column("asset", width=120, anchor="center")
        self.tree_gold.column("quantity", width=120, anchor="center")
        self.tree_gold.column("avg_price", width=120, anchor="center")
        self.tree_gold.column("current_value", width=140, anchor="center")
        self.tree_gold.column("pnl", width=140, anchor="center")

        self.tree_gold.pack(fill="both", expand=True, padx=5, pady=5)

        self.tree_gold.insert("", "end", values=("XAU/USD", "10 oz", "2 350.00", "24 100.00", "+600.00 (+2.55%)"))
        self.tree_gold.insert("", "end", values=("XAG/USD", "200 oz", "28.50", "5 900.00", "+200.00 (+3.51%)"))

        self.ctx_menu = TradingContextMenu(
            parent=self, 
            treeview=self.tree_gold, 
            asset_type="GOLD", 
            ibkr_client=self.ibkr_service
        )