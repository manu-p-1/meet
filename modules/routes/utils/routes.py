from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from server import db
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
    


    return render_template('overview/dash_overview_partial.html')
