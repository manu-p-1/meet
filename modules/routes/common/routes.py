import sys
from server import mysql
from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from .forms import LoginForm
from server import client

from modules.decorators.utils import check_login
from ..utils.functions.function_utils import gather_form_errors

common_bp = Blueprint('common_bp', __name__,
                      template_folder='templates', static_folder='static')


@common_bp.route('/login/', methods=['GET', 'POST'])
def login(ctx=None):
    try:
        load_values()
    except:
        print('')    
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
            query = '''SELECT manager_dept_FK,first_name, last_name, email, title FROM manager WHERE email = %s'''
            cursor.execute(query, (request.form.get('email')))

            try:
                manager = cursor.fetchall()[0]
                query = '''SELECT department FROM department_lookup WHERE id = %s'''
                cursor.execute(query, (manager[0]))
                department = cursor.fetchall()[0][0]

                if manager.check_password(request.form.get('password')):
                    session['logged_in'] = True
                    session['manager_fname'] = manager[1]
                    session['manager_lname'] = manager[2]
                    session['manager_email'] = manager[3]
                    session['manager_dept'] = department
                    session['manager_title'] = manager[4]
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


def load_values():
    conn = mysql.connect()
    cursor = conn.cursor()
    print('\n\nINITIALIZING DB\n\n')
    for i, dept in enumerate(client.departments):
        query = """
            INSERT INTO department_lookup (token, department)
            VALUES (%s,%s)"""
        cursor.execute(query, (dept.token, client.DEPARTMENT_LIST[i]))
        print(dept.token + ' has been inserted.')

    for e in client.employees:
        query = """
            INSERT INTO employee (token,first_name,last_name,user_dept_FK) 
            VALUES (%s ,%s, %s, %s)"""
        cursor.execute(query, (e.token, e.first_name,
                               e.last_name, e.parent_token))
        print(e.token + 'h has been inserted.')

    for dept in client.DEPARTMENT_LIST:
        query = """
            INSERT INTO manager (email,pass,first_name,last_name,title,description,manager_dept_FK)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        cursor.execute(query, (
            client.MANAGERS[dept]['email'], client.MANAGERS[dept]['pass'], client.MANAGERS[dept]['first_name'],
            client.MANAGERS[dept]['last_name'], 'Sr. Division Manager', '', client.MANAGERS[dept]['manager_dept_FK']))
    session['db_init'] = True
