# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xtij@)g$t19zj^l$u)gud6-9!0436!=cp&8prn(ahk9)68(j&+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

TEMPLATE_LOADERS = (
    ('pyjade.ext.django.Loader',(
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
            ],
        },
    },
]

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = ('127.0.0.1',)

APPEND_SLASH = False

CORS_ORIGIN_WHITELIST = (
  'localhost:8080',
)

# Application definition

INSTALLED_APPS = (
  'flat',
  'django.contrib.admin',
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
  'debug_toolbar'
)

MIDDLEWARE_CLASSES = (
  'corsheaders.middleware.CorsMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  #'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'base.middleware.ProfileMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware'
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
LOGIN_REDIRECT_URL = '/login'

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

LANGUAGE_CODE = 'nl-nl'

TIME_ZONE = 'UTC'

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
)

#
# application settings
#

NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = '6LdTEBsTAAAAAEGoRs_P10MVgylFKuxHnKZzB-m1'
RECAPTCHA_PRIVATE_KEY = '6LdTEBsTAAAAAGdjKkSYNWRSx_5w5fCEZGrZIkyk'
#
# localsettings loading
#

localsettingspath = os.path.join(BASE_DIR, "cgkv/localsettings.py")
if os.path.exists(localsettingspath):
    from cgkv.localsettings import *
