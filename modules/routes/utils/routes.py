import sys
from flask import Blueprint, render_template, request, jsonify, session
import json

from modules.decorators.utils import login_required
from modules.routes.utils.classes.class_utils import ManipulationType
from modules.routes.utils.functions.function_utils import is_active_plan, short_error, short_success
from server import mysql

util_bp = Blueprint('util_bp', __name__,
                    template_folder='templates', static_folder='static')


@util_bp.route('plans/find/department_employees/', methods=['GET'])
@login_required(session)
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

    conn.close()
    return json.dumps(e_payload)


@util_bp.route('plans/find/manage_plan/', methods=['GET'])
@login_required(session)
def manage_plan():
    print('entering route')
    conn = mysql.connect()
    cursor = conn.cursor()

    search_query = request.args.get('value')

    cursor.execute('SELECT * FROM PLAN where plan_name = %s', search_query)
    plan_data = cursor.fetchall()

    if len(plan_data) != 0:
        session['CURRENT_PLAN_EDIT'] = plan_data[0][0]

        headers = [desc[0] for desc in cursor.description]
        plan = zip(headers, plan_data[0])
        plan_fmt = {
            table_headers: val for (table_headers, val) in plan
        }

        cursor.execute('SELECT department FROM department_lookup WHERE id = %s', plan_fmt['dest_fund_FK'])

        plan_fmt['dest_fund_FK'] = cursor.fetchall()[0][0]
        plan_fmt['funding_amount'] = float("{:.2f}".format(float(plan_fmt['funding_amount'])))
        plan_fmt['start_date'] = plan_fmt['start_date'].strftime("%Y-%m-%d %H:%M")

        if plan_fmt['amount_limit'] is not None:
            plan_fmt['amount_limit'] = float("{:.2f}".format(float(plan_fmt['amount_limit'])))

        if plan_fmt['end_date'] is not None:
            plan_fmt['end_date'] = plan_fmt['end_date'].strftime("%Y-%m-%d %H:%M")

        plan_fmt['fund_individuals'] = True if int.from_bytes(plan_fmt['fund_individuals'], 'big') else False
        plan_fmt['is_active'] = True if is_active_plan(mysql, plan_fmt['plan_name']) else False

        employees_list = []
        if plan_fmt['fund_individuals']:
            get_employees_query = """
            SELECT id, CONCAT(first_name, ' ', last_name) AS name FROM employee 
            JOIN employee_plan ep on employee.id = ep.ep_employee_FK WHERE ep_plan_FK = %s
            """
            cursor.execute(get_employees_query, session['CURRENT_PLAN_EDIT'])
            cf = cursor.fetchall()
            for employee in cf:
                employees_list.append({
                    "id": employee[0],
                    "name": employee[1]
                })
        plan_fmt['employees_list'] = employees_list

        session['MANAGE_FORM'] = plan_fmt
        conn.close()

        return jsonify(
            response_status="success",
            active_status={
                "status": plan_fmt['is_active'],
                "info": None if not plan_fmt['is_active'] else render_template("plans/plan_info_partial.html",
                                                                               info_message="This plan is already "
                                                                                            "active "
                                                                                            "and cannot be modified. "
                                                                                            "It "
                                                                                            "can only "
                                                                                            "be deleted.")
            },
            response={
                "plan_name": plan_fmt['plan_name'],
                "funding_amount": plan_fmt['funding_amount'],
                "justification": plan_fmt['plan_justification'],
                "memo": plan_fmt['memo'],
                "start_date": plan_fmt['start_date'],
                "dest_fund": plan_fmt['dest_fund_FK'],
                "has_employee_specific": True if plan_fmt['fund_individuals'] else False,
                "employees_list": plan_fmt['employees_list'],
                "has_end_date": True if plan_fmt['end_date'] is not None else False,
                "end_date": plan_fmt['end_date'],
                "has_velocity_control": True if plan_fmt['control_name'] is not None else False,
                "control_name": plan_fmt['control_name'],
                "control_window": plan_fmt['control_window'],
                "amount_limit": plan_fmt['amount_limit'],
                "usage_limit": plan_fmt['usage_limit'],
                "priority": plan_fmt['priority']
            }
        )
    return short_error(err_list=['A plan with this name could not be found.'])


@util_bp.route('plans/find/delete_plan/', methods=['POST'])
@login_required(session)
def delete_plan():
    conn = mysql.connect()
    cursor = conn.cursor()

    q = """DELETE FROM employee_plan WHERE ep_plan_FK = %s"""
    q2 = """DELETE FROM plan WHERE id = %s"""

    try:
        cursor.execute(q, session['MANAGE_FORM']['id'])
        cursor.execute(q2, session['MANAGE_FORM']['id'])
        conn.commit()
        conn.close()
        return short_success(manip_type=ManipulationType.DELETED)

    except Exception as e:
        # An exception here shouldn't really occur, so log it
        conn.close()
        return short_error(err_list=['Something went wrong. Please try again.'])
