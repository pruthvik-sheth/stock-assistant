# stock_collector.py

import requests
import pandas as pd
import time
from datetime import datetime
import os
import json
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class UnifiedStockCollector:
    def __init__(self, alpha_vantage_key: str, sec_user_agent: str):
        """Initialize the unified stock data collector"""
        self.alpha_vantage_key = alpha_vantage_key
        self.alpha_vantage_base_url = 'https://www.alphavantage.co/query'
        
        # SEC EDGAR settings
        self.sec_base_url = "https://data.sec.gov"
        self.sec_headers = {
            'User-Agent': sec_user_agent,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov',
            'Accept': 'application/json'
        }
        
        # Common CIK numbers
        self.common_ciks = {
            'AAPL': '0000320193',
            'MSFT': '0000789019',
            'GOOGL': '0001652044',
            'AMZN': '0001018724',
            'META': '0001326801'
        }

    # EDGAR Methods
    def get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """Get CIK number for a ticker symbol"""
        try:
            if ticker.upper() in self.common_ciks:
                return self.common_ciks[ticker.upper()]

            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.sec_headers)
            
            if response.status_code == 200:
                companies = response.json()
                for _, company in companies.items():
                    if company['ticker'] == ticker.upper():
                        return str(company['cik_str']).zfill(10)
            return None
            
        except Exception as e:
            print(f"Error getting CIK for {ticker}: {e}")
            return None

    def get_edgar_data(self, symbol: str) -> Optional[Dict]:
        """Get company financial data from SEC EDGAR"""
        cik = self.get_cik_from_ticker(symbol)
        if not cik:
            return None

        try:
            time.sleep(0.1)  # Respect SEC rate limits
            url = f"{self.sec_base_url}/api/xbrl/companyfacts/CIK{cik}.json"
            response = requests.get(url, headers=self.sec_headers)
            
            if response.status_code == 200:
                return self.process_edgar_data(response.json())
            return None
            
        except Exception as e:
            print(f"Error getting EDGAR data for {symbol}: {e}")
            return None

    # Market Data Methods
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get current market data"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.alpha_vantage_key
        }
        
        try:
            response = requests.get(self.alpha_vantage_base_url, params=params)
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': symbol,
                    'price': float(quote.get('05. price', 0)),
                    'volume': int(quote.get('06. volume', 0)),
                    'daily_change': float(quote.get('09. change', 0)),
                    'daily_change_percent': float(quote.get('10. change percent', '0').strip('%'))
                }
            return None
            
        except Exception as e:
            print(f"Error getting market data for {symbol}: {e}")
            return None

    def get_historical_data(self, symbol: str, output_size: str = 'compact') -> Optional[List[Dict]]:
        """Get historical daily price data"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': output_size,
            'apikey': self.alpha_vantage_key
        }
        
        try:
            response = requests.get(self.alpha_vantage_base_url, params=params)
            data = response.json()
            
            if 'Time Series (Daily)' in data:
                historical_data = []
                time_series = data['Time Series (Daily)']
                
                for date, values in time_series.items():
                    historical_data.append({
                        'date': date,
                        'open': float(values['1. open']),
                        'high': float(values['2. high']),
                        'low': float(values['3. low']),
                        'close': float(values['4. close']),
                        'volume': int(values['5. volume'])
                    })
                return historical_data
            return None
            
        except Exception as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return None

    # News Methods
    def get_news_sentiment(self, symbol: str) -> Optional[List[Dict]]:
        """Get news and sentiment data"""
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'limit': 10,
            'apikey': self.alpha_vantage_key
        }
        
        try:
            response = requests.get(self.alpha_vantage_base_url, params=params)
            data = response.json()
            
            if 'feed' in data:
                return [{
                    'title': article.get('title'),
                    'time_published': article.get('time_published'),
                    'sentiment_score': article.get('overall_sentiment_score'),
                    'sentiment_label': article.get('overall_sentiment_label')
                } for article in data['feed']]
            return None
            
        except Exception as e:
            print(f"Error getting news data for {symbol}: {e}")
            return None

    def collect_all_data(self, symbol: str) -> Dict:
        """Collect all available data for a symbol"""
        data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'market_data': self.get_market_data(symbol),
            'historical_data': self.get_historical_data(symbol),
            'news_sentiment': self.get_news_sentiment(symbol),
            'edgar_data': self.get_edgar_data(symbol)
        }
        return data

    def collect_and_save_data(self, symbols: List[str], output_dir: str = 'stock_data'):
        """Collect and save data for multiple symbols"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        all_data = []
        for symbol in symbols:
            print(f"Collecting data for {symbol}...")
            data = self.collect_all_data(symbol)
            all_data.append(data)
            time.sleep(12)  # Respect API rate limits
        
        # Save complete dataset
        filename = f'{output_dir}/stock_data_{timestamp}.json'
        with open(filename, 'w') as f:
            json.dump(all_data, f, indent=4)
        
        print(f"\nSaved complete dataset to {filename}")
        return all_data

def main():
    collector = UnifiedStockCollector(
        alpha_vantage_key=os.getenv('ALPHA_VANTAGE_API_KEY'),
        sec_user_agent='your.email@example.com'
    )
    
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    collector.collect_and_save_data(symbols)

if __name__ == "__main__":
    main()