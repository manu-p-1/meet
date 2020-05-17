import sys

from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from .forms import LoginForm
from server import db, client
from models import DepartmentLookup, Manager
from modules.decorators.utils import check_login
from ..utils.functions.function_utils import gather_form_errors

common_bp = Blueprint('common_bp', __name__,
                      template_folder='templates', static_folder='static')


@common_bp.route('/login/', methods=['GET', 'POST'])
def login(ctx=None):

    if check_login(session):
        return redirect(url_for('user_bp.overview'))

    form = LoginForm()

    if request.method == 'GET':
        session['company_name'] = client.BUSINESS_NAME
        return render_template('login.html', form=form)
    else:
        if form.validate_on_submit():
            manager = Manager.query.filter_by(email=request.form.get('email')).first()

            if manager is None:
                flash("Account does not exist.")
                return redirect(url_for('common_bp.login'))

            manager_dept = DepartmentLookup.query.filter_by(id=manager.manager_dept_FK).first()

            if manager.check_password(request.form.get('password')):
                session['logged_in'] = True
                session['manager_fname'] = manager.first_name
                session['manager_lname'] = manager.last_name
                session['manager_email'] = manager.email
                session['manager_dept'] = manager_dept.department
                session['manager_title'] = manager.title
                return redirect(url_for('user_bp.overview'))
            else:
                flash("Account could not be found")
                return redirect(url_for("common_bp.login"))
        else:
            flash(gather_form_errors(form)[0])
            return redirect(url_for('common_bp.login'))


@common_bp.route('/')
def landing_page():
    return redirect(url_for('common_bp.login'))
