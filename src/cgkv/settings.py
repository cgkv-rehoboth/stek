import os

from machina import get_apps as get_machina_apps
from machina import MACHINA_MAIN_TEMPLATE_DIR, MACHINA_MAIN_STATIC_DIR

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xtij@)g$t19zj^l$u)gud6-9!0436!=cp&8prn(ahk9)68(j&+'

PAGE_USE_SITE_ID = True
SITE_ID = 1

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
          os.path.join(BASE_DIR, "../src/custommachina/templates/"),
          MACHINA_MAIN_TEMPLATE_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "machina.core.context_processors.metadata",
            ],
        },
    },
]

LOCALE_PATHS = [
  # Custom Machina translation
  os.path.join(BASE_DIR, "../src/custommachina/locale/"),
]

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/django-messages'

DEFAULT_FROM_EMAIL = 'Rehobothkerk Woerden <info@rehobothkerkwoerden.nl>'

INTERNAL_IPS = ('127.0.0.1',)

APPEND_SLASH = False

CORS_ORIGIN_WHITELIST = (
  'localhost:8080',
)

# Application definition

INSTALLED_APPS = [
  'flat',
  'django.contrib.admin',
  'django.contrib.sites',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'whitenoise.runserver_nostatic',
  'django.contrib.staticfiles',
  'django_tables2',
  'rest_framework',
  'django_extensions',
  'corsheaders',
  'agenda',
  'base',
  'public',
  'mptt',
  'haystack',
  'widget_tweaks',
  'django_markdown',
] + get_machina_apps()

MIDDLEWARE_CLASSES = (
  'corsheaders.middleware.CorsMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  #'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'base.middleware.ProfileMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',
  'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',

)

REST_FRAMEWORK = {
  'DEFAULT_PERMISSION_CLASSES': (
    'rest_framework.permissions.AllowAny',
  ),
  'DEFAULT_AUTHENTICATION_CLASSES': (
    'rest_framework.authentication.SessionAuthentication',
  ),
  'DEFAULT_FILTER_BACKENDS': (
    'rest_framework.filters.DjangoFilterBackend',
  )
}

ROOT_URLCONF = 'cgkv.urls'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/dashboard'

WSGI_APPLICATION = 'cgkv.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': 'cgkv',
    'USER': 'cgkv',
    'PASSWORD': 'lCCnO6D9Py1VQukTlGknTnFiNyx6TmJ6',
    'HOST': 'localhost',
    'PORT': '3306',
  }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'nl'

TIME_ZONE = None

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
MEDIA_URL = "/media/"

STATIC_ROOT = os.path.join(BASE_DIR, "../static/")
MEDIA_ROOT = os.path.join(BASE_DIR, "../media/")

STATICFILES_DIRS = (
  os.path.join(BASE_DIR, "../dist/"),
  MACHINA_MAIN_STATIC_DIR
)

#
# application settings
#

NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = '6LdTEBsTAAAAAEGoRs_P10MVgylFKuxHnKZzB-m1'
RECAPTCHA_PRIVATE_KEY = '6LdTEBsTAAAAAGdjKkSYNWRSx_5w5fCEZGrZIkyk'

# cache settings

CACHES = {
  'default': {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
  },
  'machina_attachments': {
    'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
    'LOCATION': '/tmp',
  }
}

HAYSTACK_CONNECTIONS = {
  'default': {
    'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
  },
}

#
# Machina settings
#

MACHINA_FORUM_NAME = "Rehobothkerk Forum"

MACHINA_DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = [
    'can_see_forum',
    'can_read_forum',
    'can_start_new_topics',
    'can_reply_to_topics',
    'can_edit_own_posts',
    'can_post_without_approval',
    'can_create_polls',
    'can_vote_in_polls',
    'can_download_file',
]

#
# localsettings loading
#

localsettingspath = os.path.join(BASE_DIR, "cgkv/localsettings.py")
if os.path.exists(localsettingspath):
    from cgkv.localsettings import *
