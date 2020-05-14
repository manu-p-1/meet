from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from .forms import LoginForm
from server import db
from models import DepartmentLookup

common_bp = Blueprint('common_bp', __name__,
                      template_folder='templates', static_folder='static')


@common_bp.route('/login/', methods=['GET'])
def login(ctx=None):
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html',form=form)
    else:
        if form.validate_on_submit():
            return 'temp'

@common_bp.route('/')
def landing_page():
    # for dept in ['IT','ACCOUNTING','MARKETING','HUMAN RESOURCES','PRODUCTION','RESEARCH','SECURITY','LOGISTICS']:
    #     x = DepartmentLookup(department=dept)
    #     db.session.add(x)
    #     db.session.commit()
    return redirect(url_for('common_bp.login'))
