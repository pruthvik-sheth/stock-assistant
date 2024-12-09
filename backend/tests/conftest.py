# tests/conftest.py
import pytest
from datetime import datetime

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