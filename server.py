from flask import Flask
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
import secrets


mysql = MySQL()
db = SQLAlchemy()


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
        
        db.create_all()



        from models import User
        @app.route('/')
        def index():
            test = User(email='hello',firstname='hi',lastname='hi',password='hi')
            db.session.add(test)
            db.session.commit()
            return 'Hello'

        #secret_key generation
        app.secret_key = secrets.token_urlsafe(256)
        

        # if you reformat this code, the imports go up resulting in
        # circular importing which breaks the blueprint architecture

        # from routes.common import routes as common_routes
        # from routes.user import routes as user_routes
        # from routes.admin import routes as admin_routes
        # from routes.api import routes as api_routes
        # from routes.errors.routes import page_not_found,logic_error

        # app.register_blueprint(common_routes.common_bp)
        # app.register_blueprint(user_routes.user_bp, url_prefix="/nileuser")
        # app.register_blueprint(admin_routes.admin_bp, url_prefix="/admin")
        # app.register_blueprint(api_routes.api_bp,url_prefix="/api")

        # app.register_error_handler(404,page_not_found)
        # app.register_error_handler(500,logic_error)

    return app