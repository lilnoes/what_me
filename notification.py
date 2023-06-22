from twilio.rest import Client
import os

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_ACCOUNT_TOKEN"]
FROM_NUMBER = os.environ["TWILIO_FROM_NUMBER"]
TO_NUMBER = os.environ["MY_NUMBER"]
client = Client(account_sid, auth_token)


def sendMessage(body):
    try:
        client.messages.create(
            from_=FROM_NUMBER,
            to=TO_NUMBER,
            body=body
        )

        print("Message sent")
    except Exception as e:
        print(f"Error sending message, Error: {e}")
