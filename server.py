from flask import Flask, session
from flaskext.mysql import MySQL
from flask_assets import Environment

from mrc_bundles import bundles
from flask_wtf.csrf import CSRFProtect
from marqeta_setup import MarqetaClient
import secrets

mysql = MySQL()
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
        csrf = CSRFProtect(app)


        # conn = mysql.connect()
        # cursor = conn.cursor()
        # print('\n\nINITIALIZING DB\n\n')
        # for i, dept in enumerate(client.departments):
        #     query = """
        #     INSERT INTO department_lookup (token, department) 
        #     VALUES (%s,%s)"""
        #     cursor.execute(query, (dept.token, client.DEPARTMENT_LIST[i]))
        #     print(dept.token + ' has been inserted.')

        # for e in client.employees:
        #     query = """
        #     INSERT INTO employee (token,first_name,last_name,user_dept_FK) 
        #     VALUES (%s ,%s, %s, %s)"""
        #     cursor.execute(query, (e.token, e.first_name,
        #                         e.last_name, e.parent_token))
        #     print(e.token + 'h has been inserted.')

        # for dept in client.DEPARTMENT_LIST:
        #     query = """
        #     INSERT INTO manager (email,pass,first_name,last_name,title,description,manager_dept_FK)
        #     VALUES (%s, %s, %s, %s, %s, %s, %s)
        #     """
        #     cursor.execute(query, (
        #         client.MANAGERS[dept]['email'], client.MANAGERS[dept]['pass'], client.MANAGERS[dept]['first_name'],
        #         client.MANAGERS[dept]['last_name'], 'Sr. Division Manager', '', client.MANAGERS[dept]['manager_dept_FK']))
        

        # conn.commit()
        # conn.close()
        # print('\n\nDB INITIALIZED\n\n')


        # secret_key generation
        app.secret_key = secrets.token_urlsafe(256)

        assets = Environment(app)
        assets.register(bundles)

        # if you reformat this code, the imports go up resulting in
        # circular importing which breaks the blueprint architecture

        from modules.routes.common import routes as common_routes
        from modules.routes.user import routes as user_routes
        from modules.routes.utils import routes as util_routes

        app.register_blueprint(common_routes.common_bp)
        app.register_blueprint(user_routes.user_bp, url_prefix="/user")
        app.register_blueprint(util_routes.util_bp, url_prefix="/util")

    return app


    
