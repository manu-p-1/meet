import sys

from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
import json
from server import mysql, client
from modules.routes.utils.forms import get_plan_form
from models import Plan
from datetime import datetime, timezone

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

    dept = request.args.get('department')
    name = request.args.get('term')

    if dept is None or name is None:
        return jsonify(query_error=True)

    query = '''SELECT token FROM department_lookup WHERE department = %s'''
    cursor.execute(query, dept)
    dept_token = cursor.fetchall()[0][0]

    query = '''SELECT id, first_name, last_name FROM employee WHERE employee_dept_FK = %s'''
    cursor.execute(query, dept_token)
    employee = cursor.fetchall()

    print(employee, file=sys.stderr)

    if name and ' ' in name:
        fname = name[:name.find(' ')].lower()
        lname = name[name.find(' '):].lower()
        e_payload = [
            {"name": f'{e[1]} {e[2]}', "id": e[0]} for e in employee if fname in e[1] and lname in e[2]
        ]
    else:
        name = name.lower()
        e_payload = [
            {"name": f'{e[1]} {e[2]}', "id": e[0]}
            for e in employee if name in e[1].lower() or name in e[2].lower()
        ]

    print(json.dumps(e_payload))

    return json.dumps(e_payload)


@util_bp.route('/manage_plan/', methods=['GET', 'POST'])
def manage_plan():

    print('entering route')
    conn = mysql.connect()
    cursor = conn.cursor()

    fund_choices = client.DEPT_MAPPINGS

    search_query = request.args.get('value')

    cursor.execute('SELECT * FROM PLAN where plan_name = %s',(search_query))
    plan_data = cursor.fetchall()

    print(plan_data)

    if len(plan_data) != 0:
        session['CURRENT_PLAN_EDIT'] = plan_data[0][0]
        

        headers = [desc[0] for desc in cursor.description]
        plan = zip(headers,plan_data[0])
        formatted_plan ={table_headers: val for (
                table_headers, val) in plan}
        print(formatted_plan)

        dept_code_query = cursor.execute(
            'SELECT department FROM department_lookup WHERE id = %s', formatted_plan['dest_fund_FK'])

        conn.close()
        formatted_plan['dest_fund_FK'] = cursor.fetchall()[0][0]
        formatted_plan['funding_amount'] = float(formatted_plan['funding_amount'])

        form = get_plan_form(formatted_plan, session, fund_choices)
        session['MANAGE_FORM'] = formatted_plan
        print(form)
        print('returning correctly')
        return render_template('plan_form_partial.html', form=form)

    return ''
