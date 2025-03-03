import os
import imaplib
import email
import asyncio

from email_processor import process_email

# Email credentials
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("SERVICE_ROLE_API_KEY")
IMAP_SERVER = os.environ.get("IMAP_SERVER")


async def check_email():
    try:
        with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
            mail.login(EMAIL, PASSWORD)
            mail.select("inbox")
            _, messages = mail.search(None, "UNSEEN")
            if messages[0]:
                latest = messages[0].split()[-1]
                _, data = mail.fetch(latest, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        content = part.get_payload(decode=True).decode()
                        await process_email(content)
                        break
            else:
                print("No HTML body found.")

        mail.logout()

    except Exception:
        pass


async def main():
    while True:
        await check_email()
        await asyncio.sleep(5)


asyncio.run(main())
