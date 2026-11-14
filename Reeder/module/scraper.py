import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime

class WebScraper:
    """
    Web scraping tool for fetching market summaries, financial headlines, 
    and real-time market data snippets from online sources.
    """
    def __init__(self, headers: dict = None):
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        self.logger = logging.getLogger("WebScraper")

    def fetch_page(self, url: str) -> str:
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Error fetching URL {url}: {e}")
            return ""

    def scrape_headlines(self, url: str, selector: str = "h3") -> list:
        html = self.fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        headlines = []
        for element in soup.select(selector):
            text = element.get_text(strip=True)
            if text and text not in headlines:
                headlines.append(text)
        
        self.logger.info(f"Extracted {len(headlines)} headlines from {url}")
        return headlines

    def parse_market_table(self, url: str, table_selector: str = "table") -> pd.DataFrame:
        html = self.fetch_page(url)
        if not html:
            return pd.DataFrame()

        try:
            dfs = pd.read_html(html)
            if dfs:
                self.logger.info(f"Parsed market table successfully from {url}")
                return dfs[0]
        except Exception as e:
            self.logger.error(f"Failed to parse table: {e}")
        
        return pd.DataFrame()

if __name__ == "__main__":
    scraper = WebScraper()
    headlines = scraper.scrape_headlines("https://news.ycombinator.com", selector=".titleline > a")
    print(f"Top scraped items ({len(headlines)}):", headlines[:5])