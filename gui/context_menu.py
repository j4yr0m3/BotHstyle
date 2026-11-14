import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class StockContextMenu:
    """
    Menu contextuel (clic droit) pour le module Stock.
    Options : Achat, Vente, Type d'ordre (Marché / Limité), Options et Vente à découvert.
    """
    def __init__(self, parent, treeview, ibkr_client=None):
        self.parent = parent
        self.treeview = treeview
        self.ibkr_client = ibkr_client

        self.menu = tk.Menu(self.parent, tearoff=0)
        self._build_menu()
        self.treeview.bind("<Button-3>", self._show_menu)

    def _build_menu(self):
        # Achat / Vente
        self.menu.add_command(label="Acheter (Buy)", command=lambda: self._place_order("BUY"))
        self.menu.add_command(label="Vendre (Sell)", command=lambda: self._place_order("SELL"))
        self.menu.add_separator()

        # Type d'Ordre
        order_type_menu = tk.Menu(self.menu, tearoff=0)
        order_type_menu.add_command(label="Ordre au Marché (Market)", command=lambda: self._set_order_type("MARKET"))
        order_type_menu.add_command(label="Ordre Limité (Limit)", command=lambda: self._set_order_type("LIMIT"))
        self.menu.add_cascade(label="Type d'Ordre", menu=order_type_menu)
        self.menu.add_separator()

        # Extensions : Options & Vente à découverte
        self.menu.add_command(label="Négocier Options (Call/Put)", command=self._open_options_dialog)
        self.menu.add_command(label="Vente à Découvert (Short)", command=self._open_short_dialog)

        self.current_order_type = "MARKET"

    def _show_menu(self, event):
        item = self.treeview.identify_row(event.y)
        if item:
            self.treeview.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def _get_selected_symbol(self):
        selected = self.treeview.selection()
        if not selected:
            return None
        values = self.treeview.item(selected[0], "values")
        return values[0] if values else None

    def _set_order_type(self, order_type):
        self.current_order_type = order_type
        messagebox.showinfo("Type d'Ordre", f"Type d'ordre configuré sur : {order_type}")

    def _place_order(self, action):
        symbol = self._get_selected_symbol()
        if not symbol:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un actif.")
            return

        qty = simpledialog.askinteger("Quantité", f"Quantité à {'acheter' if action == 'BUY' else 'vendre'} pour {symbol} :", minvalue=1)
        if not qty:
            return

        limit_price = None
        if self.current_order_type == "LIMIT":
            limit_price = simpledialog.askfloat("Prix Limité", f"Entrez le prix limité pour {symbol} ($) :")
            if not limit_price:
                return

        price_info = f"au prix limité de ${limit_price:.2f}" if limit_price else "au cours du marché"
        messagebox.showinfo("Ordre Transmis", f"Ordre {action} {qty} x {symbol} ({self.current_order_type}) {price_info} transmis.")

    def _open_options_dialog(self):
        symbol = self._get_selected_symbol() or "AAPL"
        messagebox.showinfo("Options", f"Ouverture de la chaîne d'options pour l'actif {symbol}.")

    def _open_short_dialog(self):
        symbol = self._get_selected_symbol() or "TSLA"
        messagebox.showinfo("Vente à Découvert", f"Ouverture du module de vente à découvert pour {symbol}.")