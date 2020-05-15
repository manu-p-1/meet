from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from server import db
from models import DepartmentLookup, Employee
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

    dept = request.args.get('department')[:2]
    name = request.args.get('term')
    dept_token = DepartmentLookup.query.filter_by(department=dept).first()
    employee = Employee.query.filter_by(user_dept_FK=dept_token.token)


    if name and ' ' in name:
        fname = name[:name.find('')].lower()
        lname = name[name.find(''):].lower()
        e_payload = [{"name": e.first_name + ' ' + e.last_name, "id": e.id}
                 for e in employee if fname in e.first_name.lower() and lname in e.last_name.lower()]
    else:
        name = name.lower()
        e_payload = [{"name": e.first_name + ' ' + e.last_name, "id": e.id}
                 for e in employee if name in e.first_name.lower() or name in e.last_name.lower()]
        

    # e_payload = [{"name": e.first_name+e.last_name, "id": e.id}
    #              for e in employee]

    print(json.dumps(e_payload))

    return json.dumps(e_payload)
