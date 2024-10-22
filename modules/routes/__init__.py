from flask import session

from models import Employee, Manager, Transaction
from server import client, mysql
from sys import stderr

from modules.middleware.logic import create_background_scheduler
from modules.simulation.logic import simulate_startup


def load_values():
    conn = mysql.connect()
    cursor = conn.cursor()
    print('\n\nINITIALIZING DB\n\n')

    query1 = """
        INSERT INTO department_lookup (token, department)
        VALUES (%s,%s)"""
    for i, dept in enumerate(client.departments):
        cursor.execute(query1, (dept.token, client.DEPARTMENT_LIST[i]))
        print(dept.token + client.DEPARTMENT_LIST[i] + ' has been inserted.', file=stderr)

    emp = Employee(cursor, conn, immediate_commit=False)
    for e in client.employees:
        emp.insert(e.token, e.first_name, e.last_name, e.parent_token)
        print(e.token + 'h has been inserted.', file=stderr)

    desc = "My primary role is managing different banking sectors involved in asset management, sanctioning loans, " \
           "mortgages, investments, and account operations. I oversee the efficient day to day processes as well as " \
           "preparing forecasts and reports to drive the overall success of our clients and the department. "

    man = Manager(cursor, conn, immediate_commit=False)
    for dept in client.DEPARTMENT_LIST:
        man.insert(
            client.MANAGERS[dept]['email'],
            client.MANAGERS[dept]['pass'],
            client.MANAGERS[dept]['first_name'],
            client.MANAGERS[dept]['last_name'],
            'Sr. Division Manager',
            desc,
            client.MANAGERS[dept]['manager_dept_FK'],
            client.MANAGERS[dept]['gender'])

    trans = Transaction(cursor, conn, immediate_commit=False)
    for t in client.transactions:
        if t.recipient_user_token is None:
            trans.insert(
                t.sender_business_token,
                t.recipient_business_token,
                Transaction.current_time(t.created_time),
                t.amount,
            )
        else:
            trans.insert(
                t.sender_business_token,
                t.recipient_user_token,
                Transaction.current_time(t.created_time),
                t.amount,
            )
    conn.commit()
    conn.close()
    simulate_startup()
    session['db_init'] = True

    create_background_scheduler()
