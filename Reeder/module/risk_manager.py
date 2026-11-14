import logging

class RiskManager:
    """
    Manages risk parameters including Stop-Loss (SL), Take-Profit (TP), 
    and position sizing based on risk percentage per trade.
    """
    def __init__(self, default_risk_pct: float = 2.0, default_reward_risk_ratio: float = 2.0):
        self.default_risk_pct = default_risk_pct
        self.default_reward_risk_ratio = default_reward_risk_ratio
        self.logger = logging.getLogger("RiskManager")

    def calculate_levels(self, entry_price: float, position_type: str, stop_loss_pct: float = None) -> dict:
        sl_pct = (stop_loss_pct if stop_loss_pct is not None else self.default_risk_pct) / 100.0
        tp_pct = sl_pct * self.default_reward_risk_ratio

        if position_type.upper() == "BUY":
            stop_loss = round(entry_price * (1 - sl_pct), 4)
            take_profit = round(entry_price * (1 + tp_pct), 4)
        elif position_type.upper() == "SELL":
            stop_loss = round(entry_price * (1 + sl_pct), 4)
            take_profit = round(entry_price * (1 - tp_pct), 4)
        else:
            raise ValueError(f"Invalid position type: {position_type}")

        return {
            "entry_price": entry_price,
            "position_type": position_type.upper(),
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_percentage": sl_pct * 100,
            "reward_percentage": tp_pct * 100
        }

    def check_exit_signals(self, current_price: float, entry_price: float, stop_loss: float, take_profit: float, position_type: str) -> str:
        if position_type.upper() == "BUY":
            if current_price <= stop_loss:
                return "EXIT_STOP_LOSS"
            elif current_price >= take_profit:
                return "EXIT_TAKE_PROFIT"
        elif position_type.upper() == "SELL":
            if current_price >= stop_loss:
                return "EXIT_STOP_LOSS"
            elif current_price <= take_profit:
                return "EXIT_TAKE_PROFIT"
        return "HOLD"