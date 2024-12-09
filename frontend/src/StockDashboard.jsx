// import { useState } from 'react';
// import Highcharts from 'highcharts/highstock';
// import HighchartsReact from 'highcharts-react-official';
// import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
// import { Input } from "@/components/ui/input";
// import { AlertTriangle, BarChart2, Search, MessageSquare } from "lucide-react";
// import { Progress } from "@/components/ui/progress";

// const StockDashboard = () => {
//   const [searchQuery, setSearchQuery] = useState('');

//   // Sample data - this would come from your backend
//   const stockData = [
//     [Date.UTC(2024, 0, 1), 150],
//     [Date.UTC(2024, 1, 1), 155],
//     [Date.UTC(2024, 2, 1), 153],
//     [Date.UTC(2024, 3, 1), 165]
//   ];

//   const chartOptions = {
//     chart: {
//       height: 300,
//       style: {
//         fontFamily: 'inherit'
//       }
//     },
//     title: {
//       text: ''
//     },
//     xAxis: {
//       type: 'datetime',
//       labels: {
//         style: {
//           color: '#666'
//         }
//       }
//     },
//     yAxis: {
//         title: {
//             text: 'Price',
//             style: {
//             color: '#666'
//             }
//         },
//         labels: {
//             style: {
//             color: '#666'
//             },
//             align: 'left', // Align labels to the left
//         },
//         opposite: false // This moves the axis to the left side
//     },
//     series: [{
//       name: 'Stock Price',
//       data: stockData,
//       color: '#2563eb',
//       lineWidth: 2,
//       marker: {
//         enabled: true,
//         radius: 4
//       }
//     }],
//     credits: {
//       enabled: false
//     },
//     tooltip: {
//       valuePrefix: '$'
//     },
//     rangeSelector: {
//       enabled: false
//     },
//     navigator: {
//       enabled: false
//     },
//     scrollbar: {
//       enabled: false
//     }
//   };

//   const insights = {
//     summary: "Based on recent earnings reports and market trends, this stock shows strong potential for growth. Key metrics indicate positive momentum.",
//     keyPoints: [
//       "Revenue grew 25% YoY",
//       "New product launch expected in Q3",
//       "Strong institutional buying detected"
//     ]
//   };

//   const risks = {
//     message: "Market volatility is currently high. Consider diversifying your portfolio.",
//     volatilityRisk: 75,
//     marketRisk: 85
//   };

//   return (
//     <div className="py-6 w-4/6 mx-auto space-y-6">
//       {/* Search Bar */}
//       <div className="relative">
//         <Search className="absolute left-3 top-3 h-4 w-4 text-gray-500" />
//         <Input
//           placeholder="Search for stocks..."
//           className="pl-10 w-full"
//           value={searchQuery}
//           onChange={(e) => setSearchQuery(e.target.value)}
//         />
//       </div>

//       {/* Price Trends Card */}
//       <Card>
//         <CardHeader className="flex flex-row items-center justify-between">
//           <CardTitle className="flex items-center gap-2">
//             <BarChart2 className="h-5 w-5" />
//             Price Trends
//           </CardTitle>
//         </CardHeader>
//         <CardContent>
//           <HighchartsReact
//             highcharts={Highcharts}
//             constructorType={'stockChart'}
//             options={chartOptions}
//             containerClassName="w-[80%]"
//           />
//         </CardContent>
//       </Card>

//       {/* Analysis and Risk Cards Grid */}
//       <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//         {/* AI Analysis Card */}
//         <Card>
//           <CardHeader>
//             <CardTitle className="flex items-center gap-2">
//               <MessageSquare className="h-5 w-5" />
//               AI Analysis
//             </CardTitle>
//           </CardHeader>
//           <CardContent>
//             <p className="text-gray-600 mb-4">
//               {insights.summary}
//             </p>
//             <div className="space-y-2">
//               <h4 className="font-semibold">Key Insights:</h4>
//               <ul className="list-disc pl-5 space-y-1">
//                 {insights.keyPoints.map((point, index) => (
//                   <li key={index} className="text-gray-600">{point}</li>
//                 ))}
//               </ul>
//             </div>
//           </CardContent>
//         </Card>

//         {/* Risk Assessment Card */}
//         <Card>
//           <CardHeader>
//             <CardTitle className="flex items-center gap-2">
//               <AlertTriangle className="h-5 w-5" />
//               Risk Assessment
//             </CardTitle>
//           </CardHeader>
//           <CardContent>
//             <p className="text-gray-600 mb-6">
//               {risks.message}
//             </p>
//             <div className="space-y-4">
//               <div>
//                 <div className="flex justify-between mb-2">
//                   <span className="text-sm font-medium">Volatility Risk</span>
//                   <span className="text-sm text-gray-500">{risks.volatilityRisk}%</span>
//                 </div>
//                 <Progress value={risks.volatilityRisk} className="h-2" />
//               </div>
//               <div>
//                 <div className="flex justify-between mb-2">
//                   <span className="text-sm font-medium">Market Risk</span>
//                   <span className="text-sm text-gray-500">{risks.marketRisk}%</span>
//                 </div>
//                 <Progress value={risks.marketRisk} className="h-2" />
//               </div>
//             </div>
//           </CardContent>
//         </Card>
//       </div>
//     </div>
//   );
// };

// export default StockDashboard;


