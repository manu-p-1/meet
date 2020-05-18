class PeerTransfer:
    def __init__(self,response: dict):
        self.token = response['token']
        self.amount = response['amount']
        self.currency_code = response['currency_code']
        self.sender_user_token = response['sender_user_token']
        self.recipient_user_token = response['recipient_user_token']
        self.created_time = response['created_time']