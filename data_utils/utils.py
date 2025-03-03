from data_utils.db import get_connection


async def db_save_transaction(
    ticker: str,
    shares: float,
    price: float,
    equivalent_spy_shares: float,
    year: int,
    month: int,
    day: int,
    transaction_is_buy: bool,
) -> dict:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO transactions 
                    (ticker, shares, price, equivalent_spy_shares, year, month, day, transaction_is_buy) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """,
                (
                    ticker,
                    shares,
                    price,
                    equivalent_spy_shares,
                    year,
                    month,
                    day,
                    transaction_is_buy,
                ),
            )
            connection.commit()
            result = cursor.fetchone()
            return {"id": result[0] if result else None}


# Get transactions from database
async def db_get_transactions():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM transactions ORDER BY year, month, day")
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            transactions = [dict(zip(columns, row)) for row in results]
            return {"transactions": transactions}
