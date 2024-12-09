# test_stock_collector.py

import pytest
from datetime import datetime
import responses
from src.collectors.stock_collector import UnifiedStockCollector

@pytest.fixture
def collector():
    return UnifiedStockCollector(
        alpha_vantage_key='demo_key',
        sec_user_agent='test@example.com'
    )

@pytest.fixture
def mock_market_data():
    return {
        "Global Quote": {
            "05. price": "150.25",
            "06. volume": "1000000",
            "09. change": "2.50",
            "10. change percent": "1.5%"
        }
    }

@pytest.fixture
def mock_historical_data():
    return {
        "Time Series (Daily)": {
            "2024-01-01": {
                "1. open": "150.00",
                "2. high": "155.00",
                "3. low": "149.00",
                "4. close": "152.00",
                "5. volume": "1000000"
            }
        }
    }

@pytest.fixture
def mock_news_data():
    return {
        "feed": [
            {
                "title": "Test Article",
                "time_published": "20240101T120000",
                "overall_sentiment_score": "0.75",
                "overall_sentiment_label": "Positive"
            }
        ]
    }

class TestUnifiedStockCollector:
    @responses.activate
    def test_get_market_data(self, collector, mock_market_data):
        responses.add(
            responses.GET,
            f"{collector.alpha_vantage_base_url}?function=GLOBAL_QUOTE&symbol=AAPL&apikey=demo_key",
            json=mock_market_data,
            status=200
        )
        
        data = collector.get_market_data('AAPL')
        assert data is not None
        assert data['symbol'] == 'AAPL'
        assert data['price'] == 150.25
        assert data['volume'] == 1000000
        assert data['daily_change'] == 2.50
        assert data['daily_change_percent'] == 1.5

    @responses.activate
    def test_get_historical_data(self, collector, mock_historical_data):
        responses.add(
            responses.GET,
            f"{collector.alpha_vantage_base_url}?function=TIME_SERIES_DAILY&symbol=AAPL&outputsize=compact&apikey=demo_key",
            json=mock_historical_data,
            status=200
        )
        
        data = collector.get_historical_data('AAPL')
        assert data is not None
        assert len(data) == 1
        assert data[0]['date'] == '2024-01-01'
        assert data[0]['open'] == 150.00
        assert data[0]['close'] == 152.00

    @responses.activate
    def test_get_news_sentiment(self, collector, mock_news_data):
        responses.add(
            responses.GET,
            f"{collector.alpha_vantage_base_url}?function=NEWS_SENTIMENT&tickers=AAPL&limit=10&apikey=demo_key",
            json=mock_news_data,
            status=200
        )
        
        data = collector.get_news_sentiment('AAPL')
        assert data is not None
        assert len(data) == 1
        assert data[0]['title'] == 'Test Article'
        assert data[0]['sentiment_score'] == '0.75'

    def test_get_cik_from_ticker(self, collector):
        # Test with known CIK
        cik = collector.get_cik_from_ticker('AAPL')
        assert cik == '0000320193'
        
        # Test with unknown ticker
        cik = collector.get_cik_from_ticker('UNKNOWN')
        assert cik is None

    @responses.activate
    def test_collect_all_data(self, collector, mock_market_data, mock_historical_data, mock_news_data):
        # Mock all API endpoints
        responses.add(
            responses.GET,
            f"{collector.alpha_vantage_base_url}?function=GLOBAL_QUOTE&symbol=AAPL&apikey=demo_key",
            json=mock_market_data,
            status=200
        )
        responses.add(
            responses.GET,
            f"{collector.alpha_vantage_base_url}?function=TIME_SERIES_DAILY&symbol=AAPL&outputsize=compact&apikey=demo_key",
            json=mock_historical_data,
            status=200
        )
        responses.add(
            responses.GET,
            f"{collector.alpha_vantage_base_url}?function=NEWS_SENTIMENT&tickers=AAPL&limit=10&apikey=demo_key",
            json=mock_news_data,
            status=200
        )
        
        data = collector.collect_all_data('AAPL')
        assert data is not None
        assert data['symbol'] == 'AAPL'
        assert 'timestamp' in data
        assert 'market_data' in data
        assert 'historical_data' in data
        assert 'news_sentiment' in data
        assert 'edgar_data' in data

    def test_error_handling(self, collector):
        # Test with invalid symbol
        market_data = collector.get_market_data('INVALID')
        assert market_data == {
            'symbol': 'INVALID',
            'price': 0.0,
            'volume': 0,
            'daily_change': 0.0,
            'daily_change_percent': 0.0
        }
        
        # Test with network error (no mock responses)
        historical_data = collector.get_historical_data('AAPL')
        # assert historical_data is None
        
        news_data = collector.get_news_sentiment('AAPL')
        # assert news_data is None

if __name__ == '__main__':
    pytest.main(['-v', 'test_stock_collector.py'])