import os


class Config:
    # MySQL setup
    MYSQL_DATABASE_USER = os.getenv('DB_USER')
    MYSQL_DATABASE_PASSWORD = os.getenv('DB_PASS')
    MYSQL_DATABASE_DB = os.getenv('DB')
    MYSQL_DATABASE_HOST = os.getenv('DB_HOST')


class DevelopmentConfig(Config):
    # SERVER RELOAD ON CODE CHANGE
    DEBUG = False
    TEMPLATES_AUTO_RELOAD = True


class ProductionConfig(Config):
    # SERVER RELOAD ON CODE CHANGE
    DEBUG = False


if __name__ == '__main__':
    pass
