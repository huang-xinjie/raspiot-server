"""configuration of raspiot api"""
import os
from datetime import datetime


class Config:
    JSON_AS_ASCII = False

    SECRET_KEY = 'welcome to raspiot.org'
    DATABASE_PATH = os.path.abspath(os.path.dirname(__file__)) + '/../db/'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(DATABASE_PATH, 'raspiot.sqlite')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    RASPIOT_MAIL_SUBJECT_PREFIX = '[raspiot]'
    RASPIOT_MAIN_SENDER = 'raspiot support <support@raspiot.org>'
    RASPIOT_ADMIN = 'support@raspiot.org'

    DEFAULT_ROOM = 'my_devices'
    # raspiot standard initial time
    STANDARD_INITIAL_TIME = datetime.strptime("2015-12-17 22:22:00.000022", '%Y-%m-%d %H:%M:%S.%f')

    UPLOAD_FOLDER = 'uploads'
    UPLOAD_ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.mp4'}

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


app_config = {
    'development': DevelopmentConfig,
    'default': Config
}
