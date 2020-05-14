from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from .forms import LoginForm
from server import db
from models import DepartmentLookup,Manager
from modules.decorators.utils import check_login


common_bp = Blueprint('common_bp', __name__,
                      template_folder='templates', static_folder='static')


@common_bp.route('/login/', methods=['GET','POST'])
def login(ctx=None):
    if check_login(session):
        return redirect(url_for('user_bp.overview'))
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html',form=form)
    else:
        if form.validate_on_submit():
            manager = Manager.query.filter_by(email=request.form.get('email')).first()
            if manager.check_password(request.form.get('password')):
                session['logged_in'] = True
                return redirect(url_for('user_bp.overview'))

@common_bp.route('/')
def landing_page():
    return redirect(url_for('common_bp.login'))
