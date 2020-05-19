from models import Plan
from server import mysql, client
from datetime import date
from sys import stderr
from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from modules.routes.user.forms import create_plan_form
from modules.decorators.utils import login_required
from modules.middleware.logic import dept_to_dept, dept_to_emp

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
    current_date = date.today()
    current_date_fmt = current_date.strftime("%m/%d/%Y")

    fund_choices = client.DEPT_MAPPINGS

    if not session.get('create_plan_visited'):
        session['create_plan_visited'] = True
        fund_choices.insert(0, ('', 'Please choose a fund destination'))

    form = create_plan_form(session, fund_choices)

    if request.method == 'GET':
        return render_template('create_plan/create_plan_partial.html', form=form, current_date=current_date_fmt)
    else:
        if form.validate_on_submit():
            print(request.form, file=stderr)

            # the below code is only valid for dept-to-dept transfers as of now
            # feel free to test because there are 64 different ways
            
            conn = mysql.connect()
            cursor = conn.cursor()

            p = Plan(cursor, conn=conn)
            p.insert(form)

            # There needs to be some more logic written here, specifically sending the right id

            ## unckeck the below and restart server to see it work on the plan you make (need more logic as above)
            #dept_to_emp(1)

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
