from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class DatabaseConnection:
    def __init__(self, uri="mongodb://localhost:27017/"):
        self.client = MongoClient(uri)
        self.db = self.client.stock_analysis
        self.stocks = self.db.stocks
        self.analysis = self.db.analysis

    def get_stock_data(self, symbol: str):
        try:
            # Get latest stock data
            stock_data = self.stocks.find_one(
                {"symbol": symbol},
                {"_id": 0}
            )
            
            # Get latest analysis
            analysis_data = self.analysis.find_one(
                {"symbol": symbol},
                {"_id": 0}
            )
            
            if not stock_data:
                return None
                
            # Combine stock and analysis data
            combined_data = {
                "symbol": symbol,
                "market_data": stock_data.get("data", {}).get("market", {}),
                "historical_data": stock_data.get("data", {}).get("historical", {}),
                "news_sentiment": stock_data.get("data", {}).get("news_sentiment", {}),
                "company_info": stock_data.get("data", {}).get("company_info", {}),
                "fundamentals": stock_data.get("data", {}).get("fundamentals", {}),
                "analysis": analysis_data.get("analysis") if analysis_data else None,
                "timestamp": stock_data.get("timestamp")
            }
            
            return combined_data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    def get_available_symbols(self):
        try:
            return self.stocks.distinct("symbol")
        except Exception as e:
            print(f"Error fetching symbols: {e}")
            return []

    def search_symbols(self, query: str):
        try:
            # Case-insensitive search for symbols
            symbols = self.stocks.find(
                {"symbol": {"$regex": query.upper(), "$options": "i"}},
                {"symbol": 1, "_id": 0}
            )
            return [s["symbol"] for s in symbols]
        except Exception as e:
            print(f"Error searching symbols: {e}")
            return []

# Initialize database connection
db = DatabaseConnection()

@app.route('/api/stock/<symbol>')
def get_stock_data(symbol):
    """Get complete stock data for a symbol"""
    data = db.get_stock_data(symbol.upper())
    if data:
        return jsonify(data)
    return jsonify({"error": "Stock not found"}), 404

@app.route('/api/symbols')
def get_symbols():
    """Get all available stock symbols"""
    symbols = db.get_available_symbols()
    return jsonify(symbols)

@app.route('/api/search')
def search_stocks():
    """Search for stocks based on symbol"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    symbols = db.search_symbols(query)
    return jsonify(symbols)

@app.route('/api/default')
def get_default_stock():
    """Get default stock data (AAPL)"""
    data = db.get_stock_data('AAPL')
    if data:
        return jsonify(data)
    return jsonify({"error": "Default stock data not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=8000)