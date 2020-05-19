from server import mysql
from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from server import client
from modules.simulation.logic import department_alloc, department_utilization

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/dept_allocation/', methods=['GET'])
def dept_allocation():
    funds = department_alloc()

    dept_amt = {}
    for f in funds:
        amt = str(f[0])
        dest = f[1]
        biz = client.client_sdk.businesses.find(token=dest)
        biz_name = biz.business_name_dba
        for name in client.DEPT_MAPPINGS:
            if name[0] == biz_name:
                biz_name_readable = name[1]
                dept_amt[biz_name_readable] = amt

    return jsonify(dept_amt)


@api_bp.route('/dept_utilization/', methods=['GET'])
def dept_utilization():
    utilization = department_utilization()
    return jsonify(utilization)
