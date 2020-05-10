from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for
from .forms import LoginForm

common_bp = Blueprint('common_bp', __name__,
                      template_folder='templates', static_folder='static')


@common_bp.route('/login/', methods=['GET'])
def login(ctx=None):
    return render_template('login.html',form=LoginForm())

@common_bp.route('/')
def landing_page():
    return redirect(url_for('common_bp.login'))