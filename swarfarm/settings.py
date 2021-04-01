import datetime
import os

import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['LANG'] = 'en_US.UTF-8'

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost', '10.243.243.10']),
    CORS_ALLOWED_ORIGINS=(list, []),
    SITE_ID=(int, 1),
    COMPRESS_ENABLED=(bool, False),
    CACHE_BACKEND=(str, 'django.core.cache.backends.dummy.DummyCache'),
    CACHE_LOCATION=(str, 'swarfarm'),
    EMAIL_BACKEND=(str, 'django.core.mail.backends.console.EmailBackend'),
    EMAIL_HOST=(str, ''),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    EMAIL_FROM=(str, ''),
    CELERY_BROKER=(str, 'amqp://'),
    GOOGLE_API_KEY=(str, ''),
    RECAPTCHA_PUBLIC_KEY=(str, ''),
    RECAPTCHA_PRIVATE_KEY=(str, ''),
    BUGSNAG_API_KEY=(str, ''),
    SUMMONERS_WAR_KEY=(str, '0' * 32),
    SUMMONERS_WAR_IV=(str, '0' * 32),
    JOKER_CONTAINER_KEY=(str, '0' * 64),
    JOKER_CONTAINER_IV=(str, '0' * 32),
    ADMINS=(list, [])
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SITE_ID = env('SITE_ID')
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
WSGI_APPLICATION = 'swarfarm.wsgi.application'

# Game application keys
SUMMONERS_WAR_KEY = env('SUMMONERS_WAR_KEY')
SUMMONERS_WAR_IV = env('SUMMONERS_WAR_IV')
JOKER_CONTAINER_KEY = env('JOKER_CONTAINER_KEY')
JOKER_CONTAINER_IV = env('JOKER_CONTAINER_IV')

# Security settings
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
INTERNAL_IPS = ['127.0.0.1']

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

# SSL settings
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = not DEBUG
SECURE_BROWSER_XSS_FILTER = not DEBUG
SECURE_HSTS_SECONDS = 31556926  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# CORS settings
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CORS_URLS_REGEX = r'^/api(v\d+)?/.*$'

# Email settings
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
SERVER_EMAIL = env('EMAIL_FROM')
DEFAULT_FROM_EMAIL = SERVER_EMAIL

# Admins and Managers
ADMINS = [tuple(record.split('+')) for record in env('ADMINS')]
MANAGERS = ADMINS

# Application definition
INSTALLED_APPS = [
    # Packages
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django_filters',
    'dal',
    'dal_select2',
    'captcha',
    'compressor',
    'corsheaders',
    'crispy_forms',
    'django_celery_results',
    'django_celery_beat',
    'markdown_deux',
    'rest_framework',
    'rest_framework.authtoken',
    'refreshtoken',
    'rest_framework_swagger',
    'timezone_field',

    # Custom apps
    'api',
    'apiv2',
    'herders',
    'bestiary',
    'news',
    'feedback',
    'data_log',
]

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
]

if DEBUG:
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

    DEBUG_TOOLBAR_PANELS = [
        'ddt_request_history.panels.request_history.RequestHistoryPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
    ]
    DEBUG_TOOLBAR_CONFIG = {
        'RESULTS_STORE_SIZE': 1000,
    }

# Bugsnag
if env('BUGSNAG_API_KEY'):
    MIDDLEWARE = ['bugsnag.django.middleware.BugsnagMiddleware'] + MIDDLEWARE

    BUGSNAG = {
        'api_key': env('BUGSNAG_API_KEY'),
        'project_root': BASE_DIR,
        'ignore_classes': ["django.http.response.Http404",],
    }

# URL stuff
ROOT_URLCONF = 'swarfarm.urls'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'news:latest_news'
LOGOUT_REDIRECT_URL = 'news:latest_news'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'bestiary.context_processors.quick_search_form',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

if DEBUG:
    # Non-cached loader
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]

# Database
DATABASES = {
    'default': env.db(),
}

DATABASES['default']['TEST'] = {
    'CHARSET': 'UTF8',
}

# Cache
CACHES = {
    'default': {
        'BACKEND': env('CACHE_BACKEND'),
        'LOCATION': env('CACHE_LOCATION'),
    }
}

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_TRACK_STARTED = True

# Session config
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# I18n
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Package configurations
# compress
COMPRESS_ENABLED = env('COMPRESS_ENABLED')
COMPRESS_CSS_FILTERS = ['compressor.filters.cssmin.rCSSMinFilter']

# crispyforms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Google APIs
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_USE_SSL = True
NOCAPTCHA = True

# DRF
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'apiv2.throttling.ScopedPostRequestThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '500/min',
        'user': '2000/min',
        'registration': '5/min',
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': 'v2',
    'ALLOWED_VERSIONS': ['v2'],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    'DEFAULT_CACHE_ERRORS': False,
}

JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'apiv2.views.jwt_response_payload_handler',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
}
