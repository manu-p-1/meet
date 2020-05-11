import os
import sys
from packaging import version
from urllib.parse import quote_plus


def load_env(dbu, dbpw):

    ver = ".".join(map(str, sys.version_info[:3]))
    if version.parse(ver) < version.parse("3.7.5"):
        print(f"PYTHON VERSION IS {ver} BUT REQUIRES 3.7.5 OR HIGHER")
        exit(1)

    if os.environ.get("ALCHEMY_URI") is None:
        os.environ['ALCHEMY_URI'] = f"mysql://{dbu}:%s@localhost/mrcdb" % quote_plus(dbpw)
        print('Exported ALCHEMY_URI\n')

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

    load_env(dbu=MYSQL_DATABASE_USER, dbpw=MYSQL_DATABASE_PASSWORD)

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
    MYSQL_DATABASE_DB = os.environ.get('DB')
    MYSQL_DATABASE_HOST = os.environ.get('DB_HOST')

