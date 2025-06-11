import os


class Config:
    '''Base configuration.'''
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key-change-in-production')

    # Flask application settings
    DEBUG = False
    TESTING = False

    # Algorithm settings
    MAX_INPUT_SIZE = 20  # Maximum number of items in input
    SHOW_DETAILED_LOGS = True  # Show detailed logs in result page

    # Static files configuration
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    # Application specific settings
    APP_NAME = 'הדגמת אלגוריתם'
    APP_DESCRIPTION = 'אתר פשוט להדגמת אלגוריתמים'


class DevelopmentConfig(Config):
    '''Development configuration.'''
    DEBUG = True
    DEVELOPMENT = True

    # Additional development settings
    EXPLAIN_ERRORS = True  # Provide detailed error explanations


class TestingConfig(Config):
    '''Testing configuration.'''
    TESTING = True
    DEBUG = True

    # Test-specific settings
    WTF_CSRF_ENABLED = False  # Disable CSRF protection in tests


class ProductionConfig(Config):
    '''Production configuration.'''
    # In production, set this to a strong random value
    SECRET_KEY = os.environ.get('SECRET_KEY', None)

    # Security settings for production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


# Environment configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


# Set active configuration
def get_config():
    '''Returns the active configuration based on environment variable.'''
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])
