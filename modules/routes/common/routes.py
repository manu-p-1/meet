import sys
from server import mysql
from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from .forms import LoginForm
from server import client

from modules.decorators.utils import check_login
from modules.routes import load_values
from modules.routes.utils.functions.function_utils import gather_form_errors
from modules.simulation.logic import simulate_startup

common_bp = Blueprint('common_bp', __name__,
                      template_folder='templates', static_folder='static')


@common_bp.route('/login/', methods=['GET', 'POST'])
def login(ctx=None):
    if not session.get('db_init'):
        try:
            load_values()
            print('starting simulation....')
            simulate_startup()
        except Exception as e:
            print(e)

    if check_login(session):
        return redirect(url_for('user_bp.overview'))

    form = LoginForm()

    if request.method == 'GET':
        session['company_name'] = client.BUSINESS_NAME
        return render_template('login.html', form=form)
    else:
        if form.validate_on_submit():
            conn = mysql.connect()
            cursor = conn.cursor()
            query = '''SELECT manager_dept_FK,first_name, last_name, email, title, pass, gender FROM manager WHERE email = %s'''
            cursor.execute(query, (request.form.get('email')))

            try:
                manager = cursor.fetchall()[0]
                print(manager)
                query = '''SELECT department FROM department_lookup WHERE id = %s'''
                cursor.execute(query, (manager[0]))
                department = cursor.fetchall()[0][0]

                if manager[5] == request.form.get('password'):
                    session['logged_in'] = True
                    session['manager_fname'] = manager[1]
                    session['manager_lname'] = manager[2]
                    session['manager_email'] = manager[3]
                    session['manager_dept'] = department
                    session['manager_title'] = manager[4]
                    session['manager_gender'] = manager[6]
                    print(session)
                    return redirect(url_for('user_bp.overview'))
                else:
                    flash("Account could not be found", category='err')
                    return redirect(url_for("common_bp.login"))
            except:
                flash("Account does not exist.", category='err')
                return redirect(url_for('common_bp.login'))

        else:
            flash(gather_form_errors(form)[0], category='err')
            return redirect(url_for('common_bp.login'))


@common_bp.route('/')
def landing_page():
    return redirect(url_for('common_bp.login'))
