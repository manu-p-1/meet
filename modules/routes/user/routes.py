import datetime
from typing import List, Dict, Union

from models import Plan
from modules.routes.user.custom_fields import EmployeeInfoTextAreaField, ISimpleEmployee
from modules.routes.utils.classes.class_utils import ManipulationType, OperationType, SupportedTimeFormats
from modules.routes.utils.functions.function_utils import is_duplicate_plan, short_error, short_success, \
    find_all_employees, custom_strftime, is_expired_plan
from server import mysql
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from modules.routes.user.forms import create_plan_form, get_plan_form, Forminator
from modules.decorators.utils import login_required
from modules.middleware.logic import execute_orders

user_bp = Blueprint('user_bp', __name__,
                    template_folder='templates', static_folder='static')


@user_bp.route('/overview/', methods=['GET'])
@login_required(session)
def overview(ctx=None):
    return render_template('overview/dash_overview_partial.html')


@user_bp.route('/profile/', methods=['GET', 'POST'])
@login_required(session)
def profile(ctx=None):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT description FROM manager WHERE email = %s'
    cursor.execute(query, (session['manager_email']))
    description = cursor.fetchall()[0][0]

    conn.close()

    if description is None or description.strip() == '':
        description = "None Provided"

    return render_template('profile/profile.html', description=description)


@user_bp.route('/logout/', methods=['GET'])
@login_required(session)
def logout(ctx=None):
    session.clear()
    flash("Logout Successful", category='success')
    return redirect(url_for('common_bp.login'))


@user_bp.route('/create_plan/', methods=['GET', 'POST'])
@login_required(session)
def create_plan():
    form = create_plan_form(session)

    if request.method == 'GET':
        return render_template('plans/create_plan/create_plan_partial.html', form=form,
                               current_date=custom_strftime(SupportedTimeFormats.FMT_SIDE_UI, datetime.now()))
    else:
        if form.validate_on_submit():
            conn = mysql.connect()
            cursor = conn.cursor()
            return create_plan_execution(conn, cursor, Forminator(form))
        else:
            return short_error(form)


def create_plan_execution(conn, cursor, fmr: Forminator):
    if is_duplicate_plan(mysql, fmr.plan_name):
        return short_error(err_list=['This plan already exists. Go to Manage Plan to learn more.'])

    if fmr.disbursement_type == fmr.raw_form.DISB_ALL:
        employees = find_all_employees(cursor, session['manager_dept'])

        if employees is None:
            return short_error(err_list=['No employees were found in the department'])
        fmr.employees_list = employees['data']

    p = Plan(cursor, conn=conn)
    p.insert(fmr)
    conn.close()

    execute_orders()
    return short_success(ManipulationType.CREATED)


@user_bp.route('/manage_plan/', methods=['GET', 'POST'])
@login_required(session)
def manage_plan():

    form = get_plan_form(session)

    if request.method == 'GET':
        return render_template('plans/manage_plan/manage_plan_partial.html', form=form,
                               current_date=custom_strftime(SupportedTimeFormats.FMT_SIDE_UI, datetime.now()))
    else:
        plan_fmt = session.get('MANAGE_FORM')

        if plan_fmt is None:
            return jsonify(response="A search query must be made to update it")

        form = get_plan_form(session)

        if form.validate_on_submit():
            conn = mysql.connect()
            cursor = conn.cursor()
            return manipulate_plan(conn, cursor, Forminator(form), plan_fmt)
        else:
            return short_error(form=form)


def manipulate_plan(conn, cursor, fmr, plan_fmt):

    if plan_fmt['plan_name'] != fmr.plan_name:
        if is_duplicate_plan(mysql, fmr.plan_name):
            return short_error(err_list=['This plan is already exists'])

    if plan_fmt['is_active']:
        return short_error(err_list=['This plan is currently active'])

    if is_expired_plan(mysql, fmr.plan_name):
        return short_error(err_list=['This plan is expired and is read-only.'])

    p = Plan(cursor, conn=conn)
    p.update(fmr, plan_fmt['id'])

    q_del = """DELETE FROM employee_plan WHERE ep_employee_FK = %s AND ep_plan_FK = %s"""
    q_ins = """INSERT INTO employee_plan(ep_employee_FK, ep_plan_FK) VALUES (%s, %s)"""
    uq = get_unique_employees(plan_fmt['employees_list'], fmr.employees_list)

    if uq['operation'] == OperationType.DELETE_EMPLOYEE:
        [cursor.execute(q_del, (record['id'], plan_fmt['id'])) for record in uq['diff_list']]
    else:
        [cursor.execute(q_ins, (record['id'], plan_fmt['id'])) for record in uq['diff_list']]

    conn.commit()
    conn.close()
    return short_success(ManipulationType.UPDATED)


def get_unique_employees(old_list, new_list: List[EmployeeInfoTextAreaField]) -> Dict[str, Union[List[dict],
                                                                                                 OperationType]]:
    """
    We get the old list of employees as a list of dictionaries and a new list of employees as
    a list of EmployeeInfoTextAreaField's from the form. The issue is a bit tricky because
    it becomes hard to tell when a user added or removed employees. It's very naive to rely on the
    length of the two lists.

    For example, let's say the manager removed the following employees

    x = [{"Manu": 1}, {"Sam": 2}, {"Will": 3}, {"Yijian": 4}]

    and added new ones:

    y = [{"Jack": 1}, {"Jill": 2}, {"Bill": 3}, {"Dill": 4}]

    How would you keep track of what employees were to be removed?

    Another example, If the manager adds to new employees

    y = [{"Manu": 1}, {"Sam": 2}, {"Will": 3}, {"Yijian": 4}, {"Aang": 5}, {"Appa": 10}]

    How would you figure out which ones were added? What if they were removed?

    y = [{"Manu": 1}, {"Sam": 2}, {"Will": 3}]

    Enter sets. https://docs.python.org/2/library/sets.html#set-objects
    We can convert each dictionary and group them as a set. Initially, we
    take the difference between the new and old set. If the result is an empty set, it could mean that new employees
    were added. In this case, we check the length of the new list and take the systematic difference of both sets.
    If the result was not an empty set, it means that employees were removed or changed

    *Note. The new list comes in as a list of EmployeeInfoTextAreaFields. If it's empty, it defaults to ['']. In this
    case, we just change that to an empty set:  set()

    Depending on what kind of set operation we did, we can return the type of the operation as an OperationType enum
    class.

    :param old_list: The previous list of employees
    :param new_list: The new list of employees
    :return: A dictionary containing the list of employees and the operation(add or delete)
    """

    add_employees = False

    set_list1 = set(tuple(sorted(d.items())) for d in old_list)
    set_list2 = set() if new_list[0] == '' else set(tuple(sorted(d.items())) for d in new_list)

    diff = set_list1 - set_list2

    if len(diff) == 0:
        if len(new_list) > len(old_list):
            diff = set_list1 ^ set_list2
            add_employees = True

    diff_list = []
    for tup in diff:
        diff_list.append(dict((x, y) for x, y in tup))

    return {
        "diff_list": diff_list,
        "operation": OperationType.ADD_EMPLOYEE if add_employees else OperationType.DELETE_EMPLOYEE
    }
