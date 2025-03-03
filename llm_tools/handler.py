import json
from openai import pydantic_function_tool

from llm_tools.get_portolio_alpha import GetPortfolioAlpha, get_portfolio_alpha
from llm_tools.save_transaction import SaveTransaction, save_transaction
from llm_tools.extract_transaction import ExtractTransaction, extract_transaction
from llm_tools.get_stock_or_index_price import (
    GetStockOrIndexPrice,
    get_stock_or_index_price,
)

TOOLS = [
    pydantic_function_tool(SaveTransaction),
    pydantic_function_tool(ExtractTransaction),
    pydantic_function_tool(GetStockOrIndexPrice),
    pydantic_function_tool(GetPortfolioAlpha),
]

FUNCTIONS = {
    SaveTransaction: save_transaction,
    ExtractTransaction: extract_transaction,
    GetStockOrIndexPrice: get_stock_or_index_price,
    GetPortfolioAlpha: get_portfolio_alpha,
}


async def tool_handler(tool_call):
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    print(f"Calling {function_name}...")

    for function, handler in FUNCTIONS.items():
        if function.__name__ == function_name:
            function_args = function(**function_args)
            return await handler(function_args)
    return "Unknown function"
