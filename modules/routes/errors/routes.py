from flask import render_template, Blueprint

errors_bp = Blueprint('errors_bp', __name__,
                      template_folder='templates', static_folder='static')


def bad_request(e):
    return render_template('errors.html', err=400,
                           message="Bad Request."), 400


def forbidden(e):
    return render_template('errors.html', err=403,
                           message="The page you were looking for is not allowed."), 403


def page_not_found(e):
    return render_template('errors.html', err=404,
                           message="The page you were looking for could not be found."), 404


def gone(e):
    return render_template('errors.html', err=410,
                           message="The page you were looking for no longer exists."), 410


def internal_server_error(e):
    return render_template('errors.html', err=500,
                           message="There was a problem on our end. Please try again later."), 500
