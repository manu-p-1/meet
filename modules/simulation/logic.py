import json
from datetime import datetime, timedelta, timezone
from sys import stderr
import random
from models import Transaction, EmployeeCard
from sdk.ext import Authorization
import os
import requests as r
from server import client, mysql

MIDS = ['123456890', '111111', '524352', '123421']
INT_MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}


def department_alloc():
    conn = mysql.connect()
    cursor = conn.cursor()

    q = """
        SELECT amount, dest_token FROM transaction WHERE src_token = %s
    """
    cursor.execute(q, client.business.token)
    
    funds = cursor.fetchall()

    dept_amt = {}
    for f in funds:
        amt = float(f[0])
        dest = f[1]
        biz = client.client_sdk.businesses.find(token=dest)
        biz_name = biz.business_name_dba
        dept_amt[client.READABLE_DEPARTMENTS[biz_name]] = amt

    conn.close()
    return dept_amt


def department_utilization():
    conn = mysql.connect()
    cursor = conn.cursor()

    spending = {}
    q = """
        SELECT SUM(amount) AS total_spending FROM transaction WHERE src_token = %s
        GROUP BY src_token
    """

    for dept in client.departments:
        name = client.READABLE_DEPARTMENTS[dept.business_name_dba]
        cursor.execute(q, dept.token)
        spending[name] = float(cursor.fetchall()[0][0])

    conn.close()
    return spending


def simulate(card_token: str, amount: float, mid: str):
    payload = {
        'card_token': card_token,
        'amount': amount.__round__(2),
        'mid': mid
    }

    payload = json.dumps(payload)

    headers = {
        'Content-type': 'application/json',
    }

    resp = json.loads(r.post('https://sandbox-api.marqeta.com/v3/simulate/authorization', headers=headers,
                             data=payload, auth=(os.getenv('MY_APP'), os.getenv('MY_ACCESS'))).content)

    return Authorization(resp['transaction'])


def simulate_startup():
    conn = mysql.connect()
    cursor = conn.cursor()
    t = Transaction(cursor, conn)
    ec = EmployeeCard(cursor, conn)

    for dept, e_list in client.department_employees.items():

        dept_bal = client.retrieve_balance(
            dept).gpa.available_balance * (random.randint(1, 19) / 100)

        employees = random.sample(e_list, 5)

        for e in employees:
            transfer = client.transfer(
                dept_bal, dept, e, dest_token_is_user=True)
            t.insert(dept, e, Transaction.current_time(
                transfer.created_time), dept_bal)
            card = client.client_sdk.cards.list_for_user(e)[0].token

            mid_identifer = random.choice(MIDS)
            employee_transaction = simulate(
                card, amount=dept_bal * (random.randint(1, 19) / 100), mid=mid_identifer)

            t.insert(card, mid_identifer, Transaction.current_time(
                employee_transaction.created_time), employee_transaction.amount, is_card=True)
            ec.insert(e, card)

    conn.close()


def simulate_employee_plan(plan_id):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = '''SELECT e.token, ep_card_token FROM employee_plan ep JOIN employee e ON ep.ep_employee_FK = e.id WHERE ep_plan_FK = %s'''
    t = Transaction(cursor, conn=conn)

    # THIS WILL RETURN ALL EMPLOYEES AND THEIR ASSOCIATED CARDS WITH AN ACCORDING PLAN
    cursor.execute(query, (plan_id))
    for employee_card_pair in cursor.fetchall():
        mid_identifer = random.choice(MIDS)
        employee_token = employee_card_pair[0]
        card_token = employee_card_pair[1]
        # NEED TO FIND BALANCE OF THE USER AND TIMES THAT BY SOME PERCENTAGE
        e_balance = client.retrieve_balance(
            employee_token).gpa.available_balance * .1
        employee_transaction = simulate(
            card_token, amount=e_balance, mid=mid_identifer)
        t.insert(card_token, mid_identifer, Transaction.current_time(
            employee_transaction.created_time), employee_transaction.amount, is_card=True)

    conn.close()


def current_business_balance():
    bal = client.retrieve_balance(client.business.token)
    return {
        "available_balance": float(bal.gpa.available_balance),
        "ledger_balance": float(bal.gpa.ledger_balance)
    }


def department_balance(dept_code):
    for dept in client.departments:
        if dept.business_name_dba == dept_code:
            bal = client.retrieve_balance(dept.token)
            if bal:
                return {
                    "available_balance": float(bal.gpa.available_balance),
                    "ledger_balance": float(bal.gpa.ledger_balance)
                }
    raise Exception(
        "The department code passed matches to no known department")


def department_employee_count(dept_code):
    token = find_department_token(dept_code)

    if token is not None:
        for dept_token, e_list in client.department_employees.items():
            if dept_token == token:
                return len(e_list)

    raise Exception(
        "The department code passed matches to no known department")


