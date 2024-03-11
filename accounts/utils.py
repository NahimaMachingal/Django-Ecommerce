from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import random

def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp(phone_number, otp):
    # Initialize Twilio client with your Twilio credentials
    account_sid = 'ACdeeee9eb55fed23f66c5fe65254e2723'
    auth_token = '4d8c1853fc871e917804233acfc5d144'
    client = Client(account_sid, auth_token)

    # Send OTP via SMS using Twilio
    try:
        message = client.messages.create(
            body=f'Your OTP is: {otp}',
            from_='+15169630985',
            to=phone_number
        )
    
        print(f"OTP sent to {phone_number}: {message.sid}")
    except Exception as e:
        print(f"Error sending OTP to {phone_number}: {e}")
    