// src/components/StockDashboard.js
import Markdown from 'react-markdown'
// import remarkGfm from 'remark-gfm'
import { useState, useEffect, useCallback } from 'react';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { AlertTriangle, BarChart2, Search, MessageSquare } from "lucide-react";
import { stockApi } from '@/services/stockApi';
import { useDebounce } from '@/hooks/useDebounce';


const StockDashboard = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [stockData, setStockData] = useState(null);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const debouncedSearch = useDebounce(searchQuery, 300);

  // Load default stock data
  useEffect(() => {
    const loadDefaultStock = async () => {
      try {
        setLoading(true);
        const data = await stockApi.getDefaultStock();
        setStockData(data);
      } catch (err) {
        setError('Failed to load default stock data');
      } finally {
        setLoading(false);
      }
    };

    loadDefaultStock();
  }, []);

  // Handle search
  useEffect(() => {
    const searchStocks = async () => {
      if (debouncedSearch) {
        try {
          const symbols = await stockApi.searchSymbols(debouncedSearch);
          setSearchResults(symbols);
        } catch (err) {
          console.error('Search failed:', err);
        }
      } else {
        setSearchResults([]);
      }
    };

    searchStocks();
  }, [debouncedSearch]);

  // Load stock data when symbol is selected
  const handleSelectStock = async (symbol) => {
    try {
      setLoading(true);
      setSearchQuery(symbol);
      setSearchResults([]);
      const data = await stockApi.getStockData(symbol);
      setStockData(data);
    } catch (err) {
      setError('Failed to load stock data');
    } finally {
      setLoading(false);
    }
  };

const mockDataArray = [
    [new Date('2024-12-04').getTime(), 100],
    [new Date('2024-12-03').getTime(), 102],
    [new Date('2024-12-02').getTime(), 101],
    [new Date('2024-11-29').getTime(), 105],
    [new Date('2024-11-27').getTime(), 107],
    [new Date('2024-11-26').getTime(), 110],
    [new Date('2024-11-25').getTime(), 108],
    [new Date('2024-11-22').getTime(), 112],
]

  console.log(stockData?.historical_data?.dates?.map((date, index) => {
          // console.log(new Date(date).getTime());
          // console.log(stockData.historical_data.prices[index]);
          
          return [
            new Date(date).getTime(),
            stockData.historical_data.prices[index]
          ]
        }).splice(0, 10));
  

  const getChartOptions = useCallback(() => {
    if (!stockData) return {};

    return {
      chart: {
        height: 300,
        style: {
          fontFamily: 'inherit'
        }
      },
      title: {
        text: ''
      },
      xAxis: {
        type: 'datetime',
        labels: {
          style: {
            color: '#666'
          }
        }
      },
      yAxis: {
        opposite: false,
        title: {
          text: 'Price',
          style: {
            color: '#666'
          }
        },
        labels: {
          style: {
            color: '#666'
          }
        }
      },
      series: [{
        name: 'Stock Price',
        data: stockData.historical_data.dates.map((date, index) => {
          // console.log(new Date(date).getTime());
          // console.log(stockData.historical_data.prices[index]);
          
          return [
            new Date(date).getTime(),
            stockData.historical_data.prices[index]
          ]
        }).splice(0, 365),
        yAxis: 0,
        color: '#2563eb',
        lineWidth: 2,
        marker: {
          enabled: true,
          radius: 4
        }
      }],
      credits: {
        enabled: false
      },
      tooltip: {
        valuePrefix: '$'
      },
      rangeSelector: {
        enabled: false
      },
      navigator: {
        enabled: false
      },
      scrollbar: {
        enabled: false
      }
    };
  }, [stockData]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-gray-500" />
        <Input
          placeholder="Search for stocks..."
          className="pl-10 w-full"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {searchResults.length > 0 && (
          <div className="absolute w-full mt-1 bg-white border rounded-md shadow-lg z-10">
            {searchResults.map((symbol) => (
              <div
                key={symbol}
                className="px-4 py-2 hover:bg-gray-100 cursor-pointer"
                onClick={() => handleSelectStock(symbol)}
              >
                {symbol}
              </div>
            ))}
          </div>
        )}
      </div>

      {loading ? (
        <div className="text-center">Loading...</div>
      ) : error ? (
        <div className="text-red-500 text-center">{error}</div>
      ) : stockData ? (
        <>
          {/* Price Trends Card */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <BarChart2 className="h-5 w-5" />
                Price Trends - {stockData.symbol}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <HighchartsReact
                highcharts={Highcharts}
                constructorType={'stockChart'}
                options={getChartOptions()}
              />
            </CardContent>
          </Card>

          {/* Analysis and Risk Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* AI Analysis Card */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  AI Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 whitespace-pre-line">
                  <Markdown>{stockData.analysis.text}</Markdown>
                </p>
              </CardContent>
            </Card>

            {/* Market Overview Card */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Market Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Price</span>
                      <span className="text-sm text-gray-500">
                        ${stockData.market_data.current_price}
                      </span>
                    </div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Daily Change</span>
                      <span className={`text-sm ${
                        stockData.market_data.daily_change_percent >= 0 
                        ? 'text-green-500' 
                        : 'text-red-500'
                      }`}>
                        {stockData.market_data.daily_change_percent}%
                      </span>
                    </div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium">Volume</span>
                      <span className="text-sm text-gray-500">
                        {stockData.market_data.volume.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default StockDashboard;