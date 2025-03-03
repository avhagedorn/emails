import json
import re
from pydantic import BaseModel, Field


class ExtractTransaction(BaseModel):
    freetext: str = Field(
        ...,
        title="Transaction text raw",
        description="The text for which to extract the trading activity",
    )


async def extract_transaction(freetext: ExtractTransaction):
    try:
        text = freetext.freetext
        pattern = re.compile(
            r"Your order to (?P<action>buy|sell) "
            r"(?P<quantity>\d+\.?\d*) shares of (?P<ticker>\w+) "
            r".*?at an average price of \$(?P<price>\d+\.\d+) "
            r"on (?P<date>[A-Za-z]+ \d{1,2}, \d{4})"
        )
        if match := pattern.search(text):
            return json.dumps(match.groupdict())
    except Exception as e:
        print(e)
        raise e
        # return "error"
