import os
import datetime
import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ['LANG'] = 'en_US.UTF-8'

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    COMPRESS_ENABLED=(bool, False),
    EMAIL_HOST=(str, ''),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    CACHE_LOCATION=(str, None),
    GOOGLE_API_KEY=(str, None),
    RECAPTCHA_PUBLIC_KEY=(str, None),
    RECAPTCHA_PRIVATE_KEY=(str, None),
    SUMMONERS_WAR_SECRET_KEY=(str, ''),
    BUGSNAG_API_KEY=(str, None),
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SITE_ID = 1
SECRET_KEY = env('SECRET_KEY')
SUMMONERS_WAR_SECRET_KEY = env('SUMMONERS_WAR_SECRET_KEY')
DEBUG = env('DEBUG')
WSGI_APPLICATION = 'swarfarm.wsgi.application'

# Security settings
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']

if DEBUG:
    ALLOWED_HOSTS += ['10.0.2.2', '10.243.243.10']

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
CSRF_COOKIE_HTTPONLY = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = not DEBUG
SECURE_BROWSER_XSS_FILTER = not DEBUG
SECURE_HSTS_SECONDS = 31556926  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
SERVER_EMAIL = 'noreply@swarfarm.com'
DEFAULT_FROM_EMAIL = SERVER_EMAIL

# Admins and Managers
ADMINS = (('Peter', 'swarfarm@porksmash.com'),)
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
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'dal',
    'dal_select2',
    'django_filters',
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
    'sw_parser',
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
LOGIN_REDIRECT_URL = 'news:latest_news'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

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

# django_cors
CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api(v\d+)?/.*$'

# Google APIs
GOOGLE_API_KEY = env('GOOGLE_API_KEY')
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
}

REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    'DEFAULT_CACHE_ERRORS': False,
}

JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'apiv2.views.jwt_response_payload_handler',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
}
