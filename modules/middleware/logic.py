from marqeta import Client
import json
import os

base_url = "https://sandbox-api.marqeta.com/v3/"
application_token = os.environ.get("MRC_APP_TOKEN")
access_token = os.environ.get("MRC_ACCESS_TOKEN")
timeout = 60  # seconds

client = Client(base_url, application_token, access_token, timeout)


def print_clients(clt=None):

    def v(i: str):
        print(json.dumps(json.loads(i), indent=4))

    # If you provide a client, it'll print the info, otherwise print all clients

    v(clt.__str__()) if clt is not None else [v(u.__str__()) for u in client.users.stream()]


def create_client(d: dict):
    client.users.create(d)


data = {
    "first_name": "Sam",
    "last_name": "Yuen"
}

data2 = {
    "first_name": "William",
    "last_name": "Vega"
}

data3 = {
    "first_name": "Yi-jian",
    "last_name": "Ma Ma"
}

data4 = {
    "first_name": "Manu",
    "last_name": "Puduvalli"
}

create_client(data)
create_client(data2)
create_client(data3)
create_client(data4)

# To find a user, provide a token

# user = client.users.find("USER_TOKEN")
# print_clients(user)

print_clients()