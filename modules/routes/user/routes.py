import json

from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from modules.routes.user.forms import CreatePlanForm
from datetime import date
from sys import stderr
from modules.decorators.utils import login_required

user_bp = Blueprint('user_bp', __name__,
                    template_folder='templates', static_folder='static')

@login_required(session)
@user_bp.route('/overview/', methods=['GET'])
def overview(ctx=None):
    return render_template('overview/dash_overview_partial.html')


@login_required(session)
@user_bp.route('/create_plan/', methods=['GET', 'POST'])
def create_plan():
    print("IN CREATE PLAN", file=stderr)
    current_date = date.today()
    current_date_fmt = current_date.strftime("%m/%d/%Y")

    form = CreatePlanForm()
    if request.method == 'GET':
        return render_template('create_plan/create_plan_partial.html', form=form, current_date=current_date_fmt)
    else:
        if form.validate_on_submit():
            print("=============FORM VALIDATED SUCCESSFULLY================", file=stderr)
            return jsonify(
                status=True,
                response=render_template('create_plan/alert_partial.html', status=True)
            )
        else:
            print(form.errors.items(), file=stderr)
            print("=============FORM VALIDATED UNSUCCESSFULLY================", file=stderr)
            return jsonify(
                status=False,
                response=render_template('create_plan/alert_partial.html', form=form, status=False)
            )
