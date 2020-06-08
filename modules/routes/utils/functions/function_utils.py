from datetime import datetime, timezone
from typing import Union, Dict, List, Any

from flask import render_template, jsonify

from modules.routes.user.custom_fields import ISimpleEmployee
from modules.routes.utils.classes.class_utils import ManipulationType, SupportedTimeFormats


def gather_form_errors(form):
    ll = []
    for field, errors in form.errors.items():
        for error in form.errors[field]:
            ll.append(error)
    return ll


def is_duplicate_plan(mysql, field_data) -> bool:
    conn = mysql.connect()
    cursor = conn.cursor()
    q = '''SELECT plan_name FROM plan WHERE plan_name = %s'''
    cursor.execute(q, field_data)
    if len(cursor.fetchall()) == 0:
        conn.close()
        return False
    else:
        conn.close()
        return True


def is_active_plan(mysql, field_data) -> bool:
    conn = mysql.connect()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)
    start_date = now.strftime(SupportedTimeFormats.FMT_UTC)
    q = '''SELECT plan_name FROM plan WHERE plan_name = %s AND start_date < %s'''
    cursor.execute(q, (field_data, start_date))
    fetch = cursor.fetchall()
    conn.close()

    return False if len(fetch) == 0 else True


def is_expired_plan(mysql, plan_name) -> bool:
    conn = mysql.connect()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)

    q = """SELECT end_date FROM plan WHERE plan_name = %s"""
    cursor.execute(q, plan_name)
    fetch = cursor.fetchall()
    conn.close()

    if len(fetch) == 0:
        raise Exception("Plan name could not be found")

    if fetch[0][0] is None:
        return False

    end_date_obj = datetime.strptime(fetch[0][0], SupportedTimeFormats.FMT_UTC)

    return True if now > end_date_obj else False


def find_all_employees(cursor, dept) -> Union[Dict[str, Union[List[ISimpleEmployee], int]], Any]:
    q = """
        SELECT e.id FROM employee e 
        JOIN department_lookup dl on e.employee_dept_FK = dl.token
        WHERE dl.department = %s;
    """
    cursor.execute(q, dept)
    employees = cursor.fetchall()

    len_emps = len(employees)
    if employees is not None and len_emps != 0:
        return {
            "data": [ISimpleEmployee(eid=id_) for id_ in employees],
            "length": len_emps
        }
    return None


def short_error(form=None, err_list=None):
    if form is not None and err_list is None:
        return jsonify(
            response_status="error",
            response=render_template(
                'plans/plan_alert_partial.html',
                status=False,
                form=form
            )
        )
    elif form is None and err_list is not None:
        return jsonify(
            response_status="error",
            response=render_template(
                'plans/plan_alert_partial.html',
                status=False,
                err_list=err_list
            )
        )
    raise Exception('form and err_list are mutually exclusive')


def short_success(manip_type: ManipulationType):
    return jsonify(
        response_status="success",
        response=render_template(
            'plans/plan_alert_partial.html',
            status=True,
            manip_type=manip_type.value
        )
    )


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def custom_strftime(fmt, t):
    return t.strftime(fmt).replace('{S}', str(t.day) + suffix(t.day))
