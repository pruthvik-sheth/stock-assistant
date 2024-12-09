import os
import pandas as pd
import time
from datetime import datetime
import requests
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'

def collect_historical_data(symbol: str, output_size='full') -> Dict:
    """
    Collect historical daily stock data
    
    Parameters:
    symbol (str): Stock symbol
    output_size (str): 'compact' (latest 100 data points) or 'full' (20+ years of data)
    """
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': output_size,
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if 'Time Series (Daily)' in data:
            historical_data = []
            time_series = data['Time Series (Daily)']
            
            for date, values in time_series.items():
                historical_data.append({
                    'symbol': symbol,
                    'date': date,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            
            return historical_data
    except Exception as e:
        print(f"Error collecting historical data for {symbol}: {e}")
    return None

def collect_intraday_data(symbol: str) -> Dict:
    """Collect intraday data (1min intervals for last trading day)"""
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': symbol,
        'interval': '1min',
        'outputsize': 'full',
        'apikey': ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        time_series_key = 'Time Series (1min)'
        if time_series_key in data:
            intraday_data = []
            for timestamp, values in data[time_series_key].items():
                intraday_data.append({
                    'symbol': symbol,
                    'timestamp': timestamp,
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            return intraday_data
    except Exception as e:
        print(f"Error collecting intraday data for {symbol}: {e}")
    return None

# Include previous functions here (collect_market_data, collect_news_sentiment, collect_company_overview)
# ... (previous code remains the same)

def collect_and_save_data(symbols: List[str], output_dir: str = 'stock_data'):
    """Collect all data including historical and intraday"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Initialize data lists (including previous ones)
    historical_data_list = []
    intraday_data_list = []
    
    for symbol in symbols:
        print(f"\nCollecting data for {symbol}...")
        
        # Collect historical data
        print(f"Collecting historical data...")
        historical_data = collect_historical_data(symbol)
        if historical_data:
            historical_data_list.extend(historical_data)
        
        time.sleep(12)  # API rate limit
        
        # Collect intraday data
        print(f"Collecting intraday data...")
        intraday_data = collect_intraday_data(symbol)
        if intraday_data:
            intraday_data_list.extend(intraday_data)
        
        time.sleep(12)
        
        # Collect other data (market, news, company) as before
        # ... (previous collection code)
    
    # Save historical data
    if historical_data_list:
        historical_df = pd.DataFrame(historical_data_list)
        historical_df.to_csv(f'{output_dir}/historical_data_{timestamp}.csv', index=False)
        print(f"\nSaved historical data to historical_data_{timestamp}.csv")
    
    # Save intraday data
    if intraday_data_list:
        intraday_df = pd.DataFrame(intraday_data_list)
        intraday_df.to_csv(f'{output_dir}/intraday_data_{timestamp}.csv', index=False)
        print(f"Saved intraday data to intraday_data_{timestamp}.csv")
    
    # Save other data as before
    # ... (previous saving code)

# Example usage
if __name__ == "__main__":
    # Test symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    print("Starting comprehensive data collection...")
    collect_and_save_data(symbols)
    print("\nData collection complete!")