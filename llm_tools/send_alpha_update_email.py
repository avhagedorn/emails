from email.mime.image import MIMEImage
import os
import smtplib
from pydantic import BaseModel, Field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("SERVICE_ROLE_API_KEY")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

HTML_CONTENT = """
<html>
<body>
    <h2>An Update on Your Investments</h2>
    <img src="cid:wojak">
    <p>With your recent purchase of {new_transaction_ticker}, your updated portfolio performance is shown.</p>
    <ul>
        <li><strong>Capital Invested:</strong> ${capital_invested}</li>
        <li><strong>Portfolio Return:</strong> ${portfolio_return_dollars}</li>
        <li><strong>SPY Return:</strong> ${spy_return_dollars}</li>
        <li><strong>Alpha:</strong> ${alpha_dollars}</li>
    </ul>
</body>
</html>
"""


class SendAlphaUpdateEmail(BaseModel):
    new_transaction_ticker: str = Field(
        ...,
        title="New transaction ticker",
        description="The ticker of the new transaction",
    )
    capital_invested: float = Field(
        ..., title="Capital invested", description="The total capital invested"
    )
    portfolio_return_dollars: float = Field(
        ...,
        title="Portfolio return dollars",
        description="The total return of the portfolio",
    )
    spy_return_dollars: float = Field(
        ..., title="SPY return dollars", description="The total return of the SPY index"
    )
    alpha_dollars: float = Field(
        ..., title="Alpha dollars", description="The alpha of the portfolio"
    )


async def send_alpha_update_email(args: SendAlphaUpdateEmail):
    try:
        content = HTML_CONTENT.format(
            new_transaction_ticker=args.new_transaction_ticker,
            capital_invested=args.capital_invested,
            portfolio_return_dollars=args.portfolio_return_dollars,
            spy_return_dollars=args.spy_return_dollars,
            alpha_dollars=args.alpha_dollars,
        )

        # Set up the MIME email
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = EMAIL
        msg["Subject"] = "Your Alpha Update"
        msg.attach(MIMEText(content, "html"))

        # Add Wojak image
        image_path = (
            "./attachments/green_wojak.jpeg"
            if args.alpha_dollars > 0
            else "./attachments/red_wojak.webp"
        )
        with open(image_path, "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header(
                "Content-ID", "<wojak>"
            )  # This ID matches the `cid` in the HTML
            img.add_header("Content-Disposition", "inline", filename="wojak")
            msg.attach(img)

        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, EMAIL, msg.as_string())
        server.quit()

        return "success"

    except Exception as e:
        raise e
        # print(e)
        # return "error"
