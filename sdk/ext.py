import json


class PeerTransfer:
    def __init__(self, response: dict):
        self.token = response['token']
        self.amount = response['amount']
        self.currency_code = response['currency_code']
        self.created_time = response['created_time']
        self.response = response
        if 'sender_user_token' not in response:
            self.sender_business_token = response['sender_business_token']
            self.recipient_business_token = response['recipient_business_token']
            self.recipient_user_token = None
        else:
            self.sender_business_token = response['sender_business_token']
            self.recipient_user_token = response['recipient_user_token']
            self.recipient_business_token = None
    def __str__(self):
        return json.dumps(self.response, indent=4)
