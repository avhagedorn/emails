import json
from langfuse.decorators import observe
from langfuse.openai import openai
from bs4 import BeautifulSoup

from llm_tools.handler import TOOLS, tool_handler

# TEST DATA
with open("./test_data/buy_googl.txt", "r") as f:
    buy_googl = f.read()
with open("./test_data/sell_schg.txt", "r") as f:
    sell_schg = f.read()

# CONSTS
MODEL = "gpt-4o-mini"
MAX_FUNCTION_CALLS = 10
SYSTEM_PROMPT = "You are an email assistant, tasked with parsing email content to analyze a user's brokerage transactions."
USER_PROMPT_BASE = """
Provided with a possible email from a brokerage account, please extract the transaction details.
Then get the current price of SPY on the date of the transaction, and save the transaction details and the price in a database. 
You will then calculate the updated portfolio alpha and send a portfolio update to the user.

---
EMAIL:

"""


@observe()
async def process_email(email_raw: str):
    # cut down on input tokens (idk what im doing)
    soup = BeautifulSoup(email_raw, "html.parser")
    email_text = soup.get_text()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_BASE + email_text},
    ]

    response = openai.chat.completions.create(
        model=MODEL,
        tools=TOOLS,
        messages=messages,
    )

    function_calls = 1
    while function_calls < MAX_FUNCTION_CALLS:
        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            break

        # more numbers to crunch
        messages.append(
            {"role": "assistant", "content": None, "tool_calls": tool_calls}
        )
        print(tool_calls)

        for tool_call in tool_calls:
            tool_result = await tool_handler(tool_call)
            print(tool_result)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

        response = openai.chat.completions.create(
            model=MODEL,
            tools=TOOLS,
            messages=messages,
        )
        function_calls += 1

    return response.choices[0].message.content


import asyncio


async def main():
    t = await process_email(buy_googl)
    print(t)


asyncio.run(main())
