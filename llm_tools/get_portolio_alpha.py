import yfinance as yf
from pydantic import BaseModel

from data_utils.utils import db_get_transactions


class GetPortfolioAlpha(BaseModel):
    pass


async def get_portfolio_alpha(_: GetPortfolioAlpha):
    try:
        data = await db_get_transactions()
        transactions = data["transactions"]

        if not transactions:
            return {
                "alpha": 0,
                "portfolio_return": 0,
                "spy_return": 0,
                "transactions_with_returns": [],
            }

        stock_tickers = get_tickers(transactions)
        current_prices = await get_current_prices(stock_tickers)
        alpha = await get_alpha(transactions, current_prices)
        return alpha  # 🐺

    except Exception as e:
        print(e)
        raise e
        # return "error"


def get_tickers(transactions):
    stock_tickers = set([transaction["ticker"] for transaction in transactions])
    stock_tickers.add("SPY")
    return stock_tickers


async def get_current_prices(tickers):
    current_prices = {}
    for ticker in tickers:
        try:
            ticker_data = yf.download(ticker, period="1d")
            if not ticker_data.empty:
                current_prices[ticker] = float(ticker_data["Close"].iloc[-1])
            else:
                current_prices[ticker] = None
        except Exception as e:
            print(f"Error fetching current price for {ticker}: {e}")
            current_prices[ticker] = None
    return current_prices


# ai gen, i've done this before and it is just time consuming. bleh. sorrys.
async def get_alpha(transactions, current_prices):
    capital_invested = 0
    current_portfolio_value = 0
    spy_equivalent_value = 0

    # Track shares held for each ticker
    shares_held = {}
    spy_shares_held = 0

    for transaction in transactions:
        ticker = transaction["ticker"]
        avg_price = transaction["price"]  # per share
        shares = transaction["shares"]
        equivalent_spy_shares = transaction["equivalent_spy_shares"]
        is_buy = transaction["transaction_is_buy"]

        # Initialize ticker in shares_held if not present
        if ticker not in shares_held:
            shares_held[ticker] = 0

        # Handle buy transaction
        if is_buy:
            # Calculate cost basis for this buy transaction
            transaction_cost = avg_price * shares
            capital_invested += transaction_cost

            # Add shares to holdings
            shares_held[ticker] += shares

            # Add equivalent SPY shares for benchmarking
            spy_shares_held += equivalent_spy_shares

        # Handle sell transaction
        else:
            # Validate sell transaction - skip if trying to sell more than owned
            if shares > shares_held[ticker]:
                continue  # Skip this transaction if selling more than we have

            # Calculate sell impact
            shares_held[ticker] -= shares

            # For sell transactions, reduce capital invested
            # This assumes we're selling at the same proportion of our cost basis
            if shares_held[ticker] > 0:
                sell_fraction = shares / (shares_held[ticker] + shares)
            else:
                sell_fraction = 1.0

            capital_reduction = capital_invested * sell_fraction
            capital_invested -= capital_reduction

            # Reduce equivalent SPY shares proportionally
            if equivalent_spy_shares > 0:
                spy_shares_reduction = equivalent_spy_shares
                spy_shares_held -= spy_shares_reduction

    # Calculate current value based on remaining holdings
    for ticker, shares in shares_held.items():
        if (
            shares > 0
            and ticker in current_prices
            and current_prices[ticker] is not None
        ):
            current_price = current_prices[ticker]
            current_value = current_price * shares
            current_portfolio_value += current_value

    # Calculate SPY equivalent value based on remaining SPY shares
    if (
        "SPY" in current_prices
        and current_prices["SPY"] is not None
        and spy_shares_held > 0
    ):
        spy_price = current_prices["SPY"]
        spy_value = spy_price * spy_shares_held
        spy_equivalent_value += spy_value

    # Calculate dollar returns
    portfolio_return_dollars = current_portfolio_value - capital_invested
    spy_return_dollars = spy_equivalent_value - capital_invested

    # Calculate alpha in dollars
    alpha_dollars = portfolio_return_dollars - spy_return_dollars

    return {
        "capital_invested": round(capital_invested, 2),
        "portfolio_return_dollars": round(portfolio_return_dollars, 2),
        "spy_return_dollars": round(spy_return_dollars, 2),
        "alpha_dollars": round(alpha_dollars, 2),
    }
