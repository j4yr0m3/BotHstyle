import sqlite3
import os
import logging
from datetime import datetime

class DatabaseLogger:
    """
    SQLite database interface for storing trading transactions, execution history, and portfolio metrics.
    """
    def __init__(self, db_path: str = "trading_system.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("DatabaseLogger")
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    total_value REAL NOT NULL,
                    status TEXT DEFAULT 'EXECUTED'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    strategy_name TEXT NOT NULL,
                    total_return REAL,
                    win_rate REAL,
                    max_drawdown REAL,
                    sharpe_ratio REAL
                )
            """)
            conn.commit()
            self.logger.info("Database initialized successfully.")

    def log_transaction(self, symbol: str, order_type: str, quantity: float, price: float, status: str = "EXECUTED") -> int:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_value = round(quantity * price, 2)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (timestamp, symbol, order_type, quantity, price, total_value, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, symbol.upper(), order_type.upper(), quantity, price, total_value, status))
            conn.commit()
            transaction_id = cursor.lastrowid
            self.logger.info(f"Logged transaction #{transaction_id} to database.")
            return transaction_id

    def log_performance(self, strategy_name: str, metrics: dict):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO performance_metrics (timestamp, strategy_name, total_return, win_rate, max_drawdown, sharpe_ratio)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                strategy_name,
                metrics.get("total_return_pct"),
                metrics.get("win_rate_pct"),
                metrics.get("max_drawdown_pct"),
                metrics.get("sharpe_ratio")
            ))
            conn.commit()

    def get_all_transactions(self) -> list:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    db = DatabaseLogger()
    db.log_transaction("BTC/USD", "BUY", 0.25, 64000.0)
    print("Transactions:", db.get_all_transactions())