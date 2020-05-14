from flask import Flask
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment
from mrc_bundles import bundles
from flask_wtf.csrf import CSRFProtect
from marqeta_setup import MarqetaClient
import secrets

mysql = MySQL()
db = SQLAlchemy()
csrf = CSRFProtect()
client = MarqetaClient()

def create_server(config):
    app = Flask(__name__)

    

    # update app config from file config.py
    app.config.from_object('config.DevelopmentConfig')
    # IN A PRODUCTION ENVIRONMENT
    # app.config.from_object(config)
    app.jinja_env.cache = {}

    with app.app_context():
        # initialize extensions
        mysql.init_app(app)
        db = SQLAlchemy(app)
        csrf = CSRFProtect(app)
        
        

        from models import DepartmentLookup,Employee,Manager

        for i,dept in enumerate(client.departments):
            db.session.add(DepartmentLookup(token=dept.token,
                                            department=client.DEPARTMENT_LIST[i]))

        for e in client.employees:
            db.session.add(Employee(token=e.token, firstname=e.first_name,
                                    lastname=e.last_name, user_dept_FK=e.parent_token))

        db.session.add(Manager(email='mrc@hack.com',_pass='root'))
        db.session.commit()
        
        #secret_key generation
        app.secret_key = secrets.token_urlsafe(256)

        assets = Environment(app)
        assets.register(bundles)

        # if you reformat this code, the imports go up resulting in
        # circular importing which breaks the blueprint architecture

        from modules.routes.common import routes as common_routes
        from modules.routes.user import routes as user_routes
        from modules.routes.utils import routes as util_routes
        # from routes.admin import routes as admin_routes
        # from routes.api import routes as api_routes
        # from routes.errors.routes import page_not_found,logic_error

        app.register_blueprint(common_routes.common_bp)
        app.register_blueprint(user_routes.user_bp, url_prefix="/user")
        app.register_blueprint(util_routes.util_bp, url_prefix="/util")
        # app.register_blueprint(admin_routes.admin_bp, url_prefix="/admin")
        # app.register_blueprint(api_routes.api_bp,url_prefix="/api")

        # app.register_error_handler(404,page_not_found)
        # app.register_error_handler(500,logic_error)

    return app


