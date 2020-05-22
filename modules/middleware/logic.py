from marqeta import Client
from server import mysql, client
from datetime import datetime
from models import EmployeeCard, Transaction
import json
import os
import random
from modules.simulation.logic import simulate_employee_plan, MIDS
from apscheduler.schedulers.background import BackgroundScheduler
import time
import atexit

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


def createBackgroundScheduler():
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(func=executeOrders, trigger="interval", seconds=10)
    scheduler.start()
    print("!!!@@@               Running Backgroun Scheduler @@@                 !!!")
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

# executeOrders
# the plan_ids should be a list of plan ids, as stored in the db
# This will come from some func that queries the db for all
# past due and store them as a list
def executeOrders():
    #print("Executing Orders")
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT id, fund_individuals FROM plan WHERE start_date < NOW() AND complete = 0'
    cursor.execute(query)
    records = cursor.fetchall()

    if records and records[0][0]:
        for row in records:
            plan_id = row[0]
            fund_individuals = row[1]
            print(row)
            print(fund_individuals)
            if fund_individuals:
                dept_to_emp(plan_id)
            else:
                dept_to_dept(plan_id)

    conn.commit()
    conn.close()


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

    transfer = client.transfer(funding_amount, source_token, dest_token, dest_token_is_user=False)
    
    t = Transaction(cursor,conn=conn)
    t.insert(source_token,dest_token,Transaction.current_time(transfer.created_time),funding_amount)

    query = 'UPDATE plan SET complete = 1 WHERE id = %s'
    cursor.execute(query, plan_id)

    conn.commit()
    conn.close()

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

    t = Transaction(cursor,conn)

    for row in records:
        query = 'SELECT token FROM employee WHERE id = %s'
        cursor.execute(query, row[0])
        dest_token = cursor.fetchall()[0][0]
        transfer = client.transfer(funding_amount, source_token, dest_token, dest_token_is_user=True)
        t.insert(source_token,dest_token,Transaction.current_time(transfer.created_time),funding_amount)

    conn.commit()
    conn.close()

    complete_employee_plan(plan_id)
    #simulate_employee_plan(plan_id)


def complete_employee_plan(plan_id):
    conn = mysql.connect()
    cursor = conn.cursor()

    query = 'SELECT ep_employee_FK FROM employee_plan WHERE ep_plan_FK = %s'
    cursor.execute(query, plan_id)

    # list of employees IDs under a plan
    employee_ids = cursor.fetchall()

    query = 'SELECT start_date, end_date FROM plan WHERE id = %s'
    cursor.execute(query, plan_id)
    records = cursor.fetchall()
    # start date
    start_date = records[0][0]
    # end date
    end_date = records[0][1]

    # get the days between
    if end_date:
        delta = (end_date) - (start_date)
        days = delta.days

    query = 'SELECT token FROM employee WHERE id = %s'
    employee_tokens = []
    for eid in employee_ids:
        cursor.execute(query,eid[0])
        employee_tokens.append(cursor.fetchone()[0])

    
    for et in employee_tokens:
        payload = {
            'user_token': et,
            'card_product_token': os.environ['SAM_CARD_PRODUCT_TOKEN'],
        }
        
        if end_date:
            payload['expiration_offset'] = {
                "unit": "DAYS",
                "value": days
            }
        ec = EmployeeCard(cursor, conn, True)
        card = client.client_sdk.cards.create(payload)
        ec.insert(et, card.token)

    query = 'UPDATE plan SET complete = 1 WHERE id = %s'
    cursor.execute(query, plan_id)

    conn.commit()
    conn.close()