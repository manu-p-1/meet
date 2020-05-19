import os
import sys
from sys import stderr

from flask import Flask, session
from flaskext.mysql import MySQL
from flask_assets import Environment

from mrc_bundles import bundles
from flask_wtf.csrf import CSRFProtect
from marqeta_setup import MarqetaClient
import secrets
import subprocess
import platform

mysql = MySQL()
csrf = CSRFProtect()
client = MarqetaClient()


def create_server():
    if platform.system() == 'Windows':
        os.system('startdb.sh')
    else:
        os.system('./startdb.sh')
    app = Flask(__name__)

    # update app config from file config.py
    app.config.from_object('config.DevelopmentConfig')

    # IN A PRODUCTION ENVIRONMENT
    # app.config.from_object(config)
    app.jinja_env.cache = {}

    with app.app_context():
        # initialize extensions
        mysql.init_app(app)
        csrf = CSRFProtect(app)

        # secret_key generation
        app.secret_key = secrets.token_urlsafe(256)

        assets = Environment(app)
        assets.register(bundles)

        # if you reformat this code, the imports go up resulting in
        # circular importing which breaks the blueprint architecture

        from modules.routes.common import routes as common_routes
        from modules.routes.user import routes as user_routes
        from modules.routes.utils import routes as util_routes
        from modules.routes.api import routes as api_routes

        app.register_blueprint(common_routes.common_bp)
        app.register_blueprint(user_routes.user_bp, url_prefix="/user")
        app.register_blueprint(util_routes.util_bp, url_prefix="/util")
        app.register_blueprint(api_routes.api_bp, url_prefix="/api")

    return app


    
