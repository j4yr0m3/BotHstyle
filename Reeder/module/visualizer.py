import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class PerformanceVisualizer:
    """
    Visualization engine for plotting strategy performance, cumulative returns,
    and portfolio drawdown over time.
    """
    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        try:
            plt.style.use(style)
        except Exception:
            plt.style.use("default")

    def plot_backtest_results(self, backtest_df: pd.DataFrame, title: str = "Backtest Performance Report", save_path: str = None):
        """
        Plots price action, portfolio value equity curve, and drawdown.
        """
        fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

        # Plot 1: Asset Price & Buy/Sell Signals
        axes[0].plot(backtest_df.index, backtest_df['Close'], label='Close Price', color='#2980b9', linewidth=1.5)
        if 'Signal' in backtest_df.columns:
            buy_signals = backtest_df[backtest_df['Signal'] == 1]
            sell_signals = backtest_df[backtest_df['Signal'] == -1]
            axes[0].scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', s=70, label='BUY Signal')
            axes[0].scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', s=70, label='SELL Signal')
        axes[0].set_title(title, fontsize=14, fontweight='bold')
        axes[0].set_ylabel("Price ($)")
        axes[0].legend(loc='upper left')

        # Plot 2: Portfolio Equity Curve
        if 'Portfolio_Value' in backtest_df.columns:
            axes[1].plot(backtest_df.index, backtest_df['Portfolio_Value'], label='Portfolio Value', color='#27ae60', linewidth=1.8)
            axes[1].set_ylabel("Portfolio ($)")
            axes[1].legend(loc='upper left')

        # Plot 3: Drawdown Chart
        if 'Portfolio_Value' in backtest_df.columns:
            cum_max = backtest_df['Portfolio_Value'].cummax()
            drawdown = (backtest_df['Portfolio_Value'] - cum_max) / cum_max * 100
            axes[2].fill_between(backtest_df.index, drawdown, 0, color='#e74c3c', alpha=0.4, label='Drawdown (%)')
            axes[2].set_ylabel("Drawdown (%)")
            axes[2].set_xlabel("Date")
            axes[2].legend(loc='lower left')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"Chart saved to {save_path}")
        
        plt.show()

if __name__ == "__main__":
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100)
    df = pd.DataFrame({
        'Close': 100 + np.random.randn(100).cumsum(),
        'Signal': np.random.choice([1, -1, 0], size=100, p=[0.2, 0.2, 0.6])
    }, index=dates)
    df['Strategy_Returns'] = df['Close'].pct_change() * df['Signal'].shift(1)
    df['Portfolio_Value'] = 10000 * (1 + df['Strategy_Returns'].fillna(0)).cumprod()

    viz = PerformanceVisualizer()
    viz.plot_backtest_results(df, title="Sample Strategy Performance")