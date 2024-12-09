import os
import pandas as pd
import time
from datetime import datetime
import json
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

# Load API keys
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'

def collect_market_data(symbol: str) -> Dict:
    """Collect market data for a symbol"""
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            return {
                'symbol': symbol,
                'price': float(quote.get('05. price', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'daily_change': float(quote.get('09. change', 0)),
                'daily_change_percent': float(quote.get('10. change percent', '0').strip('%')),
                'latest_trading_day': quote.get('07. latest trading day', '')
            }
    except Exception as e:
        print(f"Error collecting market data for {symbol}: {e}")
    return None

def collect_news_sentiment(symbol: str) -> Dict:
    """Collect news and sentiment data"""
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': symbol,
        'limit': 10,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'feed' in data:
            articles = []
            for article in data['feed']:
                articles.append({
                    'symbol': symbol,
                    'title': article.get('title'),
                    'time_published': article.get('time_published'),
                    'summary': article.get('summary'),
                    'source': article.get('source'),
                    'overall_sentiment_score': article.get('overall_sentiment_score'),
                    'overall_sentiment_label': article.get('overall_sentiment_label'),
                    'url': article.get('url')
                })
            return articles
    except Exception as e:
        print(f"Error collecting news data for {symbol}: {e}")
    return None

def collect_company_overview(symbol: str) -> Dict:
    """Collect company overview data"""
    params = {
        'function': 'OVERVIEW',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'Symbol' in data:
            return {
                'symbol': symbol,
                'name': data.get('Name'),
                'sector': data.get('Sector'),
                'industry': data.get('Industry'),
                'market_cap': float(data.get('MarketCapitalization', 0)),
                'pe_ratio': float(data.get('PERatio', 0)),
                'dividend_yield': float(data.get('DividendYield', 0)),
                'profit_margin': float(data.get('ProfitMargin', 0)),
                'beta': float(data.get('Beta', 0)),
                '52_week_high': float(data.get('52WeekHigh', 0)),
                '52_week_low': float(data.get('52WeekLow', 0))
            }
    except Exception as e:
        print(f"Error collecting company overview for {symbol}: {e}")
    return None

def collect_and_save_data(symbols: List[str], output_dir: str = 'stock_data'):
    """Collect data for all symbols and save to CSV files"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Initialize lists to store data
    market_data_list = []
    news_data_list = []
    company_data_list = []
    
    for symbol in symbols:
        print(f"\nCollecting data for {symbol}...")
        
        # Collect market data
        market_data = collect_market_data(symbol)
        if market_data:
            market_data['timestamp'] = timestamp
            market_data_list.append(market_data)
        
        time.sleep(12)  # Respect API rate limit
        
        # Collect news data
        news_data = collect_news_sentiment(symbol)
        if news_data:
            for article in news_data:
                article['timestamp'] = timestamp
            news_data_list.extend(news_data)
        
        time.sleep(12)  # Respect API rate limit
        
        # Collect company overview
        company_data = collect_company_overview(symbol)
        if company_data:
            company_data['timestamp'] = timestamp
            company_data_list.append(company_data)
        
        time.sleep(12)  # Respect API rate limit
    
    # Save to CSV files
    if market_data_list:
        market_df = pd.DataFrame(market_data_list)
        market_df.to_csv(f'{output_dir}/market_data_{timestamp}.csv', index=False)
        print(f"\nSaved market data to market_data_{timestamp}.csv")
    
    if news_data_list:
        news_df = pd.DataFrame(news_data_list)
        news_df.to_csv(f'{output_dir}/news_data_{timestamp}.csv', index=False)
        print(f"Saved news data to news_data_{timestamp}.csv")
    
    if company_data_list:
        company_df = pd.DataFrame(company_data_list)
        company_df.to_csv(f'{output_dir}/company_data_{timestamp}.csv', index=False)
        print(f"Saved company data to company_data_{timestamp}.csv")

# Example usage
if __name__ == "__main__":
    # List of stock symbols to collect data for
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    print("Starting data collection...")
    collect_and_save_data(symbols)
    print("\nData collection complete!")