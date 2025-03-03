from pydantic import BaseModel, Field

from data_utils.utils import db_save_transaction


class SaveTransaction(BaseModel):
    ticker: str = Field(..., title="Ticker", description="The stock or index ticker")
    shares: float = Field(..., title="Shares", description="The number of shares")
    price: float = Field(..., title="Price", description="The price per share")
    current_spy_price: float = Field(
        ...,
        title="Current SPY price",
        description="The current price of the index with ticker 'SPY'",
    )
    year: int = Field(..., title="Year", description="The year to get the price for")
    month: int = Field(..., title="Month", description="The month to get the price for")
    day: int = Field(..., title="Day", description="The day to get the price for")
    transaction_is_buy: bool = Field(
        ...,
        title="Transaction is buy",
        description="Whether the transaction is a buy (True) or a sell (False)",
    )


async def save_transaction(args: SaveTransaction):
    equivalent_spy_shares = args.shares * args.price / args.current_spy_price
    try:
        await db_save_transaction(
            args.ticker,
            args.shares,
            args.price,
            equivalent_spy_shares,
            args.year,
            args.month,
            args.day,
            args.transaction_is_buy,
        )
        return "success"
    except Exception as e:
        print(e)
        raise e
        # return "error"
