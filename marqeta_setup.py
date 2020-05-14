from faker import Faker
from marqeta import Client
import re
import json
import random
import os


'''
HIERARCHY

BUSINESS_TOKEN
    DEPT_TOKEN1
        AH_GROUP_TOKEN1
            EMPLOYEE_TOKEN1
            EMPLOYEE_TOKEN2
            EMPLOYEE_TOKEN3
    DEPT_TOKEN2
        AH_GROUP_TOKEN2
            EMPLOYEE_TOKEN1
            EMPLOYEE_TOKEN2
            EMPLOYEE_TOKEN3
'''

'''
Each user will have their own MarqetaClient instance.
'''
class MarqetaClient():
    def init(self):
        self.fake = Faker()

        client_payload = {
            'base_url': "https://sandbox-api.marqeta.com/v3/",
            'application_token': os.environ['MY_APP'],
            'access_token': os.environ['MY_ACCESS'],
            'timeout': 60
        }
        self.client = Client(client_payload['base_url'], client_payload['application_token'],
                             client_payload['access_token'], client_payload['timeout'])

        self.DEPARTMENTS = ['IT', 'ACCOUNTING', 'MARKETING', 'HUMAN RESOURCES', 'PRODUCTION', 'RESEARCH', 'SECURITY',
                    'LOGISTICS']
        self.BUSINESS_NAME = self.fake.company()
        self.BUSINESS_TOKEN = ''.join(re.findall('([A-Z])', BUSINESS_NAME))
        self.TOKEN_COUNTER = 0

        self.FUNDING_PAYLOAD = {'name': BUSINESS_NAME + ' Program Funding',
                        'active': True,
                        'token': BUSINESS_TOKEN + '_FUNDING'
                        }

        self.BUSINESS_PAYLOAD = {'token': BUSINESS_TOKEN + str(TOKEN_COUNTER),
                            'business_name_dba': BUSINESS_NAME,
                            'general_business_description': self.fake.catch_phrase()
                            }

        self.BUSINESS_GPA_PAYLOAD = {'token': BUSINESS_TOKEN + '_GPA_TOKEN',
                                'business_token': '',
                                'amount': ''
                                }

    def setup(self):
        pass

    # HIERARCHY
    # CREATE PROGRAM FUNDING SOURCE
    def create_program_funding_source(self, fund: list):
        for payload in fund:
            self.client.funding_sources.program.create(payload)

    # CREATE BUSINESS USER
    def create_business(self, business: list = []):
        for b in business:
            self.client.businesses.create(b)

    # MAKE GPA ORDER TO BUSINESS
    def fund(self, amount: float, gpa_type: str, dest_token: str, currency_code: str = 'USD'):
        payload = {'token': BUSINESS_TOKEN + '_GPA_TOKEN',
                   gpa_type + '_token': dest_token,
                   'amount': amount,
                   'currency_code': currency_code
                   }
        self.client.gpa_orders.create(payload)

    # CREATE DEPARTMENT USERS (BUSINESSES)
    def create_department(self, department: list = []):
        for d in department:
            DEPARTMENT_PAYLOAD = {'token': BUSINESS_TOKEN + '_' + d + str(TOKEN_COUNTER),
                                  'business_name_dba': BUSINESS_TOKEN + '_' + d,
                                  }
            self.client.businesses.create(DEPARTMENT_PAYLOAD)

    # CREATE ACCOUNT HOLDER GROUPS FOR EACH DEPARTMENT
    # WITH APPROPRIATE CONFIG
    def create_ah_group(self, department: list = []):
        for d in department:
            AH_GROUP_PAYLOAD = {'token': BUSINESS_TOKEN + '_' + d + 'AH_GROUP' + str(TOKEN_COUNTER),
                                'name': BUSINESS_TOKEN + '_' + d + 'AH_GROUP'
                                }
            self.client.businesses.create(AH_GROUP_PAYLOAD)

        # CREATE USERS OF EACH DEPARTMENT WITH PARENT BEING THE DEPARTMENT USER TOKEN AND HAVING ACH TOKEN
    def create_employee(self, employee: list = []):
        for e in employee:
            self.client.users.create(e)
    def generate_employee_data(self, n: int, user_token: str, parent_token: str):
        return [
            {"token": str(BUSINESS_TOKEN + 1),
             "first_name": fake.first_name(),
             "last_nane": fake.last_name(),
             "parent_token": parent_token,
             "account_holder_group_token": None
             }
            for n in range(n)
        ]

    # EXPORT BUSINESS DATA AS JSON OR JUST SUBMIT DIRECTLY TO MARQETA API
    def print_businesses(self, clt=None):

        def v(i: str):
            print(json.dumps(json.loads(i), indent=4))
            token = json.loads(i)['token']
            if len(token) < 9:
                print(token)

        v(clt.__str__()) if clt is not None else [
            v(u.__str__()) for u in self.client.businesses.stream()]


# ESTABLISH THE DEPARTMENTS AS CONSTANTS/ACCOUNT HOLDER GROUPS

# FOR EACH DEPARTMENT/ACCOUNT HOLDER GROUP, CREATE A RANDOM AMOUNT OF USERS FOR EACH GROUP WHOSE PARENTS ARE THE BUSINESS
