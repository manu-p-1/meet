from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
import json
from server import mysql

util_bp = Blueprint('util_bp', __name__,
                    template_folder='templates', static_folder='static')


@util_bp.route('/department_employees/', methods=['GET'])
def overview(ctx=None):
    """
        Given a department (?department), return all the employees in that department
        {
            [
                {
                "name": "Firstname Lastname"
                "id": employeeID
                },

                {
                "name": "Firstname Lastname"
                "id": employeeID
                },

                {
                "name": "Firstname Lastname"
                "id": employeeID
                },
            ]
        }
    """

    conn = mysql.connect()
    cursor = conn.cursor()

    dept = request.args.get('department')[:2]
    name = request.args.get('term')
    query = '''SELECT token FROM department_lookup WHERE department = %s'''
    cursor.execute(query,(dept))
    dept_token = cursor.fetchall()[0][0]

    query = '''SELECT id, first_name, last_name FROM employee WHERE employee_dept_FK = %s'''
    cursor.execute(query,(dept_token))
    employee = cursor.fetchall()

    if name and ' ' in name:
        fname = name[:name.find(' ')].lower()
        lname = name[name.find(' '):].lower()
        e_payload = [{"name": e.first_name + ' ' + e.last_name, "id": e.id}
                     for e in employee if fname in e.first_name.lower() and lname in e.last_name.lower()]
    else:
        name = name.lower()
        e_payload = [{"name": e.first_name + ' ' + e.last_name, "id": e.id}
                     for e in employee if name in e.first_name.lower() or name in e.last_name.lower()]

    print(json.dumps(e_payload))

    return json.dumps(e_payload)
