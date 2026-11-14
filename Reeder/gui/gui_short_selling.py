import tkinter as tk
from tkinter import ttk, messagebox

class ShortSellingModule(ttk.Frame):
    """
    Module dédié aux opérations de Vente à Découvert (Short Selling).
    """
    def __init__(self, parent, ibkr_service=None):
        super().__init__(parent)
        self.parent = parent
        self.ibkr_service = ibkr_service
        self._build_ui()

    def _build_ui(self):
        header = ttk.Label(self, text="MODULE VENTE À DÉCOUVERT (Short Selling)", font=("Helvetica", 14, "bold"))
        header.pack(pady=10)

        order_frame = ttk.LabelFrame(self, text=" Passage d'Ordre Short ")
        order_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(order_frame, text="Actif:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_symbol = ttk.Entry(order_frame, width=12)
        self.entry_symbol.insert(0, "TSLA")
        self.entry_symbol.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(order_frame, text="Quantité:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_qty = ttk.Entry(order_frame, width=10)
        self.entry_qty.insert(0, "50")
        self.entry_qty.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(order_frame, text="Type Ordre:").grid(row=0, column=4, padx=5, pady=5)
        self.combo_ord_type = ttk.Combobox(order_frame, values=["Au Marché", "Limité"], width=10, state="readonly")
        self.combo_ord_type.set("Au Marché")
        self.combo_ord_type.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(order_frame, text="Vendre à Découvert (Short)", command=self._execute_short).grid(row=0, column=6, padx=5, pady=5)
        ttk.Button(order_frame, text="Racheter (Cover)", command=self._execute_cover).grid(row=0, column=7, padx=5, pady=5)

        tree_frame = ttk.LabelFrame(self, text=" Positions Vente à Découvert Actives ")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("asset", "short_qty", "short_price", "current_price", "borrow_rate", "unrealized_pnl")
        self.tree_short = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        self.tree_short.heading("asset", text="Actif")
        self.tree_short.heading("short_qty", text="Qté Short")
        self.tree_short.heading("short_price", text="Prix Vente ($)")
        self.tree_short.heading("current_price", text="Prix Actuel ($)")
        self.tree_short.heading("borrow_rate", text="Frais Emprunt")
        self.tree_short.heading("unrealized_pnl", text="P&L Latent ($)")

        for col in columns:
            self.tree_short.column(col, width=120, anchor="center")

        self.tree_short.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_short.insert("", "end", values=("TSLA", "-50", "220.00", "205.00", "1.25%", "+$750.00 (+6.82%)"))

    def _execute_short(self):
        messagebox.showinfo("Vente à Découvert", f"Ordre Short ({self.combo_ord_type.get()}) pour {self.entry_qty.get()} x {self.entry_symbol.get()} transmis.")

    def _execute_cover(self):
        messagebox.showinfo("Rachat de Marge", f"Ordre Cover ({self.combo_ord_type.get()}) pour {self.entry_qty.get()} x {self.entry_symbol.get()} transmis.")