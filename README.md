# QuantAI - Stock Analysis Platform

An AI-powered stock analysis platform that combines real-time market data with LLM-based insights for comprehensive stock analysis.

## Project Structure

stock-assistant-final/
├── backend/
│ ├── src/
│ │ ├── analysis/
│ │ │ └── llm_analyzer.py
│ │ ├── api/
│ │ │ └── auth_server.py
│ │ ├── collectors/
│ │ │ ├── edgar_collector.py
│ │ │ ├── market_collector.py
│ │ │ ├── news_collector.py
│ │ │ └── stock_collector.py
│ │ └── storage/
│ │ ├── DatabaseConnection.py
│ │ ├── StockDataAggregator.py
│ │ └── StockDataStorage.py
│ ├── data/
│ │ ├── processed/
│ │ └── raw/
│ └── tests/
│ ├── conftest.py
│ ├── test_analysis.py
│ └── test_stock_collector.py
│
└── frontend/
├── src/
│ ├── components/
│ ├── services/
│ ├── hooks/
│ ├── lib/
│ └── StockDashboard.jsx
└── public/

## Features

### Data Collection & Analysis

- Real-time market data from Alpha Vantage API
- Financial data from SEC EDGAR API
- News sentiment analysis
- LLM-powered market insights using Llama 2

### Visualization

- Interactive stock price charts with Highcharts
- Real-time market data updates
- AI analysis dashboard
- Sentiment and risk analysis

## Tech Stack

### Backend

- Python 3.10+
- Flask
- MongoDB
- Ollama (LLaMA 2)

### Frontend

- React
- Highcharts
- Tailwind CSS
- shadcn/ui

## Setup Instructions

### Backend Setup

1. Create and activate virtual environment

```bash
python -m venv .myvenv
source .myvenv/bin/activate  # Linux/Mac
# or
.myvenv\Scripts\activate    # Windows
```

2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables

```bash
# Create .env file in backend directory
ALPHA_VANTAGE_API_KEY=your_key
MONGODB_URI=mongodb://localhost:27017/
```

### Frontend Setup

1. Install dependencies

```bash
cd frontend
npm install
```

2. Set up environment variables

```bash
# Create .env file in frontend directory
REACT_APP_API_URL=http://localhost:5000
```

## Running the Application

1. Start Backend

```bash
cd backend
python src/api/auth_server.py
```

2. Start Frontend

```bash
cd frontend
npm start
```

## Testing

Run backend tests:

```bash
cd backend
pytest tests/
```

## API Endpoints

- `GET /api/stock/<symbol>` - Get stock data
- `GET /api/search?q=<query>` - Search stocks
- `GET /api/stock/<symbol>/analysis` - Get AI analysis

## Key Components

### Backend

- `llm_analyzer.py`: LLM-based stock analysis
- `market_collector.py`: Real-time market data collection
- `edgar_collector.py`: SEC EDGAR data integration
- `news_collector.py`: News sentiment analysis
- `StockDataStorage.py`: MongoDB data management

### Frontend

- `StockDashboard.jsx`: Main dashboard component
- Highcharts integration for price visualization
- Real-time data updates
- Responsive design with Tailwind CSS

## Dependencies

### Backend

- Flask
- pymongo
- pandas
- requests
- pytest
- python-dotenv

### Frontend

- React
- Highcharts
- tailwindcss
- shadcn/ui
- lucide-react

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push branch (`git push origin feature/name`)
5. Open Pull Request

## License

MIT License

## Acknowledgments

- Alpha Vantage for market data API
- SEC EDGAR for financial data
- Ollama for LLM integration
