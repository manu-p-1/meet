import locale

from modules.decorators.utils import login_required
from flask import Blueprint, jsonify, session
from modules.simulation.logic import department_alloc, department_utilization, current_business_balance, \
    department_balance, department_employee_count, current_outgoing_transactions, active_plans, \
    department_employee__monthly_spending, plan_avg_six_months, generate_employee_spending_graph
from server import client

widgets_bp = Blueprint('widgets_bp', __name__)


@widgets_bp.route('/dash/department_allocation/', methods=['GET'])
@login_required(session)
def wid_department_allocation():
    return jsonify(department_alloc())


@widgets_bp.route('/dash/department_utilization/', methods=['GET'])
@login_required(session)
def wid_department_utilization():
    return jsonify(department_utilization())


@widgets_bp.route('/dash/current_business_balance/', methods=['GET'])
@login_required(session)
def wid_current_business_balance():
    sendable = current_business_balance()
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    for key, val in sendable.items():
        sendable[key] = locale.currency(round(val), grouping=True)
    return jsonify(sendable)


@widgets_bp.route('/dash/department_balance/', methods=['GET'])
@login_required(session)
def wid_department_balance():
    sendable = department_balance(session['manager_dept'])
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    for key, val in sendable.items():
        sendable[key] = locale.currency(round(val), grouping=True)
    return jsonify(sendable)


@widgets_bp.route('/dash/department_employee_count/', methods=['GET'])
@login_required(session)
def wid_department_employee_count():
    return jsonify(amount=department_employee_count(session['manager_dept']))


@widgets_bp.route('/dash/current_outgoing_transactions/', methods=['GET'])
@login_required(session)
def wid_current_outgoing_transactions():
    return jsonify(current_outgoing_transactions(session['manager_dept']))


@widgets_bp.route('/dash/active_plans/', methods=['GET'])
@login_required(session)
def wid_active_plans():
    return jsonify(total=active_plans())


@widgets_bp.route('/dash/department_employee__monthly_spending/', methods=['GET'])
@login_required(session)
def wid_department_employee__monthly_spending():
    sendable = department_employee__monthly_spending(session['manager_dept'])
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    for key, value in sendable.items():
        value['gpa_bal'] = locale.currency(value['gpa_bal'], grouping=True)
        value['monthly_spending'] = locale.currency(value['monthly_spending'], grouping=True)
    return jsonify(sendable)


@widgets_bp.route('/dash/plan_avg_six_months/', methods=['GET'])
@login_required(session)
def wid_plan_avg_six_months():
    return jsonify(
        data=plan_avg_six_months(session['manager_dept']),
        department=client.READABLE_DEPARTMENTS[session['manager_dept']]
    )


@widgets_bp.route('/dash/monthly_employee_spending/', methods=['GET'])
@login_required(session)
def wid_monthly_employee_spending():
    return jsonify(
        data=generate_employee_spending_graph(session['manager_dept'])
    )
