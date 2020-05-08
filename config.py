import os


'''
Configuration settings to be used on localhost.
'''
class DevelopmentConfig:
    # SERVER RELOAD ON CODE CHANGE
    DEBUG = True

    TEMPLATES_AUTO_RELOAD = True


    #MySQL setup
    MYSQL_DATABASE_USER = os.environ['DB_USER']
    MYSQL_DATABASE_PASSWORD = os.environ['DB_PASS']
    MYSQL_DATABASE_DB = os.environ.get('DB')
    MYSQL_DATABASE_HOST = os.environ.get('DB_HOST')

    SQLALCHEMY_DATABASE_URI = os.environ.get('ALCHEMY_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


'''
Configuration settings to be used on PythonAnywhere.
'''
class ProductionConfig:
    # SERVER RELOAD ON CODE CHANGE
    DEBUG = False

    #MySQL setup
    MYSQL_DATABASE_USER = os.environ['DB_USER']
    MYSQL_DATABASE_PASSWORD = os.environ['DB_PASS']
    MYSQL_DATABASE_DB = 'niledb' #CHANGE TO PA DB
    MYSQL_DATABASE_HOST = 'localhost' #CHANGE TO PA DB URL
