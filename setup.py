import imaplib
import email
import time
import os

# Email credentials
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("EMAIL_PASSWORD")
IMAP_SERVER = os.environ.get("IMAP_SERVER")


def check_email():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        _, data = mail.search(None, "UNSEEN")
        email_ids = data[0].split()

        for email_id in email_ids:
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject = msg["subject"]
            sender = msg["from"]

            print(f"\n📩 New email from {sender}: {subject}")

            # Extract the HTML body
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        print("HTML Body:\n", body)
                        break  # Stop at the first HTML part
            else:
                print("No HTML body found.")

        mail.logout()

    except Exception as e:
        print("Error checking email:", e)


# Run the script every 10 seconds
while True:
    check_email()
    time.sleep(10)
