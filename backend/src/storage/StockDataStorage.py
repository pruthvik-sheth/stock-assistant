from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
import json

class StockDataStorage:
    def __init__(self, connection_uri: str = "mongodb://localhost:27017/", 
                 db_name: str = "stock_analysis"):
        """
        Initialize MongoDB connection
        
        Parameters:
        connection_uri (str): MongoDB connection URI
        db_name (str): Name of the database
        """
        self.client = MongoClient(connection_uri)
        self.db = self.client[db_name]
        
        # Collections
        self.stocks = self.db.stocks
        self.analysis = self.db.analysis
        
        # Create indexes for better query performance
        self.stocks.create_index([("symbol", 1), ("timestamp", -1)])
        self.analysis.create_index([("symbol", 1), ("timestamp", -1)])

    def store_stock_data(self, data: List[Dict]) -> None:
        """
        Store aggregated stock data
        
        Parameters:
        data (List[Dict]): List of aggregated stock data dictionaries
        """
        timestamp = datetime.now()
        
        for stock_data in data:
            symbol = stock_data['symbol']
            
            # Add timestamp if not present
            if 'timestamp' not in stock_data:
                stock_data['timestamp'] = timestamp
            
            try:
                # Store data
                self.stocks.update_one(
                    {"symbol": symbol},
                    {"$set": stock_data},
                    upsert=True
                )
                print(f"Stored stock data for {symbol}")
                
            except Exception as e:
                print(f"Error storing stock data for {symbol}: {e}")

    def store_analysis_data(self, analysis_data: List[Dict]) -> None:
        """
        Store analysis results
        
        Parameters:
        analysis_data (List[Dict]): List of analysis results
        """
        timestamp = datetime.now()
        
        for analysis in analysis_data:
            symbol = analysis['symbol']
            
            # Add timestamp if not present
            if 'timestamp' not in analysis:
                analysis['timestamp'] = timestamp
            
            try:
                # Store in analysis collection
                self.analysis.update_one(
                    {"symbol": symbol},
                    {"$set": analysis},
                    upsert=True
                )
                print(f"Stored analysis for {symbol}")
                
            except Exception as e:
                print(f"Error storing analysis for {symbol}: {e}")

    def get_stock_data(self, symbol: str, 
                      start_date: datetime = None, 
                      end_date: datetime = None,
                      limit: int = None) -> List[Dict]:
        """
        Get stock data with optional date range and limit
        """
        query = {"symbol": symbol}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.stocks.find(query, {"_id": 0}).sort("timestamp", -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)

    def get_latest_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get most recent data for a specific stock"""
        data = self.get_stock_data(symbol, limit=1)
        return data[0] if data else None

    def get_analysis_data(self, symbol: str,
                         start_date: datetime = None,
                         end_date: datetime = None,
                         limit: int = None) -> List[Dict]:
        """
        Get analysis data with optional date range and limit
        """
        query = {"symbol": symbol}
        
        if start_date or end_date:
            query["timestamp"] = {}
            if start_date:
                query["timestamp"]["$gte"] = start_date
            if end_date:
                query["timestamp"]["$lte"] = end_date
        
        cursor = self.analysis.find(query, {"_id": 0}).sort("timestamp", -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)

    def get_latest_analysis(self, symbol: str) -> Optional[Dict]:
        """Get most recent analysis for a specific stock"""
        data = self.get_analysis_data(symbol, limit=1)
        return data[0] if data else None

    def get_all_symbols(self) -> List[str]:
        """Get list of all available stock symbols"""
        return self.stocks.distinct("symbol")

    def delete_old_data(self, days: int = 30) -> None:
        """
        Delete data older than specified days
        
        Parameters:
        days (int): Number of days of data to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            # Delete old stock data
            result = self.stocks.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            print(f"Deleted {result.deleted_count} old stock records")
            
            # Delete old analysis
            result = self.analysis.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            print(f"Deleted {result.deleted_count} old analysis records")
            
        except Exception as e:
            print(f"Error deleting old data: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize storage
    db = StockDataStorage()
    
    # Example: Store stock data
    with open("aggregated_data/aggregated_stock_data_latest.json", "r") as f:
        stock_data = json.load(f)
    db.store_stock_data(stock_data)
    
    # Example: Store analysis data
    with open("analysis_results/stock_analysis_latest.json", "r") as f:
        analysis_data = json.load(f)
    db.store_analysis_data(analysis_data)
    
    # Example: Retrieve data
    symbols = db.get_all_symbols()
    print("\nAvailable symbols:", symbols)
    
    for symbol in symbols:
        # Get latest stock data
        stock_data = db.get_latest_stock_data(symbol)
        if stock_data:
            print(f"\nLatest stock data for {symbol}:")
            print(f"Price: ${stock_data['data']['market']['current_price']}")
        
        # Get latest analysis
        analysis = db.get_latest_analysis(symbol)
        if analysis:
            print(f"\nLatest analysis for {symbol}:")
            print(analysis['analysis'])