import tkinter as tk
from tkinter import ttk
from gui.gui_stock import StockDashboardModule
from gui.gui_forex import ForexDashboardModule
from gui.gui_gold import GoldDashboardModule
from gui.gui_crypto import CryptoDashboardModule

class OrchestrateurTradingGUI(tk.Tk):
    """
    Application principale - Orchestrateur de Trading.
    """
    def __init__(self, ibkr_service=None):
        super().__init__()
        self.title("ORCHESTRATEUR DE TRADING MULTI-ACTIFS")
        self.geometry("900x650")
        self.configure(bg="#1e1e1e")
        self.ibkr_service = ibkr_service

        self._build_main_ui()

    def _build_main_ui(self):
        title_lbl = tk.Label(self, text="ORCHESTRATEUR DE TRADING MULTI-ACTIFS", font=("Helvetica", 16, "bold"), fg="#ffffff", bg="#0055ff", pady=10)
        title_lbl.pack(fill="x")

        frame_select = tk.LabelFrame(self, text=" Sélection des Marchés ", fg="white", bg="#252526", font=("Helvetica", 10, "bold"), padx=10, pady=10)
        frame_select.pack(fill="x", padx=15, pady=10)

        self.var_stock = tk.BooleanVar(value=True)
        self.var_forex = tk.BooleanVar(value=True)
        self.var_gold = tk.BooleanVar(value=True)
        self.var_crypto = tk.BooleanVar(value=True)

        tk.Checkbutton(frame_select, text="Stock", variable=self.var_stock, bg="#252526", fg="white", selectcolor="#333333").pack(side=tk.LEFT, padx=15)
        tk.Checkbutton(frame_select, text="Forex", variable=self.var_forex, bg="#252526", fg="white", selectcolor="#333333").pack(side=tk.LEFT, padx=15)
        tk.Checkbutton(frame_select, text="Gold", variable=self.var_gold, bg="#252526", fg="white", selectcolor="#333333").pack(side=tk.LEFT, padx=15)
        tk.Checkbutton(frame_select, text="Crypto", variable=self.var_crypto, bg="#252526", fg="white", selectcolor="#333333").pack(side=tk.LEFT, padx=15)

        frame_dashboards = tk.LabelFrame(self, text=" Tableaux Individuels ", fg="white", bg="#252526", font=("Helvetica", 10, "bold"), padx=10, pady=10)
        frame_dashboards.pack(fill="x", padx=15, pady=10)

        tk.Button(frame_dashboards, text="Refresh Stock Interface", bg="#00aa55", fg="white", command=self.open_stock_window).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_dashboards, text="Refresh Forex Interface", bg="#00aa55", fg="white", command=self.open_forex_window).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_dashboards, text="Refresh Gold Interface", bg="#00aa55", fg="white", command=self.open_gold_window).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_dashboards, text="Refresh Crypto Interface", bg="#00aa55", fg="white", command=self.open_crypto_window).pack(side=tk.LEFT, padx=10)

        frame_console = tk.LabelFrame(self, text=" Console & Statut d'Orchestration ", fg="white", bg="#252526", font=("Helvetica", 10, "bold"))
        frame_console.pack(fill="both", expand=True, padx=15, pady=10)

        self.txt_console = tk.Text(frame_console, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.txt_console.pack(fill="both", expand=True, padx=5, pady=5)
        self.txt_console.insert(tk.END, "--- Dashboard Orchestrateur Initialisé ---\n")

    def _open_sub_window(self, title, module_class):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry("950x550")
        module = module_class(win, ibkr_service=self.ibkr_service)
        module.pack(fill="both", expand=True)

    def open_stock_window(self):
        self._open_sub_window("Tableau de Bord Dédié (Stock)", StockDashboardModule)

    def open_forex_window(self):
        self._open_sub_window("Tableau de Bord Dédié (Forex)", ForexDashboardModule)

    def open_gold_window(self):
        self._open_sub_window("Tableau de Bord Dédié (Gold)", GoldDashboardModule)

    def open_crypto_window(self):
        self._open_sub_window("Tableau de Bord Dédié (Crypto)", CryptoDashboardModule)

if __name__ == "__main__":
    app = OrchestrateurTradingGUI()
    app.mainloop()