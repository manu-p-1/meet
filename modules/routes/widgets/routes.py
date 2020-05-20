from server import mysql
from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from server import client
from modules.simulation.logic import department_alloc, department_utilization, current_business_balance, \
    department_balance, department_employee_count, current_outgoing_transactions, active_plans

widgets_bp = Blueprint('widgets_bp', __name__)


@widgets_bp.route('/dash/department_allocation/', methods=['GET'])
def wid_department_allocation():
    return jsonify(department_alloc())


@widgets_bp.route('/dash/department_utilization/', methods=['GET'])
def wid_department_utilization():
    return jsonify(department_utilization())


@widgets_bp.route('/dash/current_business_balance/', methods=['GET'])
def wid_current_business_balance():
    return jsonify(current_business_balance())


@widgets_bp.route('/dash/department_balance/', methods=['GET'])
def wid_department_balance():
    return jsonify(department_balance(session['manager_dept']))


@widgets_bp.route('/dash/department_employee_count/', methods=['GET'])
def wid_department_employee_count():
    return jsonify(amount=department_employee_count(session['manager_dept']))


@widgets_bp.route('/dash/current_outgoing_transactions/', methods=['GET'])  # Doesn't work
def wid_current_outgoing_transactions():
    return jsonify(total=current_outgoing_transactions(session['manager_dept']))


@widgets_bp.route('/dash/active_plans/', methods=['GET'])
def wid_active_plans():
    return jsonify(total=active_plans())
