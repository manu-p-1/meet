from datetime import datetime, timezone

from flask import render_template, jsonify

from modules.routes.utils.classes.class_utils import ManipulationType


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
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    q = '''SELECT plan_name FROM plan WHERE plan_name = %s AND start_date < %s'''
    cursor.execute(q, (field_data, start_date))
    if len(cursor.fetchall()) == 0:
        conn.close()
        return False
    else:
        conn.close()
        return True


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
