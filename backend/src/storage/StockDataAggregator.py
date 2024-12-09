import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json

class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for numpy data types"""
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                          np.int16, np.int32, np.int64, np.uint8,
                          np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class StockDataAggregator:
    def __init__(self, data_dir: str = 'stock_data'):
        """
        Initialize the data aggregator
        
        Parameters:
        data_dir (str): Directory containing the CSV files
        """
        self.data_dir = Path(data_dir)
        
    def get_latest_file(self, prefix: str) -> Optional[Path]:
        """Get the most recent file with given prefix"""
        files = list(self.data_dir.glob(f'{prefix}_*.csv'))
        if not files:
            return None
        return max(files, key=os.path.getctime)
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all available data files"""
        data_files = {
            'market': self.get_latest_file('market_data'),
            'historical': self.get_latest_file('historical_data'),
            'news': self.get_latest_file('news_data'),
            'company': self.get_latest_file('company_data'),
            'edgar': self.get_latest_file('edgar_financial_data_pivot')
        }
        
        data = {}
        for key, file_path in data_files.items():
            if file_path and file_path.exists():
                data[key] = pd.read_csv(file_path)
                print(f"Loaded {key} data from {file_path.name}")
            else:
                print(f"No {key} data file found")
        
        return data
    
    def aggregate_stock_data(self, symbol: str) -> Dict:
        """
        Aggregate all available data for a specific stock
        """
        data = self.load_all_data()
        
        aggregated_data = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'data_sources': {},
            'data': {}
        }
        
        try:
            # 1. Market Data
            if 'market' in data:
                market_df = data['market']
                symbol_market = market_df[market_df['symbol'] == symbol].iloc[0] if not market_df[market_df['symbol'] == symbol].empty else None
                
                if symbol_market is not None:
                    aggregated_data['data']['market'] = {
                        'current_price': float(symbol_market['price']),
                        'daily_change': float(symbol_market['daily_change']),
                        'daily_change_percent': float(symbol_market['daily_change_percent']),
                        'volume': int(symbol_market['volume']),
                        'trading_day': str(symbol_market['latest_trading_day'])
                    }
                    aggregated_data['data_sources']['market'] = True
            
            # 2. Historical Data
            if 'historical' in data:
                hist_df = data['historical']
                symbol_hist = hist_df[hist_df['symbol'] == symbol]
                
                if not symbol_hist.empty:
                    aggregated_data['data']['historical'] = {
                        'dates': symbol_hist['date'].tolist(),
                        'prices': [float(x) for x in symbol_hist['close'].tolist()],
                        'volumes': [int(x) for x in symbol_hist['volume'].tolist()]
                    }
                    aggregated_data['data_sources']['historical'] = True
            
            # 3. News Sentiment
            if 'news' in data:
                news_df = data['news']
                symbol_news = news_df[news_df['symbol'] == symbol]
                
                if not symbol_news.empty:
                    aggregated_data['data']['news_sentiment'] = {
                        'articles': [
                            {k: float(v) if isinstance(v, np.number) else str(v) 
                             for k, v in article.items()}
                            for article in symbol_news.to_dict('records')
                        ],
                        'aggregate_sentiment': {
                            'average_score': float(symbol_news['overall_sentiment_score'].mean()),
                            'article_count': int(len(symbol_news))
                        }
                    }
                    aggregated_data['data_sources']['news_sentiment'] = True
            
            # 4. Company Data
            if 'company' in data:
                company_df = data['company']
                symbol_company = company_df[company_df['symbol'] == symbol].iloc[0] if not company_df[company_df['symbol'] == symbol].empty else None
                
                if symbol_company is not None:
                    aggregated_data['data']['company_info'] = {
                        'name': str(symbol_company['name']),
                        'sector': str(symbol_company['sector']),
                        'industry': str(symbol_company['industry']),
                        'market_cap': float(symbol_company['market_cap']),
                        'pe_ratio': float(symbol_company['pe_ratio']),
                        'dividend_yield': float(symbol_company['dividend_yield'])
                    }
                    aggregated_data['data_sources']['company_info'] = True
            
            # 5. SEC EDGAR Data
            if 'edgar' in data:
                edgar_df = data['edgar']
                symbol_edgar = edgar_df[edgar_df['symbol'] == symbol]
                
                if not symbol_edgar.empty:
                    # Get the most recent data
                    latest_data = symbol_edgar.sort_values('end_date', ascending=False).iloc[0]
                    
                    # Convert numeric values to native Python types
                    metrics = {
                        k: float(v) if isinstance(v, np.number) else str(v)
                        for k, v in latest_data.drop(['symbol', 'end_date']).to_dict().items()
                    }
                    
                    aggregated_data['data']['fundamentals'] = {
                        'latest_filing': {
                            'date': str(latest_data['end_date']),
                            'metrics': metrics
                        }
                    }
                    
                    # Add historical data if available
                    if len(symbol_edgar) > 1:
                        historical_filings = []
                        for _, row in symbol_edgar.iterrows():
                            filing_data = {
                                'date': str(row['end_date']),
                                'metrics': {
                                    k: float(v) if isinstance(v, np.number) else str(v)
                                    for k, v in row.drop(['symbol', 'end_date']).to_dict().items()
                                }
                            }
                            historical_filings.append(filing_data)
                        aggregated_data['data']['fundamentals']['historical_filings'] = historical_filings
                    
                    aggregated_data['data_sources']['fundamentals'] = True
            
            return aggregated_data
        
        except Exception as e:
            print(f"Error aggregating data for {symbol}: {e}")
            return aggregated_data

    def save_aggregated_data(self, symbols: List[str], output_dir: str = 'aggregated_data'):
        """
        Save aggregated data for multiple symbols
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        all_aggregated_data = []
        
        for symbol in symbols:
            print(f"\nAggregating data for {symbol}...")
            aggregated_data = self.aggregate_stock_data(symbol)
            all_aggregated_data.append(aggregated_data)
        
        # Save as JSON using custom encoder
        json_file = Path(output_dir) / f'aggregated_stock_data_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(all_aggregated_data, f, indent=4, cls=NumpyEncoder)
        print(f"\nSaved aggregated data to {json_file}")
        
        return all_aggregated_data

# Example usage
if __name__ == "__main__":
    # Initialize aggregator
    aggregator = StockDataAggregator()
    
    # List of symbols to aggregate
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    # Aggregate and save data
    aggregated_data = aggregator.save_aggregated_data(symbols)
    
    # Print summary
    print("\nAggregation Summary:")
    for data in aggregated_data:
        symbol = data['symbol']
        sources = data['data_sources']
        print(f"\n{symbol}:")
        print("Available data sources:")
        for source, available in sources.items():
            print(f"  - {source}: {'Available' if available else 'Not Available'}")