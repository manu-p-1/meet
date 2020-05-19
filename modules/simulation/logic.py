import json
from sys import stderr

from server import client, mysql


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
