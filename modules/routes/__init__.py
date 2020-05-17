from flask import session
from models import Employee
from server import client, mysql
from sys import stderr


def load_values():
    conn = mysql.connect()
    cursor = conn.cursor()
    print('\n\nINITIALIZING DB\n\n')

    query1 = """
        INSERT INTO department_lookup (token, department)
        VALUES (%s,%s)"""
    for i, dept in enumerate(client.departments):
        cursor.execute(query1, (dept.token, client.DEPARTMENT_LIST[i]))
        print(dept.token + ' has been inserted.', file=stderr)

    emp = Employee(cursor)
    for e in client.employees:
        emp.insert(e.token, e.first_name, e.last_name, e.parent_token)

    query3 = """
        INSERT INTO manager (email,pass,first_name,last_name,title,description,manager_dept_FK)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    for dept in client.DEPARTMENT_LIST:
        cursor.execute(query3, (
            client.MANAGERS[dept]['email'], client.MANAGERS[dept]['pass'], client.MANAGERS[dept]['first_name'],
            client.MANAGERS[dept]['last_name'], 'Sr. Division Manager', '', client.MANAGERS[dept]['manager_dept_FK']))
    session['db_init'] = True
    conn.commit()
