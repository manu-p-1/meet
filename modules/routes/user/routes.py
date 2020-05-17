import json

from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for

from models import Manager, Plan, PlanUser
from modules.routes.user.forms import CreatePlanForm
from datetime import date
from sys import stderr
from modules.decorators.utils import login_required

user_bp = Blueprint('user_bp', __name__,
                    template_folder='templates', static_folder='static')


@user_bp.route('/overview/', methods=['GET'])
@login_required(session)
def overview(ctx=None):
    return render_template('overview/dash_overview_partial.html')


@user_bp.route('/profile/', methods=['GET', 'POST'])
@login_required(session)
def profile(ctx=None):
    manager = Manager.query.filter_by(email=session['manager_email']).first()
    return render_template('profile/profile.html', description=manager.description)


@user_bp.route('/logout/', methods=['GET'])
@login_required(session)
def logout(ctx=None):
    session.clear()
    flash("Logout Successful", category='success')
    return redirect(url_for('common_bp.login'))


@user_bp.route('/create_plan/', methods=['GET', 'POST'])
@login_required(session)
def create_plan():
    current_date = date.today()
    current_date_fmt = current_date.strftime("%m/%d/%Y")

    form = CreatePlanForm()
    if request.method == 'GET':
        return render_template('create_plan/create_plan_partial.html', form=form, current_date=current_date_fmt)
    else:
        if form.validate_on_submit():
            print(request.form, file=stderr)

            plan = Plan(plan_name=form.planName.data,
                        funding_amount=form.fundingAmount.data,
                        plan_justification=form.planJustification.data,
                        description=form.memo.data,
                        start_date=form.startDate.data,
                        end_date=form.endDate.data,
                        source_fund=form.sourceFund.data,
                        dest_fund=form.destFund.data,
                        fund_individuals=form.fundIndivEmployeesToggle.data,
                        control_name=form.controlName.data,
                        control_window=form.controlWindow.data,
                        amount_limit=form.amountLimit.data,
                        usage_limit=form.usageLimit.data,
                        complete=False)

            return jsonify(
                status=True,
                response=render_template('create_plan/alert_partial.html', status=True)
            )
        else:
            print(form.errors.items(), file=stderr)
            return jsonify(
                status=False,
                response=render_template('create_plan/alert_partial.html', form=form, status=False)
            )
