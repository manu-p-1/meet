from marqeta import Client
from server import mysql, client
import json
import os
import random

# open Client connection
def openClient():
    # Marqeta Client
    client_payload = {
        'base_url': "https://sandbox-api.marqeta.com/v3/",
        'application_token': os.environ['MY_APP'],
        'access_token': os.environ['MY_ACCESS'],
        'timeout': 60
    }
    client = Client(client_payload['base_url'], client_payload['application_token'],
                         client_payload['access_token'], client_payload['timeout'])
    return client

# executeOrders
# the plan_ids should be a list of plan ids, as stored in the db
# This will come from some func that queries the db for all
# past due and store them as a list
def executerOrders(plan_ids):
    # Implement: for-each over plan_ids, sorting them,
    # then sending each id to the appropriate func
    # (either dept_to_dept or dept_to_emp)


    #if(fund_individuals == False and completed == False) {
    #    # send plan to dep_to_dep order
    #} else {
    #    # send pan to dep_to_emps order
    #}

    pass


def dept_to_dept(plan_id):
    '''
    for department to department transfers,
    gathers info from plan in db and
    enters it into Marqet API

     param: plan_id - the id of the plan in db to submit
     returns: 1 on success 0 on faliure
    '''
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT * FROM plan WHERE id = %s'
    cursor.execute(query, plan_id)
    records = cursor.fetchall()

    id = records[0][0]
    plan_name = records[0][1]
    funding_amount = records[0][2]
    plan_justification = records[0][3]
    memo = records[0][4]
    start_date = records[0][5]
    end_date = records[0][6]
    source_fund_FK = records[0][7]
    dest_fund_FK = records[0][8]
    fund_individuals = records[0][9]
    control_name = records[0][10]
    control_window = records[0][11]
    amount_limit = records[0][12]
    usage_limit = records[0][13]
    complete = records[0][14]
    
    query = 'SELECT token FROM department_lookup WHERE id = %s'
    cursor.execute(query, source_fund_FK)
    source_token = cursor.fetchall()[0][0]

    query = 'SELECT token FROM department_lookup WHERE id = %s'
    cursor.execute(query, dest_fund_FK)
    dest_token = cursor.fetchall()[0][0]

    conn.commit()
    conn.close()

    transfer = client.transfer(funding_amount, source_token, dest_token, dest_token_is_user=False)

    #print(transfer)

def dept_to_emp(plan_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT * FROM plan WHERE id = %s'
    cursor.execute(query, plan_id)
    records = cursor.fetchall()

    id = records[0][0]
    plan_name = records[0][1]
    funding_amount = records[0][2]
    plan_justification = records[0][3]
    memo = records[0][4]
    start_date = records[0][5]
    end_date = records[0][6]
    source_fund_FK = records[0][7]
    dest_fund_FK = records[0][8]
    fund_individuals = records[0][9]
    control_name = records[0][10]
    control_window = records[0][11]
    amount_limit = records[0][12]
    usage_limit = records[0][13]
    complete = records[0][14]

    query = 'SELECT token FROM department_lookup WHERE id = %s'
    cursor.execute(query, source_fund_FK)
    source_token = cursor.fetchall()[0][0]

    query = 'SELECT * FROM employee_plan WHERE ep_plan_FK = %s'
    cursor.execute(query, plan_id)
    records = cursor.fetchall()

    for row in records:
        query = 'SELECT token FROM employee WHERE id = %s'
        cursor.execute(query, row[0])
        dest_token = cursor.fetchall()[0][0]
        transfer = client.transfer(funding_amount, source_token, dest_token, dest_token_is_user=True)
        #print(transfer)

    conn.commit()
    conn.close()

    # now we can make a function that adds cards based on the transfer (either here or from transaction table)


def complete_employee_plan(plan_id):
    conn = mysql.connect()
    cursor = conn.cursor()

    query = 'SELECT ep_employee_FK FROM employee_plan WHERE ep_plan_FK = %s'
    cursor.execute(query, plan_id)

    # list of employees IDs under a plan
    employee_ids = cursor.fetchall()

    query = 'SELECT token FROM employee WHERE id = %s'
    employee_tokens = []
    for eid in employee_ids:
        cursor.execute(query,eid[0])
        employee_tokens.append(cursor.fetchone()[0])

    for et in employee_tokens:
        card = client.client_sdk.cards.list_for_user(et)
        for c in card:
            print(c)
        break

