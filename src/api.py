from dotenv import load_dotenv
import os
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient

load_dotenv()

API_KEY = os.getenv("API_KEY")
SECRET = os.getenv("SECRET")

url = "https://data.alpaca.markets/v2/stocks"

tClient = TradingClient(
    API_KEY,
    SECRET
)

dClient = StockHistoricalDataClient(
    API_KEY,
    SECRET
)