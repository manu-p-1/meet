class PeerTransfer:
    def __init__(self,response: dict):
        print(response)
    
        self.token = response['token']
        self.amount = response['amount']
        self.currency_code = response['currency_code']
        self.sender_business_token = response['sender_business_token']
        self.recipient_business_token = response['recipient_business_token']
        self.created_time = response['created_time']