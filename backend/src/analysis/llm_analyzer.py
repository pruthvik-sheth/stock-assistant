from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
from datetime import datetime
import os
from typing import Dict, List

class StockAnalysisLLM:
    def __init__(self):
        """Initialize the LLM service using Ollama"""
        self.llm = Ollama(model="llama3.2:3b")

        # Comprehensive analysis prompt
        self.analysis_template = """You are an expert financial analyst. 
        Analyze the following comprehensive stock data and provide a clear, insightful summary.
        Make sure to specifically reference the provided metrics and growth rates in your analysis.

        Stock Symbol: {symbol}

        Market Data:
        {market_data}

        News Sentiment:
        {news_data}

        Fundamental Data:
        {fundamental_data}

        Based on the SPECIFIC numerical data provided above, provide a professional analysis that includes:
        1. Overall market position and trend analysis, citing the exact price and volume numbers
        2. Growth analysis using the provided revenue and income growth rates
        3. Financial health assessment using the provided ratios and metrics
        4. News sentiment impact on stock performance with the specific sentiment score
        5. Three most important actionable insights based on the numerical data

        Focus on the actual numbers provided and avoid making assumptions about missing data.
        If a particular metric is referenced, always include its specific value.

        Analysis:"""

    def format_market_data(self, market_data: Dict) -> str:
        """Format market data for the prompt"""
        return f"""
        Current Price: ${market_data.get('current_price', 'N/A')}
        Daily Change: {market_data.get('daily_change_percent', 'N/A')}%
        Trading Volume: {market_data.get('volume', 'N/A')}
        """

    def format_news_data(self, news_data: Dict) -> str:
        """Format news sentiment data for the prompt"""
        articles = news_data.get('articles', [])[:5]  # Get latest 5 articles
        sentiment_summary = f"""
        Overall Sentiment Score: {news_data.get('aggregate_sentiment', {}).get('average_score', 'N/A')}
        Recent Headlines:
        """
        for article in articles:
            sentiment_summary += f"- {article.get('title')} (Sentiment: {article.get('overall_sentiment_score')})\n"
        return sentiment_summary

    def format_fundamental_data(self, fundamental_data: Dict) -> str:
        """Format fundamental data for the prompt"""
        try:
            metrics = fundamental_data.get('latest_filing', {}).get('metrics', {})
            historical = fundamental_data.get('historical_filings', [])
            
            # Convert string values to float and handle formatting
            def format_value(value):
                try:
                    return f"${float(value):,.2f}" if value else "N/A"
                except (ValueError, TypeError):
                    return "N/A"
            
            # Format current metrics
            current_metrics = f"""
            Current Financial Metrics:
            - Revenue: {format_value(metrics.get('revenue'))}
            - Net Income: {format_value(metrics.get('net_income'))}
            - Operating Income: {format_value(metrics.get('operating_income'))}
            - Total Assets: {format_value(metrics.get('assets'))}
            - Total Liabilities: {format_value(metrics.get('liabilities'))}
            - Stockholders Equity: {format_value(metrics.get('stockholders_equity'))}
            """
            
            # Calculate growth metrics if historical data is available
            if historical and len(historical) > 1:
                try:
                    current_period = historical[0]['metrics']
                    previous_period = historical[1]['metrics']
                    
                    def calculate_growth(current, previous):
                        try:
                            current = float(current or 0)
                            previous = float(previous or 1)  # Avoid division by zero
                            return ((current - previous) / previous) * 100
                        except (ValueError, TypeError):
                            return None
                    
                    revenue_growth = calculate_growth(
                        current_period.get('revenue'),
                        previous_period.get('revenue')
                    )
                    
                    net_income_growth = calculate_growth(
                        current_period.get('net_income'),
                        previous_period.get('net_income')
                    )
                    
                    growth_metrics = f"""
                    Growth Metrics (Year-over-Year):
                    - Revenue Growth: {f'{revenue_growth:.2f}%' if revenue_growth is not None else 'N/A'}
                    - Net Income Growth: {f'{net_income_growth:.2f}%' if net_income_growth is not None else 'N/A'}
                    """
                except Exception as e:
                    growth_metrics = f"Error calculating growth metrics: {str(e)}"
            else:
                growth_metrics = "Historical growth data not available"
            
            # Calculate key financial ratios
            try:
                current_assets = float(metrics.get('current_assets') or 0)
                current_liabilities = float(metrics.get('current_liabilities') or 1)
                revenue = float(metrics.get('revenue') or 1)
                net_income = float(metrics.get('net_income') or 0)
                
                current_ratio = current_assets / current_liabilities
                profit_margin = (net_income / revenue) * 100
                
                financial_ratios = f"""
                Financial Ratios:
                - Current Ratio: {current_ratio:.2f}
                - Profit Margin: {profit_margin:.2f}%
                """
            except Exception as e:
                financial_ratios = f"Error calculating financial ratios: {str(e)}"
            
            return current_metrics + "\n" + growth_metrics + "\n" + financial_ratios

        except Exception as e:
            print(f"Error formatting fundamental data: {e}")
            return "Error processing fundamental data"

    def generate_analysis(self, stock_data: Dict) -> Dict:
        """Generate comprehensive stock analysis"""
        try:
            symbol = stock_data['symbol']
            data = stock_data['data']

            # Format different data components
            market_str = self.format_market_data(data.get('market', {}))
            news_str = self.format_news_data(data.get('news_sentiment', {}))
            fundamental_str = self.format_fundamental_data(data.get('fundamentals', {}))

            # Create analysis chain
            analysis_chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    template=self.analysis_template,
                    input_variables=["symbol", "market_data", "news_data", "fundamental_data"]
                )
            )

            # Generate analysis
            analysis = analysis_chain.invoke({
                "symbol": symbol,
                "market_data": market_str,
                "news_data": news_str,
                "fundamental_data": fundamental_str
            })

            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis
            }

        except Exception as e:
            print(f"Error generating analysis for {stock_data.get('symbol', 'unknown')}: {e}")
            return {
                "symbol": stock_data.get('symbol', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

def analyze_stocks(aggregated_data_path: str, output_dir: str = 'analysis_results'):
    """Analyze stocks and save results"""
    analyzer = StockAnalysisLLM()
    
    # Load aggregated data
    with open(aggregated_data_path, 'r') as f:
        stocks_data = json.load(f)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Analyze stocks
    analysis_results = []
    for stock_data in stocks_data:
        print(f"\nAnalyzing {stock_data['symbol']}...")
        analysis = analyzer.generate_analysis(stock_data)
        analysis_results.append(analysis)
    
    # Save results
    output_file = os.path.join(output_dir, f'stock_analysis_{timestamp}.json')
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=4)
    
    print(f"\nAnalysis completed. Results saved to {output_file}")
    return analysis_results

if __name__ == "__main__":
    aggregated_data_path = "aggregated_data/aggregated_stock_data_latest.json"
    analysis_results = analyze_stocks(aggregated_data_path)
    
    # Print sample analysis
    for result in analysis_results:
        print(f"\n=== Analysis for {result['symbol']} ===")
        print(result['analysis'])