def current_outgoing_transactions(dept_code):
    conn = mysql.connect()
    cursor = conn.cursor()

    token = find_department_token(dept_code)
    """
    Where the source token is the department token
    Get list of employees from client.department_employees given token
    Query db where src token is employee token
    """
    e_list = client.department_employees[token]

    now = time_now()
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    twenty_four_ago = (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    q = """SELECT SUM(amount) FROM transaction 
    WHERE src_token = %s AND create_time BETWEEN %s AND %s 
    GROUP BY src_token"""

    e_query = '''SELECT SUM(t.amount) FROM transaction t
    JOIN employee_card ec ON t.src_token = ec.ec_card_token
    WHERE ec.ec_employee_token = %s
    AND t.create_time BETWEEN %s AND %s
    '''

    amounts = []
    for e in e_list:
        cursor.execute(e_query, (e, twenty_four_ago, start_date))
        cf = cursor.fetchall()
        if cf[0][0] is not None:
            amounts.append(cf[0][0])

    cursor.execute(q, (token, twenty_four_ago, start_date))
    

    cf = cursor.fetchall()
    if len(cf) != 0:
        amounts.append(cf[0][0])

    tot = float(sum(amounts))
    conn.close()
    return {
        "number_transactions": len(amounts),
        "total": tot
    }


def active_plans():
    conn = mysql.connect()
    cursor = conn.cursor()

    now = time_now()
    now_time = now.strftime("%Y-%m-%d %H:%M:%S")

    q = """SELECT COUNT(id) FROM plan WHERE start_date >= %s AND end_date <= %s"""
    cursor.execute(q, (now_time, now_time))
    data = cursor.fetchall()[0][0]
    conn.close()
    return float(data)


def find_department_token(dept_code):
    for dept in client.departments:
        if dept.business_name_dba == dept_code:
            return dept.token
    return None


def department_employee__monthly_spending(dept_code):
    conn = mysql.connect()
    cursor = conn.cursor()

    """
    ID:
        NAME
        CURRENT_GPA_BAL
        MONTHLY SPENDING
    ID:
        NAME
        CURRENT_GPA_BAL
        MONTHLY SPENDING
    """

    employee_to_spending = {}
    dept_token = find_department_token(dept_code)

    now = time_now()
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")

    q = """SELECT e.id, first_name, last_name, e.token, t.amount FROM employee e
    JOIN employee_card ec on e.token = ec.ec_employee_token
    JOIN transaction t on src_token = ec.ec_card_token
    WHERE e.employee_dept_FK = %s
    AND t.create_time >= %s AND t.create_time <= %s"""

    cursor.execute(q, (dept_token, week_ago, start_date))
    cf = cursor.fetchall()

    # No need for length check because we are guaranteed first 5 people

    for record in cf:
        employee_to_spending[record[0]] = {
            "id": record[0],
            "name": record[1] + ' ' + record[2],
            "gpa_bal": client.retrieve_balance(record[3]).gpa.available_balance,
            "monthly_spending": float(record[4])
        }
    conn.close()
    return employee_to_spending


def generate_employee_spending_graph(dept_code):
    conn = mysql.connect()
    cursor = conn.cursor()
    dept_token = find_department_token(dept_code)

    now = time_now()
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    month_ago = (now - timedelta(days=31)).strftime("%Y-%m-%d %H:%M:%S")
    prev_month = (now - timedelta(days=62)).strftime("%Y-%m-%d %H:%M:%S")

    q = """SELECT sum(t.amount), day(t.create_time) as e_sum FROM employee e
    JOIN employee_card ec on e.token = ec.ec_employee_token
    JOIN transaction t on src_token = ec.ec_card_token
    WHERE e.employee_dept_FK = %s
    AND t.create_time >= %s AND t.create_time <= %s
    GROUP BY e_sum
    ORDER BY e_sum"""

    prev_query = """SELECT sum(t.amount), day(t.create_time) as e_sum FROM employee e
    JOIN employee_card ec on e.token = ec.ec_employee_token
    JOIN transaction t on src_token = ec.ec_card_token
    WHERE e.employee_dept_FK = %s
    AND t.create_time >= %s AND t.create_time <= %s
    GROUP BY e_sum
    ORDER BY e_sum"""

    cursor.execute(q, (dept_token, month_ago, start_date))
    cf = cursor.fetchall()

    employee_sum = {}

    for record in cf:
        employee_sum[record[1]] = float(record[0])

    prev_sum = {}

    cursor.execute(prev_query, (dept_token, prev_month, month_ago))
    cf = cursor.fetchall()

    for record in cf:
        prev_sum[record[1]] = float(record[0])

    conn.close()
    return {'current_month': employee_sum, 'previous_month': prev_sum}


def plan_avg_six_months(dept_code):
    conn = mysql.connect()
    cursor = conn.cursor()

    """
        January: {
            avg: 1515
        },
        February: {
            avg: 3256
        }
    
    """
    now = time_now()
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    six_months_ago = (now - timedelta(days=365 / 2)
                      ).strftime("%Y-%m-%d %H:%M:%S")

    q = """
        SELECT avg(funding_amount) AS avg, month(start_date) AS mstd FROM plan
        WHERE start_date BETWEEN %s AND %s
        AND source_fund_FK = (SELECT id FROM department_lookup WHERE department = %s)
        GROUP BY mstd
        ORDER BY mstd DESC;
    """

    cursor.execute(q, (six_months_ago, start_date, dept_code))
    cf = cursor.fetchall()

    plan_avg = {}

    for record in cf:
        plan_avg[INT_MONTHS[record[1]]] = {
            "avg": float(record[0])
        }
    conn.close()
    return plan_avg


def time_now():
    now = datetime.now(timezone.utc)
    return now
