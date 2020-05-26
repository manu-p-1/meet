import os

'''
Configuration settings to be used on localhost.
'''


class DevelopmentConfig:
    # SERVER RELOAD ON CODE CHANGE
    DEBUG = False
    TEMPLATES_AUTO_RELOAD = True

    # MySQL setup
    MYSQL_DATABASE_USER = os.getenv('DB_USER')
    MYSQL_DATABASE_PASSWORD = os.getenv('DB_PASS')
    MYSQL_DATABASE_DB = os.getenv('DB')
    MYSQL_DATABASE_HOST = os.getenv('DB_HOST')

'''
Configuration settings to be used on PythonAnywhere.
'''


class ProductionConfig:
    # SERVER RELOAD ON CODE CHANGE
    DEBUG = False

    # MySQL setup
    MYSQL_DATABASE_USER = os.getenv('DB_USER')
    MYSQL_DATABASE_PASSWORD = os.getenv('DB_PASS')
    MYSQL_DATABASE_DB = os.getenv('DB')
    MYSQL_DATABASE_HOST = os.getenv('DB_HOST')


if __name__ == '__main__':
    pass