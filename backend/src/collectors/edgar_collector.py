import requests
import pandas as pd
import time
from datetime import datetime
import os
from typing import Dict, List, Optional

class EDGARDataCollector:
    def __init__(self, user_agent: str):
        """
        Initialize SEC EDGAR data collector
        
        Parameters:
        user_agent (str): Email address for SEC API requests
        """
        self.base_url = "https://data.sec.gov"
        self.headers = {
            'User-Agent': f'{user_agent}',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov',  # Changed from www.sec.gov
            'Accept': 'application/json'
        }
        
        # Common CIK numbers for well-known companies
        self.common_ciks = {
            'AAPL': '0000320193',
            'MSFT': '0000789019',
            'GOOGL': '0001652044',
            'AMZN': '0001018724',
            'META': '0001326801',
            'NVDA': '0001045810',
            'TSLA': '0001318605',
            'JPM': '0000019617',
            'V': '0001403161',
            'JNJ': '0000200406'
        }

    def get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """Get CIK number for a ticker symbol"""
        try:
            # First check our common CIKs dictionary
            if ticker.upper() in self.common_ciks:
                return self.common_ciks[ticker.upper()]

            # If not in common CIKs, try SEC API
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                companies = response.json()
                for _, company in companies.items():
                    if company['ticker'] == ticker.upper():
                        return str(company['cik_str']).zfill(10)
            
            print(f"Could not find CIK for ticker {ticker}")
            return None
            
        except Exception as e:
            print(f"Error getting CIK for {ticker}: {e}")
            return None

    def get_company_facts(self, cik: str) -> Optional[Dict]:
        """Get company facts from SEC"""
        try:
            time.sleep(0.1)  # Respect SEC rate limits
            # Update the URL format
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            print(f"Fetching data from: {url}")  # Debug print
            
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting company facts: {e}")
            return None

    def extract_financial_data(self, facts_data: Dict) -> Dict:
        """Extract key financial metrics from company facts"""
        financial_data = []
        
        if not facts_data or 'facts' not in facts_data or 'us-gaap' not in facts_data['facts']:
            return financial_data

        # Key metrics to extract
        metrics_to_extract = [
            'Assets',
            'Liabilities',
            'StockholdersEquity',
            'Revenues',
            'NetIncomeLoss',
            'CashAndCashEquivalentsAtCarryingValue',
            'OperatingIncomeLoss',
            'GrossProfit',
            'ResearchAndDevelopmentExpense',
            'SellingGeneralAndAdministrativeExpense',
            'OperatingExpenses',
            'CurrentAssets',
            'CurrentLiabilities'
        ]

        us_gaap_data = facts_data['facts']['us-gaap']
        
        for metric in metrics_to_extract:
            if metric in us_gaap_data:
                metric_data = us_gaap_data[metric]
                
                # Get the most recent annual report data (10-K)
                if 'units' in metric_data and 'USD' in metric_data['units']:
                    for entry in metric_data['units']['USD']:
                        if entry.get('form') == '10-K':
                            financial_data.append({
                                'metric': metric,
                                'value': entry['val'],
                                'end_date': entry['end'],
                                'filed_date': entry.get('filed', ''),
                                'form': '10-K'
                            })

        return financial_data

def collect_and_save_edgar_data(symbols: List[str], output_dir: str = 'stock_data'):
    """
    Collect and save SEC EDGAR data for multiple symbols
    """
    # Initialize EDGAR collector
    collector = EDGARDataCollector(user_agent='your.email@example.com')  # Replace with your email
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Initialize list to store all financial data
    all_financial_data = []
    
    print("Starting SEC EDGAR data collection...")
    
    for symbol in symbols:
        print(f"\nProcessing {symbol}...")
        
        # Get CIK
        cik = collector.get_cik_from_ticker(symbol)
        if not cik:
            continue
            
        print(f"Found CIK: {cik}")
        
        # Get company facts
        facts_data = collector.get_company_facts(cik)
        if facts_data:
            # Extract and process financial data
            financial_data = collector.extract_financial_data(facts_data)
            
            # Add symbol and CIK to each record
            for record in financial_data:
                record['symbol'] = symbol
                record['cik'] = cik
                all_financial_data.append(record)
            
            print(f"Collected {len(financial_data)} financial records")
        
        time.sleep(0.1)  # Respect SEC rate limits
    
    if all_financial_data:
        # Create DataFrame and save to CSV
        df = pd.DataFrame(all_financial_data)
        
        # Organize columns
        columns_order = ['symbol', 'cik', 'metric', 'value', 'end_date', 
                        'filed_date', 'form']
        df = df[columns_order]
        
        # Save to CSV
        filename = f'{output_dir}/edgar_financial_data_{timestamp}.csv'
        df.to_csv(filename, index=False)
        print(f"\nSaved financial data to {filename}")
        
        # Create pivot table for easier analysis
        pivot_df = df.pivot_table(
            index=['symbol', 'end_date'],
            columns='metric',
            values='value',
            aggfunc='first'
        ).reset_index()
        
        # Save pivot table to CSV
        pivot_filename = f'{output_dir}/edgar_financial_data_pivot_{timestamp}.csv'
        pivot_df.to_csv(pivot_filename, index=False)
        print(f"Saved pivot table to {pivot_filename}")
        
        return df, pivot_df
    else:
        print("No financial data collected")
        return None, None

# Example usage
if __name__ == "__main__":
    # List of stock symbols to collect data for
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']
    
    # Collect and save data
    df, pivot_df = collect_and_save_edgar_data(symbols)
    
    if df is not None:
        print("\nData collection summary:")
        print(f"Total records collected: {len(df)}")
        print("\nSample of collected data:")
        print(df.head())
        
        print("\nSample of pivot table:")
        print(pivot_df.head())