
from app.email_service import send_email

recipient = input("Enter your real Gmail address to receive a test email: ")

try:
    send_email(
        to_email=recipient,
        subject="Financial Portfolio Engine - Gmail Test",
        body="Congratulations! Your FastAPI project has successfully connected to Gmail API."
    )

    print("SUCCESS: Test email sent!")

except Exception as error:
    print("ERROR:", error)
