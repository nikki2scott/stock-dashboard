from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel


import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Load .env file from backend directory
load_dotenv(BASE_DIR / ".env", override=True)


def get_finnhub_api_key() -> str | None:
    return os.getenv("FINNHUB_API_KEY") or os.getenv("FINNHUB_KEY") or os.getenv("API_KEY")


FINNHUB_API_KEY = get_finnhub_api_key()

class StockResponse(BaseModel):
    ticker: str
    message: str

class StockQuote(BaseModel):
    ticker: str
    current_price: float
    change: float
    change_percent: float
    high_price: float
    low_price: float
    open_price: float
    previous_close: float

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Stock Dashboard API"}

@app.get("/status")
async def status():
    return {"status": "Online", "message": "Stock Dashboard API is running successfully."}

@app.get("/about")
async def about():
    return {"project": "Stock Dashboard", "developer": "Nikki"}

@app.get("/health")
async def health():
    return {"healthy": "true"}

# used for direct viewing a stock, mostly for when just viewing a stock and not searching for it. This is more of a direct lookup.
@app.get("/stocks/{ticker}")
async def stock_ticker(ticker: str):
    ticker = ticker.upper()
    if len(ticker) > 5:
        raise HTTPException(status_code=400, detail="Ticker symbol is too long. Please provide a valid ticker symbol.")
    if len(ticker) == 0:
        raise HTTPException(status_code=400, detail="Ticker symbol is required. Please provide a valid ticker symbol.")

    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={FINNHUB_API_KEY}"
    request = Request(url, headers={"User-Agent": "stock-dashboard/1.0"})

    try:
        with urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
    except HTTPError as exc:
        raise HTTPException(status_code=exc.code, detail={"message": exc.reason}) from exc
    except URLError as exc:
        raise HTTPException(status_code=502, detail=f"Unable to reach Finnhub: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="Invalid response from Finnhub.") from exc
    
    if not data or data.get("c") == 0:
        raise HTTPException(
            status_code=404,
            detail="Ticker not found or no quote data available."
        )
    return StockQuote(ticker=ticker, current_price=data["c"], change=data["d"], change_percent=data["dp"], high_price=data["h"], low_price=data["l"], open_price=data["o"], previous_close=data["pc"])

# Alternative test route for searching stocks by query parameters, used more as a search filter.
@app.get("/search")
async def search_stock(ticker: str):
    ticker = ticker.upper()
    if len(ticker) > 5:
        raise HTTPException(status_code=400, detail="Ticker symbol is too long. Please provide a valid ticker symbol.")
    if len(ticker) == 0:
        raise HTTPException(status_code=400, detail="Ticker symbol is required. Please provide a valid ticker symbol.")
    if not FINNHUB_API_KEY:
        raise HTTPException(status_code=500, detail="API key not found. Please check your environment variables.")
    return StockResponse(ticker=ticker, message="Stock search received.")


#Temp test endpoint for testing the API key and environment variable loading
@app.get("/apikey-test")
async def api_key_test():
    if FINNHUB_API_KEY:
        return {"loaded": True}
    else:
        raise HTTPException(status_code=500, detail="API key not found. Please check your environment variables.")

#Test endpoint for testing the Finnhub API connection and response
@app.get("/finnhub-test")
async def finnhub_test():
    if not FINNHUB_API_KEY:
        raise HTTPException(status_code=500, detail="API key not found. Please check your environment variables.")

    url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={FINNHUB_API_KEY}"
    request = Request(url, headers={"User-Agent": "stock-dashboard/1.0"})

    try:
        with urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
    except HTTPError as exc:
        raise HTTPException(status_code=exc.code, detail={"message": exc.reason, "url": url}) from exc
    except URLError as exc:
        raise HTTPException(status_code=502, detail=f"Unable to reach Finnhub: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail="Invalid response from Finnhub.") from exc

    return StockQuote(
    ticker="AAPL",
    current_price=data["c"],
    change=data["d"],
    change_percent=data["dp"],
    high_price=data["h"],
    low_price=data["l"],
    open_price=data["o"],
    previous_close=data["pc"]
)