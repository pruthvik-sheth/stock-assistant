// src/services/stockApi.js
const API_BASE_URL = "http://127.0.0.1:8000/api";

export const stockApi = {
  async getStockData(symbol) {
    const response = await fetch(`${API_BASE_URL}/stock/${symbol}`);
    if (!response.ok) {
      throw new Error("Failed to fetch stock data");
    }
    return response.json();
  },

  async searchSymbols(query) {
    const response = await fetch(`${API_BASE_URL}/search?q=${query}`);
    if (!response.ok) {
      throw new Error("Failed to search symbols");
    }
    return response.json();
  },

  async getDefaultStock() {
    const response = await fetch(`${API_BASE_URL}/default`);
    console.log(response);

    if (!response.ok) {
      throw new Error("Failed to fetch default stock");
    }
    return response.json();
  },
};
