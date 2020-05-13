import os
import sys
from packaging import version
from urllib.parse import quote_plus
from faker import Faker
from marqeta import Client
import re
import json
import random

def load_env(dbu, dbpw):

    ver = ".".join(map(str, sys.version_info[:3]))
    if version.parse(ver) < version.parse("3.7.5"):
        print(f"PYTHON VERSION IS {ver} BUT REQUIRES 3.7.5 OR HIGHER")
        exit(1)

    if os.environ.get("ALCHEMY_URI") is None:
        os.environ['ALCHEMY_URI'] = f"mysql://{dbu}:%s@localhost/mrcdb" % quote_plus(dbpw)
        print('Exported ALCHEMY_URI\n')

'''
Configuration settings to be used on localhost.
'''
class DevelopmentConfig:
    # SERVER RELOAD ON CODE CHANGE
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

    #MySQL setup
    MYSQL_DATABASE_USER = os.environ['DB_USER']
    MYSQL_DATABASE_PASSWORD = os.environ['DB_PASS']
    MYSQL_DATABASE_DB = os.environ.get('DB')
    MYSQL_DATABASE_HOST = os.environ.get('DB_HOST')

    load_env(dbu=MYSQL_DATABASE_USER, dbpw=MYSQL_DATABASE_PASSWORD)

    SQLALCHEMY_DATABASE_URI = os.environ.get('ALCHEMY_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

'''
Configuration settings to be used on PythonAnywhere.
'''
class ProductionConfig:
    # SERVER RELOAD ON CODE CHANGE
    DEBUG = False

    #MySQL setup
    MYSQL_DATABASE_USER = os.environ['DB_USER']
    MYSQL_DATABASE_PASSWORD = os.environ['DB_PASS']
    MYSQL_DATABASE_DB = os.environ.get('DB')
    MYSQL_DATABASE_HOST = os.environ.get('DB_HOST')


if __name__ == '__main__':
    fake = Faker()

    base_url = "https://sandbox-api.marqeta.com/v3/"
    # application_token = os.environ['MRC_APP_TOKEN']
    # access_token = os.environ['MRC_ACCESS_TOKEN']
    application_token = os.environ['MY_APP']
    access_token = os.environ['MY_ACCESS']
    timeout = 60 # seconds

    client = Client(base_url, application_token, access_token, timeout)
    
    DEPARTMENTS = ['IT','ACCOUNTING','MARKETING','HUMAN RESOURCES','PRODUCTION','RESEARCH','SECURITY','LOGISTICS']
    BUSINESS_NAME = fake.company()
    BUSINESS_TOKEN = ''.join(re.findall('([A-Z])',BUSINESS_NAME))
    TOKEN_COUNTER = 0

    
    FUNDING_PAYLOAD = {'name':BUSINESS_NAME+' Program Funding',
                        'active': True,
                        'token':BUSINESS_TOKEN+'_FUNDING'
                        }

    BUSINESS_PAYLOAD = {'token':BUSINESS_TOKEN+str(TOKEN_COUNTER),
                        'business_name_dba':BUSINESS_NAME,
                        'general_business_description':fake.catch_phrase()
                        }

    BUSINESS_GPA_PAYLOAD = {'token':BUSINESS_TOKEN+'_GPA_TOKEN',
                            'business_token':'',
                            'amount':  ''
                            }

    


    
    # HIERARCHY
    # CREATE PROGRAM FUNDING SOURCE
    def create_program_funding_source(fund: list):
        for payload in fund:
            client.funding_sources.program.create(payload)

    # CREATE BUSINESS USER
    def create_business(business: list = []):
        for b in business:
            client.businesses.create(b)

    # MAKE GPA ORDER TO BUSINESS
    def fund(amount: float, gpa_type: str, dest_token:str,currency_code: str = 'USD'):
        payload = {'token':BUSINESS_TOKEN+'_GPA_TOKEN',
                    gpa_type+'_token':dest_token,
                    'amount': amount,
                    'currency_code': currency_code
                    }
        client.gpa_orders.create(payload)


    # CREATE DEPARTMENT USERS (BUSINESSES)
    def create_department(department: list=[]):
        for d in department:
            DEPARTMENT_PAYLOAD = {'token':BUSINESS_TOKEN+'_'+d+str(TOKEN_COUNTER),
                                'business_name_dba':BUSINESS_TOKEN+'_'+d,
                                }
            client.businesses.create(DEPARTMENT_PAYLOAD)

    # CREATE ACCOUNT HOLDER GROUPS FOR EACH DEPARTMENT
    # WITH APPROPRIATE CONFIG
    def create_ah_group(department: list=[]):
        for d in department:
            AH_GROUP_PAYLOAD = {'token':BUSINESS_TOKEN+'_'+d+'AH_GROUP'+str(TOKEN_COUNTER),
                                'name':BUSINESS_TOKEN+'_'+d+'AH_GROUP'
                                }
            client.businesses.create(AH_GROUP_PAYLOAD)

    # CREATE USERS OF EACH DEPARTMENT WITH PARENT BEING THE DEPARTMENT USER TOKEN AND HAVING ACH TOKEN

    

    # EXPORT BUSINESS DATA AS JSON OR JUST SUBMIT DIRECTLY TO MARQETA API


    def print_businesses(clt=None):

        def v(i: str):
            print(json.dumps(json.loads(i), indent=4))
            token = json.loads(i)['token']
            if len(token) < 9:
                print(token)

        v(clt.__str__()) if clt is not None else [v(u.__str__()) for u in client.businesses.stream()]

    

    def create_employee(employee: list = []):
        for e in employee:
            client.users.create(e)
    
    def generate_employee_data(n: int,user_token: str,parent_token: str):
        return [
            {"token":str(BUSINESS_TOKEN+1),
            "first_name": fake.first_name(),
            "last_nane": fake.last_name(),
            "parent_token":parent_token,
            "account_holder_group_token":None
            }
            for n in range(n)
        ]

    def create_account_holder_group(department_token: str,department_name: list):
        pass

    # def 


    

    print_businesses()


    # ESTABLISH THE DEPARTMENTS AS CONSTANTS/ACCOUNT HOLDER GROUPS

    # FOR EACH DEPARTMENT/ACCOUNT HOLDER GROUP, CREATE A RANDOM AMOUNT OF USERS FOR EACH GROUP WHOSE PARENTS ARE THE BUSINESS