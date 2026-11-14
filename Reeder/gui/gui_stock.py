import tkinter as tk
from tkinter import ttk, messagebox
from gui.context_menu import StockContextMenu

class StockDashboardModule(ttk.Frame):
    """
    Tableau de bord pour le marché des Actions (Stock) avec menu contextuel intégré.
    """
    def __init__(self, parent, ibkr_service=None):
        super().__init__(parent)
        self.parent = parent
        self.ibkr_service = ibkr_service
        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self, text="TABLEAU DE BORD DÉDIÉ (Stock)", font=("Helvetica", 14, "bold"))
        header.pack(pady=10)

        tree_frame = ttk.LabelFrame(self, text=" Portefeuille & Actifs Détenus (Clic Droit pour Actions) ")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("asset", "quantity", "avg_price", "current_value", "pnl")
        self.tree_stock = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        self.tree_stock.heading("asset", text="Actif")
        self.tree_stock.heading("quantity", text="Quantité")
        self.tree_stock.heading("avg_price", text="Prix Moyen ($)")
        self.tree_stock.heading("current_value", text="Valeur Actuelle ($)")
        self.tree_stock.heading("pnl", text="P&L ($)")

        for col in columns:
            self.tree_stock.column(col, width=120, anchor="center")

        self.tree_stock.pack(fill="both", expand=True, padx=5, pady=5)

        # Exemples de données
        self.tree_stock.insert("", "end", values=("AAPL", "50", "175.20", "9 425.00", "+665.00 (+7.59%)"))
        self.tree_stock.insert("", "end", values=("NVDA", "20", "450.00", "9 800.00", "+800.00 (+8.89%)"))
        self.tree_stock.insert("", "end", values=("MSFT", "15", "330.00", "5 220.00", "+270.00 (+5.45%)"))

        # Association du menu contextuel personnalisé
        self.ctx_menu = StockContextMenu(
            parent=self, 
            treeview=self.tree_stock, 
            ibkr_client=self.ibkr_service
        )