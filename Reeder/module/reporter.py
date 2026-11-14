import os
import json
import logging
from datetime import datetime
import pandas as pd

class ReportingManager:
    """
    Automated reporting engine that generates formatted performance summaries 
    in text, HTML, and JSON formats for execution and backtesting metrics.
    """
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.logger = logging.getLogger("ReportingManager")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_performance_summary(self, metrics: dict, strategy_name: str = "Default Strategy") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_text = f"""
==================================================
           TRADING PERFORMANCE SUMMARY REPORT
==================================================
Timestamp:        {timestamp}
Strategy:         {strategy_name}
--------------------------------------------------
Initial Capital:  ${metrics.get('initial_capital', 0.0):,.2f}
Final Value:      ${metrics.get('final_value', 0.0):,.2f}
Total Return:     {metrics.get('total_return_pct', 0.0):+.2f}%
Total Trades:     {metrics.get('total_trades', 0)}
Win Rate:         {metrics.get('win_rate_pct', 0.0):.2f}%
Max Drawdown:     {metrics.get('max_drawdown_pct', 0.0):.2f}%
Sharpe Ratio:     {metrics.get('sharpe_ratio', 0.0):.2f}
==================================================
        """
        return report_text.strip()

    def export_html_report(self, metrics: dict, strategy_name: str = "Default Strategy", filename: str = None) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Trading Performance Report - {strategy_name}</title>
    <style>
        body {{{{ font-family: Arial, sans-serif; margin: 30px; background-color: #f4f6f9; color: #333; }}}} 
        .card {{{{ background: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }}}} 
        h2 {{{{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}}} 
        .metric {{{{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}}} 
        .metric-name {{{{ font-weight: bold; color: #555; }}}} 
        .metric-val {{{{ font-family: monospace; font-size: 1.1em; }}}} 
        .positive {{{{ color: #27ae60; font-weight: bold; }}}} 
        .negative {{{{ color: #e74c3c; font-weight: bold; }}}} 
    </style>
</head>
<body>
    <div class="card">
        <h2>Performance Report: {strategy_name}</h2>
        <p><em>Generated on: {timestamp}</em></p>
        <div class="metric"><span class="metric-name">Initial Capital</span><span class="metric-val">${metrics.get('initial_capital', 0.0):,.2f}</span></div>
        <div class="metric"><span class="metric-name">Final Portfolio Value</span><span class="metric-val">${metrics.get('final_value', 0.0):,.2f}</span></div>
        <div class="metric"><span class="metric-name">Total Return</span><span class="metric-val {'positive' if metrics.get('total_return_pct', 0) >= 0 else 'negative'}">{metrics.get('total_return_pct', 0.0):+.2f}%</span></div>
        <div class="metric"><span class="metric-name">Total Trades</span><span class="metric-val">{metrics.get('total_trades', 0)}</span></div>
        <div class="metric"><span class="metric-name">Win Rate</span><span class="metric-val">{metrics.get('win_rate_pct', 0.0):.2f}%</span></div>
        <div class="metric"><span class="metric-name">Max Drawdown</span><span class="metric-val negative">{metrics.get('max_drawdown_pct', 0.0):.2f}%</span></div>
        <div class="metric"><span class="metric-name">Sharpe Ratio</span><span class="metric-val">{metrics.get('sharpe_ratio', 0.0):.2f}</span></div>
    </div>
</body>
</html>
        """
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        self.logger.info(f"HTML report exported to {filepath}")
        return filepath

    def export_json_report(self, metrics: dict, strategy_name: str = "Default Strategy", filename: str = None) -> str:
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        payload = {
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy_name,
            "metrics": metrics
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        self.logger.info(f"JSON report exported to {filepath}")
        return filepath