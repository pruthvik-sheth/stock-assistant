# tests/test_analysis.py
import pytest
from datetime import datetime
from src.analysis.llm_analyzer import StockAnalysisLLM

@pytest.fixture
def sample_stock_data():
    return {
        "symbol": "AAPL",
        "data": {
            "market": {
                "current_price": 175.50,
                "daily_change_percent": 1.36,
                "volume": 23456789
            },
            "news_sentiment": {
                "aggregate_sentiment": {"average_score": 0.65},
                "articles": [
                    {
                        "title": "Test Article",
                        "overall_sentiment_score": 0.75
                    }
                ]
            },
            "fundamentals": {
                "latest_filing": {
                    "metrics": {
                        "revenue": "100000000",
                        "net_income": "25000000",
                        "operating_income": "30000000",
                        "assets": "200000000",
                        "liabilities": "100000000",
                        "stockholders_equity": "100000000",
                        "current_assets": "80000000",
                        "current_liabilities": "40000000"
                    }
                },
                "historical_filings": [
                    {
                        "metrics": {
                            "revenue": "100000000",
                            "net_income": "25000000"
                        }
                    },
                    {
                        "metrics": {
                            "revenue": "90000000",
                            "net_income": "22000000"
                        }
                    }
                ]
            }
        }
    }

class TestStockAnalysisLLM:
    def test_generate_analysis(self, sample_stock_data):
        analyzer = StockAnalysisLLM()
        analysis = analyzer.generate_analysis(sample_stock_data)
        
        assert analysis is not None
        assert "symbol" in analysis
        assert "timestamp" in analysis
        assert analysis["symbol"] == "AAPL"
        # Updated test to check for the actual structure returned by the analyzer
        assert isinstance(analysis["analysis"], dict)
        assert "market_data" in analysis["analysis"]
        assert "news_data" in analysis["analysis"]
        assert "fundamental_data" in analysis["analysis"]

    def test_format_market_data(self):
        analyzer = StockAnalysisLLM()
        market_data = {
            "current_price": 175.50,
            "daily_change_percent": 1.36,
            "volume": 23456789
        }
        formatted_data = analyzer.format_market_data(market_data)
        
        assert isinstance(formatted_data, str)
        # Updated test to match the actual formatting
        assert "Current Price: $175.5" in formatted_data
        assert "Daily Change: 1.36%" in formatted_data
        assert "Trading Volume: 23456789" in formatted_data

    def test_format_news_data(self):
        analyzer = StockAnalysisLLM()
        news_data = {
            "aggregate_sentiment": {"average_score": 0.65},
            "articles": [
                {
                    "title": "Test Article",
                    "overall_sentiment_score": 0.75
                }
            ]
        }
        formatted_data = analyzer.format_news_data(news_data)
        
        assert isinstance(formatted_data, str)
        assert "0.65" in formatted_data
        assert "Test Article" in formatted_data
        assert "0.75" in formatted_data

    def test_format_fundamental_data(self):
        analyzer = StockAnalysisLLM()
        fundamental_data = {
            "latest_filing": {
                "metrics": {
                    "revenue": "100000000",
                    "net_income": "25000000",
                    "operating_income": "30000000",
                    "assets": "200000000",
                    "liabilities": "100000000",
                    "stockholders_equity": "100000000",
                    "current_assets": "80000000",
                    "current_liabilities": "40000000"
                }
            }
        }
        formatted_data = analyzer.format_fundamental_data(fundamental_data)
        
        assert isinstance(formatted_data, str)
        assert "$100,000,000.00" in formatted_data
        assert "$25,000,000.00" in formatted_data
        assert "Current Ratio" in formatted_data