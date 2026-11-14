import numpy as np
import pandas as pd
import logging

class PortfolioManager:
    """
    Advanced portfolio management engine handling risk allocation, dynamic position sizing,
    Kelly Criterion calculation, and maximum exposure controls across multi-asset portfolios.
    """
    def __init__(self, total_capital: float = 100000.0, max_portfolio_risk_pct: float = 5.0, max_asset_allocation_pct: float = 25.0):
        self.total_capital = total_capital
        self.max_portfolio_risk_pct = max_portfolio_risk_pct
        self.max_asset_allocation_pct = max_asset_allocation_pct
        self.logger = logging.getLogger("PortfolioManager")

    def calculate_position_size(self, entry_price: float, stop_loss_price: float, risk_per_trade_pct: float = 1.0) -> dict:
        """
        Calculates position size based on fixed account percentage risk model.
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            raise ValueError("Entry price and Stop Loss price must be positive.")

        risk_amount = self.total_capital * (risk_per_trade_pct / 100.0)
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share == 0:
            raise ValueError("Entry price cannot equal Stop Loss price.")

        units = risk_amount / risk_per_share
        position_value = units * entry_price

        # Cap at maximum asset allocation limit
        max_allowed_value = self.total_capital * (self.max_asset_allocation_pct / 100.0)
        if position_value > max_allowed_value:
            position_value = max_allowed_value
            units = position_value / entry_price
            self.logger.warning(f"Position size capped by max allocation limit ({self.max_asset_allocation_pct}%).")

        return {
            "entry_price": entry_price,
            "stop_loss": stop_loss_price,
            "risk_amount_usd": round(risk_amount, 2),
            "units": round(units, 4),
            "position_value_usd": round(position_value, 2),
            "portfolio_weight_pct": round((position_value / self.total_capital) * 100, 2)
        }

    def calculate_kelly_position_size(self, win_rate: float, win_loss_ratio: float, fraction: float = 0.5) -> float:
        """
        Calculates optimal position sizing using fractional Kelly Criterion.
        win_rate: Decimal float (0.0 to 1.0)
        win_loss_ratio: Average Win / Average Loss
        fraction: Kelly fraction (default 0.5 for Half-Kelly)
        """
        if win_loss_ratio <= 0:
            return 0.0
        p = win_rate
        q = 1.0 - p
        b = win_loss_ratio
        kelly_f = (b * p - q) / b
        
        # Apply fractional multiplier and clamp non-negative
        optimal_allocation = max(0.0, kelly_f * fraction)
        optimal_allocation = min(optimal_allocation, self.max_asset_allocation_pct / 100.0)
        return round(optimal_allocation * 100, 2)

    def allocate_multi_asset_risk(self, assets: list, target_weights: dict = None) -> dict:
        """
        Allocates total capital across multiple active market assets (Equal Weight or Target Weight).
        """
        num_assets = len(assets)
        if num_assets == 0:
            return {}

        allocations = {}
        if target_weights:
            weight_sum = sum(target_weights.values())
            normalized_weights = {k: v / weight_sum for k, v in target_weights.items()}
            for asset in assets:
                weight = normalized_weights.get(asset, 0.0)
                allocations[asset] = {
                    "weight_pct": round(weight * 100, 2),
                    "capital_allocated": round(self.total_capital * weight, 2)
                }
        else:
            equal_weight = 1.0 / num_assets
            for asset in assets:
                allocations[asset] = {
                    "weight_pct": round(equal_weight * 100, 2),
                    "capital_allocated": round(self.total_capital * equal_weight, 2)
                }

        return allocations

if __name__ == "__main__":
    pm = PortfolioManager(total_capital=50000.0)
    pos = pm.calculate_position_size(entry_price=150.0, stop_loss_price=145.0, risk_per_trade_pct=1.0)
    print("Fixed Risk Position Sizing:", pos)

    kelly_pct = pm.calculate_kelly_position_size(win_rate=0.55, win_loss_ratio=1.8, fraction=0.5)
    print(f"Optimal Half-Kelly Allocation: {kelly_pct}%")

    allocation = pm.allocate_multi_asset_risk(["Forex", "Gold", "Crypto", "Stock"])
    print("Multi-Asset Allocations:", allocation)