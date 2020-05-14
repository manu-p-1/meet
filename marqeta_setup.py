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


class MarqetaClient:
    def __init__(self,db):
        # Fake data generator
        self.fake = Faker()
        self.db = db

        # Marqeta Client
        client_payload = {
            'base_url': "https://sandbox-api.marqeta.com/v3/",
            'application_token': os.environ['MY_APP'],
            'access_token': os.environ['MY_ACCESS'],
            'timeout': 60
        }
        self.client = Client(client_payload['base_url'], client_payload['application_token'],
                             client_payload['access_token'], client_payload['timeout'])

        # Constants
        self.DEPARTMENT_LIST = ['IT', 'ACCOUNTING', 'MARKETING', 'HUMAN_RESOURCES', 'PRODUCTION', 'RESEARCH',
                                'SECURITY',
                                'LOGISTICS']
        self.BUSINESS_NAME = self.fake.company()
        self.BUSINESS_TOKEN = ''.join(
            re.findall('([A-Z])', self.BUSINESS_NAME))

        self.TOKEN_COUNTER = 0
        self.DEPT_TOKEN_COUNTER = 0
        self.AH_GROUP_TOKEN_COUNTER = 0
        self.EMPLOYEE_TOKEN_COUNTER = 0

        self.FUNDING_PAYLOAD = {'name': self.BUSINESS_NAME + ' Program Funding',
                                'active': True,
                                'token': self.BUSINESS_TOKEN + '_FUNDING'
                                }

        self.BUSINESS_PAYLOAD = {'token': self.BUSINESS_TOKEN,
                                 'business_name_dba': self.BUSINESS_NAME,
                                 'general_business_description': self.fake.catch_phrase()
                                 }


        self.funding_source = []
        self.business = []
        self.departments = []
        self.ah_groups = []
        self.employees = []

        # self.setup()

    def setup(self):
        self.funding_source = self.create_program_funding_source(
            self.FUNDING_PAYLOAD)

        self.business = self.create_business(self.BUSINESS_PAYLOAD)

        self.fund(float(random.randint(100_000, 1_000_000)),
                  gpa_type='business', fund_source_token=self.funding_source.token,dest_token=self.business.token)

        self.departments = [self.create_department(
            dept) for dept in self.DEPARTMENT_LIST]

        self.ah_groups = [self.create_ah_group(
            dept) for dept in self.DEPARTMENT_LIST]

        for i, dept in enumerate(self.departments):
            self.generate_employee_data(12, self.departments[i].token, self.ah_groups[i].token)

    # HIERARCHY
    # CREATE PROGRAM FUNDING SOURCE

    def create_program_funding_source(self, fund):
        return self.client.funding_sources.program.create(fund)

    # CREATE BUSINESS USER
    def create_business(self, business):
        return self.client.businesses.create(business)

    # MAKE GPA ORDER TO BUSINESS
    def fund(self, amount: float, gpa_type: str, fund_source_token: str,dest_token: str, currency_code: str = 'USD'):
        payload = {'token': self.BUSINESS_TOKEN + '_GPA_TOKEN',
                   gpa_type + '_token': dest_token,
                   'funding_source_token': fund_source_token,
                   'amount': amount,
                   'currency_code': currency_code
                   }
        return self.client.gpa_orders.create(payload)

    # CREATE DEPARTMENT USERS (BUSINESSES)
    def create_department(self, department):
        dept_payload = {'token': self.BUSINESS_TOKEN + '_' + department + str(self.DEPT_TOKEN_COUNTER),
                        'business_name_dba': self.BUSINESS_TOKEN + '_' + department,
                        }
        print(f'dept_payload: {dept_payload}')
        self.DEPT_TOKEN_COUNTER += 1
        return self.client.businesses.create(dept_payload)

    # CREATE ACCOUNT HOLDER GROUPS FOR EACH DEPARTMENT
    # WITH APPROPRIATE CONFIG
    def create_ah_group(self, department):
        ah_group_payload = {
            'token': self.BUSINESS_TOKEN + '_' + department + '_AH_GROUP' + str(self.AH_GROUP_TOKEN_COUNTER),
            'name': self.BUSINESS_TOKEN + '_' + department + '_AH_GROUP'
        }
        print(f'ah_group_payload: {ah_group_payload}')
        self.AH_GROUP_TOKEN_COUNTER += 1
        return self.client.account_holder_groups.create(ah_group_payload)

        # CREATE USERS OF EACH DEPARTMENT WITH PARENT BEING THE DEPARTMENT USER TOKEN AND HAVING ACH TOKEN

    def create_employee(self, employee):
        return self.client.users.create(employee)

    def generate_employee_data(self, n: int, parent_token: str, ah_group_token: str):
        for count in range(n):
            e_payload = {
                "token": self.BUSINESS_TOKEN + '_e' + str(self.EMPLOYEE_TOKEN_COUNTER),
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "parent_token": parent_token,
                "account_holder_group_token": ah_group_token
            }
            self.EMPLOYEE_TOKEN_COUNTER += 1
            self.employees.append(self.create_employee(e_payload))

    # EXPORT BUSINESS DATA AS JSON OR JUST SUBMIT DIRECTLY TO MARQETA API

    def print_businesses(self, clt=None):

        def v(i: str):
            print(json.dumps(json.loads(i), indent=4))
            token = json.loads(i)['token']
            if len(token) < 9:
                print(token)

        v(clt.__str__()) if clt is not None else [
            v(u.__str__()) for u in self.client.businesses.stream()]

    def print_clients(self,clt=None):

        def v(i: str):
            print(json.dumps(json.loads(i), indent=4))
            # token = json.loads(i)['token']
            # print(client.balances.find_for_user_or_business(token))
        # If you provide a client, it'll print the info, otherwise print all clients

        v(clt.__str__()) if clt is not None else [v(u.__str__()) for u in self.client.users.stream()]

    def print_ah_groups(self,clt=None):

        def v(i: str):
            print(json.dumps(json.loads(i), indent=4))
            # token = json.loads(i)['token']
            # print(client.balances.find_for_user_or_business(token))
        # If you provide a client, it'll print the info, otherwise print all clients

        v(clt.__str__()) if clt is not None else [v(u.__str__()) for u in self.client.account_holder_groups.stream()]

    

    # def print_hierarchy(self):


# ESTABLISH THE DEPARTMENTS AS CONSTANTS/ACCOUNT HOLDER GROUPS

# FOR EACH DEPARTMENT/ACCOUNT HOLDER GROUP, CREATE A RANDOM AMOUNT OF USERS FOR EACH GROUP WHOSE PARENTS ARE THE BUSINESS

if __name__ == '__main__':
    # client = MarqetaClient()
    # client.print_businesses()
    # client.print_clients()
    # client.print_ah_groups()

