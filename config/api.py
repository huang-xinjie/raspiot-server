"""configuration of raspiot_api"""


class Config:
    JSON_AS_ASCII = False

    SECRET_KEY = 'welcome to raspiot.org'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(database_dir, 'data.sqlite')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    RASPIOT_MAIL_SUBJECT_PREFIX = '[raspIot]'
    RASPIOT_MAIN_SENDER = 'raspiot support <support@raspiot.org>'
    RASPIOT_ADMIN = 'support@raspiot.org'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'default': Config
}
