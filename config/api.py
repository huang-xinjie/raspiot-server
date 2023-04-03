"""configuration of raspiot api"""
import os


class Config:
    JSON_AS_ASCII = False

    SECRET_KEY = 'welcome to raspiot.org'
    database_path = os.path.abspath(os.path.dirname(__file__)) + '/../db/'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(database_path, 'raspiot.sqlite')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    RASPIOT_MAIL_SUBJECT_PREFIX = '[raspiot]'
    RASPIOT_MAIN_SENDER = 'raspiot support <support@raspiot.org>'
    RASPIOT_ADMIN = 'support@raspiot.org'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


app_config = {
    'development': DevelopmentConfig,
    'default': Config
}
