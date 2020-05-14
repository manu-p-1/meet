from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from server import db
from models import DepartmentLookup,Employee
import json

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

    dept = request.args.get('department')
    

    dept_token = DepartmentLookup.query.filter_by(department='ACCOUNTING').first()
    employee = Employee.query.filter_by(user_dept_FK=dept_token.token)

    e_payload = [{"name":e.firstname+e.lastname,"id":e.id} for e in employee]

    print(json.dumps(e_payload))

    return json.dumps(e_payload)
