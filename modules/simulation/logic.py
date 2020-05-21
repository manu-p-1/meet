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
    print(client.business.token, file=stderr)
    cursor.execute(q, client.business.token)
    conn.close()
    funds = cursor.fetchall()

    dept_amt = {}
    for f in funds:
        amt = float(f[0])
        dest = f[1]
        biz = client.client_sdk.businesses.find(token=dest)
        biz_name = biz.business_name_dba
        for name in client.DEPT_MAPPINGS:
            if name[0] == biz_name:
                biz_name_readable = name[1]
                dept_amt[biz_name_readable] = amt

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
                             data=payload, auth=(os.environ['MY_APP'], os.environ['MY_ACCESS'])).content)

    return Authorization(resp['transaction'])


def simulate_startup():
    conn = mysql.connect()
    cursor = conn.cursor()
    t = Transaction(cursor, conn)
    ec = EmployeeCard(cursor, conn)

    for dept, e_list in client.department_employees.items():

        dept_bal = client.retrieve_balance(dept).gpa.available_balance * .1

        employees = random.sample(e_list, 5)

        for e in employees:
            transfer = client.transfer(
                dept_bal, dept, e, dest_token_is_user=True)
            t.insert(dept, e, Transaction.current_time(
                transfer.created_time), dept_bal)
            card = client.client_sdk.cards.list_for_user(e)[0].token

            mid_identifer = random.choice(MIDS)
            employee_transaction = simulate(
                card, amount=dept_bal * random.random(), mid=mid_identifer)

            t.insert(card, mid_identifer, Transaction.current_time(
                employee_transaction.created_time), employee_transaction.amount, is_card=True)
            ec.insert(e, card)

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
    raise Exception("Idiot. There isn't even a department with this name")


def department_employee_count(dept_code):
    token = find_department_token(dept_code)

    if token is not None:
        for dept_token, e_list in client.department_employees.items():
            if dept_token == token:
                return len(e_list)

    raise Exception("Idiot. There isn't even a department with this name")


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
        print(e, file=stderr)
        cursor.execute(e_query, (e, twenty_four_ago, start_date))
        cf = cursor.fetchall()
        print(cf, file=stderr)
        if cf[0][0] is not None:
            amounts.append(cf[0][0])

    cursor.execute(q, (token, twenty_four_ago, start_date))

    cf = cursor.fetchall()
    print(cf)
    if len(cf) != 0:
        amounts.append(cf[0][0])

    tot = float(sum(amounts))

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
    return float(cursor.fetchall()[0][0])


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
            "name": record[1] + ' ' + record[2],
            "current_gpa_bal": client.retrieve_balance(record[3]).gpa.available_balance,
            "weekly_spending": float(record[4])
        }

    return employee_to_spending


def plan_overview_six_months(dept_code):
    conn = mysql.connect()
    cursor = conn.cursor()

    now = time_now()
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    six_months_ago = (now - timedelta(days=365 / 2)).strftime("%Y-%m-%d %H:%M:%S")

    q = """
    SELECT plan_name, funding_amount, start_date FROM plan
    WHERE start_date BETWEEN %s AND %s
    AND source_fund_FK = (SELECT id FROM department_lookup WHERE department = %s)
    ORDER BY start_date DESC
    """

    cursor.execute(q, (six_months_ago, start_date, dept_code))
    cf = cursor.fetchall()

    plans_over_time = {}

    for record in cf:
        # time = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S')
        time = record[2]
        time_month = time.month
        if time_month not in plans_over_time:
            plans_over_time[time_month] = [{
                "plan_name": record[0],
                "funding_amount": float(record[1])
            }]
        else:
            plans_over_time[time_month].append({
                "plan_name": record[0],
                "funding_amount": float(record[1])
            })
    return plans_over_time


def time_now():
    now = datetime.now(timezone.utc)
    return now
