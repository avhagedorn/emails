from yfinance import Ticker
from pydantic import BaseModel, Field


class GetStockOrIndexPrice(BaseModel):
    ticker: str = Field(..., title="Ticker", description="The stock or index ticker")
    year: int = Field(..., title="Year", description="The year to get the price for")
    month: int = Field(..., title="Month", description="The month to get the price for")
    day: int = Field(..., title="Day", description="The day to get the price for")


async def get_stock_or_index_price(args: GetStockOrIndexPrice):
    try:
        ticker = args.ticker
        stock = Ticker(ticker)
        day_before_date = f"{args.year}-{args.month}-{args.day - 1}"
        date = f"{args.year}-{args.month}-{args.day}"
        history = stock.history(start=day_before_date, end=date)
        last_price = float(history.Close.iloc[0])
        return last_price
    except Exception as e:
        print(e)
        raise e
        # return "error"
