import os
import csv
import logging
from datetime import datetime

class OrderSimulator:
    """
    Simulates trading order executions and logs transactions with timestamp,
    symbol, quantity, order type, and price.
    """
    def __init__(self, log_file: str = "simulated_orders.csv"):
        self.log_file = log_file
        self.orders = []
        self._setup_logging()
        self._init_csv()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("order_simulator.log", mode="a")
            ]
        )
        self.logger = logging.getLogger("OrderSimulator")

    def _init_csv(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Symbol", "OrderType", "Quantity", "Price", "TotalValue"])

    def record_order(self, symbol: str, order_type: str, quantity: float, price: float) -> dict:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_value = round(quantity * price, 2)
        
        order = {
            "timestamp": timestamp,
            "symbol": symbol.upper(),
            "order_type": order_type.upper(),
            "quantity": float(quantity),
            "price": float(price),
            "total_value": total_value
        }
        
        self.orders.append(order)
        self._log_to_file(order)
        self.logger.info(f"Order Executed: {order['order_type']} {order['quantity']} {order['symbol']} @ ${order['price']:.2f} (Total: ${total_value:.2f})")
        
        return order

    def _log_to_file(self, order: dict):
        with open(self.log_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                order["timestamp"],
                order["symbol"],
                order["order_type"],
                order["quantity"],
                order["price"],
                order["total_value"]
            ])

    def get_order_history(self) -> list:
        return self.orders

if __name__ == "__main__":
    simulator = OrderSimulator()
    simulator.record_order("BTC/USD", "BUY", 0.5, 65000.0)
    simulator.record_order("EUR/USD", "SELL", 1000, 1.0850)