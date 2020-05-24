from models import Plan
from modules.routes.utils.classes.class_utils import ManipulationType
from modules.routes.utils.functions.function_utils import is_duplicate_plan, is_active_plan, short_error
from server import mysql, client
from datetime import date
from sys import stderr
from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from modules.routes.user.forms import create_plan_form, get_plan_form
from modules.decorators.utils import login_required
from modules.middleware.logic import executerOrders

user_bp = Blueprint('user_bp', __name__,
                    template_folder='templates', static_folder='static')


@user_bp.route('/overview/', methods=['GET'])
@login_required(session)
def overview(ctx=None):
    return render_template('overview/dash_overview_partial.html')


@user_bp.route('/profile/', methods=['GET', 'POST'])
@login_required(session)
def profile(ctx=None):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT description FROM manager WHERE email = %s'
    cursor.execute(query, (session['manager_email']))
    description = cursor.fetchall()[0][0]

    conn.close()

    if description is None or description.strip() == '':
        description = "None Provided"

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
    fund_choices = client.DEPT_MAPPINGS

    if not session.get('create_plan_visited'):
        session['create_plan_visited'] = True
        fund_choices.insert(0, ('', 'Please choose a fund destination'))

    form = create_plan_form(session, fund_choices)

    if request.method == 'GET':
        return render_template('plans/create_plan/create_plan_partial.html', form=form, current_date=time_now())
    else:
        if form.validate_on_submit():
            print(request.form, file=stderr)

            conn = mysql.connect()
            cursor = conn.cursor()

            if is_duplicate_plan(mysql, form.planName.data):
                return short_error(err_list=['This plan is already exists'])

            p = Plan(cursor, conn=conn)
            p.insert(form)

            executerOrders()

            return jsonify(
                response_status="success",
                response=render_template(
                    'alert_partial.html', status=True, manip_type=ManipulationType.CREATED.value)
            )
        else:
            print(form.errors.items(), file=stderr)
            return jsonify(
                response_status="error",
                response=render_template(
                    'alert_partial.html', form=form, status=False)
            )


@user_bp.route('/manage_plan/', methods=['GET', 'POST'])
@login_required(session)
def manage_plan():
    fund_choices = client.DEPT_MAPPINGS
    if not session.get('create_plan_visited'):
        session['create_plan_visited'] = True
        fund_choices.insert(0, ('', 'Please choose a fund destination'))

    form = get_plan_form(session, fund_choices)

    if request.method == 'GET':
        return render_template('plans/manage_plan/manage_plan_partial.html', form=form, current_date=time_now())
    else:
        formatted_plan = session['MANAGE_FORM']
        form = get_plan_form(session, client.DEPT_MAPPINGS)

        if form.validate_on_submit():
            print(request.form, file=stderr)

            conn = mysql.connect()
            cursor = conn.cursor()

            if formatted_plan['plan_name'] != form.planName.data:
                if is_duplicate_plan(mysql, form.planName.data):
                    return short_error(err_list=['This plan is already exists'])

            if formatted_plan['is_active']:
                return short_error(err_list=['This plan is currently active'])

            p = Plan(cursor, conn=conn)
            p.update(form, formatted_plan['id'])

            """
            We get plan.employeesOptional.data

            We get a list of employees associated with the old plan through a query.
            We delete any employee in employee_plan that is not in the list of employees

            """

            return jsonify(
                response_status="success",
                response=render_template(
                    'alert_partial.html', status=True, manip_type=ManipulationType.UPDATED.value)
            )
        else:
            return short_error(form=form)


def time_now() -> str:
    current_date = date.today()
    return current_date.strftime("%m/%d/%Y")
