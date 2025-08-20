import os


# https://flask.palletsprojects.com/en/stable/config/#development-production
class BaseConfig:
    """Base configuration"""

    TESTING = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    DEBUG = True


class TestingConfig(BaseConfig):
    """Testing configuration"""

    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""

    DEBUG = False


class StageConfig(BaseConfig):
    """Staging configuration"""

    DEBUG = False
