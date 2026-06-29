from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

class StockResponse(BaseModel):
    ticker: str
    message: str

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
    return StockResponse(ticker=ticker, message="Stock lookup received.")

# Alternative test route for searching stocks by query parameters, used more as a search filter.
@app.get("/search")
async def search_stock(ticker: str):
    ticker = ticker.upper()
    if len(ticker) > 5:
        raise HTTPException(status_code=400, detail="Ticker symbol is too long. Please provide a valid ticker symbol.")
    if len(ticker) == 0:
        raise HTTPException(status_code=400, detail="Ticker symbol is required. Please provide a valid ticker symbol.")
    return StockResponse(ticker=ticker, message="Stock search received.")