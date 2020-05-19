import json
from sys import stderr
import random
from models import Transaction
from server import client, mysql

MIDS = ['123456890','111111','524352','123421']


def department_alloc():
    conn = mysql.connect()
    cursor = conn.cursor()

    q = """
        SELECT amount, dest_token FROM transaction WHERE src_token = %s
    """
    print(client.business.token, file=stderr)
    cursor.execute(q, client.business.token)
    conn.close()
    return cursor.fetchall()


def department_utilization():
    conn = mysql.connect()
    cursor = conn.cursor()

    spending = {}
    q = """
        SELECT SUM(amount) AS total_spending FROM transaction WHERE src_token = %s
        GROUP BY src_token
    """

    for dept in client.departments:
        name = dept.business_name_dba
        cursor.execute(q, dept.token)
        spending[name] = cursor.fetchall()[0]

    conn.close()
    return spending


def simulate_startup():
    conn = mysql.connect()
    cursor = conn.cursor()
    t = Transaction(cursor, conn=conn)
    

    for dept, e_list in client.department_employees.items():
        print("Department --> ", dept, file=stderr)
        dept_balance = client.retrieve_balance(dept).gpa.available_balance * .1

        employees = random.sample(e_list, 5)

        for e in employees:
            print("Employeees --> ", e, file=stderr)
            transfer = client.transfer(dept_balance, dept, e, dest_token_is_user=True)
            t.insert(dept, e, Transaction.current_time(transfer.created_time), dept_balance)
            card = client.client_sdk.cards.list_for_user(e)[0].token
            print(type(card))
            print(f'card from marqeta --> {card}')
            mid_identifer = random.choice(MIDS)
            employee_transaction = client.simulate(card,amount=dept_balance*random.random(),mid=mid_identifer)
            print('printing employee transaction response')
            print(f'employee transaction --> {employee_transaction.response}')
            print('done')
            t.insert(card,mid_identifer,Transaction.current_time(employee_transaction.created_time),employee_transaction.amount)
            

    conn.close()
