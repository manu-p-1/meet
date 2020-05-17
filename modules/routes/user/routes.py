import json
from server import mysql
from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
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
    conn = mysql()
    cursor = conn.cursor()
    query = 'SELECT description FROM manager WHERE email = %s'
    cursor.execute(query, (session['manager_email']))
    description = cursor.fetchall()[0][0]
    conn.close()
    return render_template('profile/profile.html', description=description)


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

            conn = mysql()
            cursor = conn.cursor()

            query = '''INSERT INTO plan (plan_name,funding_amount,plan_justification,description,start_date,end_date,
            source_fund,dest_fund,fund_individuals,control_name, control_window,amount_limit,usage_limit,complete) VALUES 
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            cursor.execute(query, (form.planName.data, form.fundingAmount.data,
                                   form.planJustification.data, form.memo.data, form.startDate.data,
                                   form.endDate.data, form.sourceFund.data, form.destFund.data, form.fundIndivEmployeesToggle.data,
                                   form.controlName.data, form.controlWindow.data, form.amountLimit.data, form.usageLimit.data, False))

            conn.commit()
            conn.close()

            return jsonify(
                status=True,
                response=render_template(
                    'create_plan/alert_partial.html', status=True)
            )
        else:
            print(form.errors.items(), file=stderr)
            return jsonify(
                status=False,
                response=render_template(
                    'create_plan/alert_partial.html', form=form, status=False)
            )
