from flask import Blueprint, render_template, request, jsonify, redirect, flash, session, url_for

user_bp = Blueprint('user_bp', __name__,
                      template_folder='templates', static_folder='static')


@user_bp.route('/overview/', methods=['GET'])
def login(ctx=None):
    return render_template('overview/dash_overview_partial.html')
