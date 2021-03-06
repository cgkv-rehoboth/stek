# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

from machina import get_apps as get_machina_apps
from machina import MACHINA_MAIN_TEMPLATE_DIR, MACHINA_MAIN_STATIC_DIR

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''********'

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
                'django.template.context_processors.request',
            ],
        },
    },
]

LOCALE_PATHS = [
  # Custom Machina translation
  os.path.join(BASE_DIR, "../src/custommachina/locale/"),
]

# People who get code error notifications.
# In the format (('Full Name', 'email@example.com'), ('Full Name', 'anotheremail@example.com'))
ADMINS = (('Website Team', 'no@robots.nl'))

ALLOWED_HOSTS = ['*']  # todo: make default to rehobothkerkwoerden.nl
CORS_ORIGIN_ALLOW_ALL = True

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/django-messages'

DEFAULT_FROM_EMAIL = 'Rehobothkerk Woerden <no@robots.nl>'

# Tuple of IP addresses, as strings, that:
#   * See debug comments, when DEBUG is true
#   * Receive x-headers
INTERNAL_IPS = ('127.0.0.1',)

APPEND_SLASH = False

CORS_ORIGIN_WHITELIST = (
  'localhost:8080',
)

# Application definition

INSTALLED_APPS = [
  'flat',
  'django.contrib.sites',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.sitemaps',
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
  'ckeditor',
  'compressor',
  'easy_thumbnails',
  'fiber',
  'django.contrib.admin',
] + get_machina_apps()

MIDDLEWARE_CLASSES = (
  'django.middleware.security.SecurityMiddleware',
  'corsheaders.middleware.CorsMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'base.middleware.ProfileMiddleware',
  'whitenoise.middleware.WhiteNoiseMiddleware',
  'machina.apps.forum_permission.middleware.ForumPermissionMiddleware',
  'fiber.middleware.ObfuscateEmailAddressMiddleware',
  'fiber.middleware.AdminPageMiddleware',

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

LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/dashboard/'

WSGI_APPLICATION = 'cgkv.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.mysql',
    'NAME': '********',
    'USER': '********',
    'PASSWORD': '********',
    'HOST': 'localhost',
    'PORT': '3306',
  }
}

# Internationalization
internationalizationpath = os.path.join(BASE_DIR, "cgkv/internationalization.py")
if os.path.exists(internationalizationpath):
    from cgkv.internationalization import *


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
# Security
#
AUTH_PASSWORD_VALIDATORS = [
  {
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    'OPTIONS': {
      'min_length': 8,
    }
  },
  {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
  },
  {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
  },
]

SECURE_SSL_REDIRECT = True

#
# application settings
#

NOCAPTCHA = True
RECAPTCHA_PUBLIC_KEY = ''********'
RECAPTCHA_PRIVATE_KEY = ''********'

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

MACHINA_FORUM_NAME = "Rehobothkerk Woerden | Forum"

MACHINA_MARKUP_LANGUAGE = None
MACHINA_MARKUP_WIDGET = 'ckeditor.widgets.CKEditorWidget'

CKEDITOR_CONFIGS = {
  'default': {
    'toolbar': 'Custom',
    'toolbar_Custom': [
      ['Format'],
      ['TextColor', '-', 'Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
      ['NumberedList', 'BulletedList', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
      ['Link', 'Unlink', 'Image', '-', 'Table', 'HorizontalRule'],
      ['Smiley', 'SpecialChar'],
      ['Undo', 'Redo'],
    ],
    'width': '100%',
    #'allowedContent': ['p', 'strong', 'i', 's', 'u', 'span', 'div', 'ul', 'li', 'ol', 'em', 'a', 'table', 'thead', 'tbody', 'caption', 'tr', 'td', 'th', 'img', 'br', 'hr', 'pr', 'address', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
  },
  'email': {
    'toolbar'       : 'Custom_email',
    'toolbar_Custom_email': [
      ['Format'],
      ['TextColor', '-', 'Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
      ['NumberedList', 'BulletedList', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
      ['Link', 'Unlink', 'Image', '-', 'Table', 'HorizontalRule'],
      ['SpecialChar'],
      ['Undo', 'Redo'],
    ],
    'width'         : '100%',
    # 'allowedContent': ['p', 'strong', 'i', 's', 'u', 'span', 'div', 'ul', 'li', 'ol', 'em', 'a', 'table', 'thead', 'tbody', 'caption', 'tr', 'td', 'th', 'img', 'br', 'hr', 'pr', 'address', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
  },
  'no_files': {
    'toolbar'       : 'Customno_files',
    'toolbar_Customno_files': [
      ['Format'],
      ['TextColor', '-', 'Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'],
      ['NumberedList', 'BulletedList', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight'],
      ['Link', 'Unlink', '-', 'Table', 'HorizontalRule'],
      ['SpecialChar'],
      ['Undo', 'Redo'],
    ],
    'width'         : '100%',
    # 'allowedContent': ['p', 'strong', 'i', 's', 'u', 'span', 'div', 'ul', 'li', 'ol', 'em', 'a', 'table', 'thead', 'tbody', 'caption', 'tr', 'td', 'th', 'img', 'br', 'hr', 'pr', 'address', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
  }
}

MACHINA_DEFAULT_AUTHENTICATED_USER_FORUM_PERMISSIONS = [
    'can_see_forum',
    'can_read_forum',
    'can_start_new_topics',
    'can_reply_to_topics',
    'can_edit_own_posts',
    'can_delete_own_posts',
    'can_post_without_approval',
    'can_create_polls',
    'can_vote_in_polls',
    'can_attach_file',
    'can_download_file',
]

#
# Fiber settings
#

# Set default template to render
FIBER_DEFAULT_TEMPLATE = 'public_layout.html'

# Set default upload location
FIBER_IMAGES_DIR = 'fiber/uploads/images'
FIBER_FILES_DIR = 'fiber/uploads/files'

FIBER_TEMPLATE_CHOICES = (
    ('', 'Standaard sjabloom'),
    ('anbi.html', 'Vaste ANBI'),
    ('list.html', 'Vaste diensten overzicht'),
    ('kerktijden.html', 'Vaste kerktijden'),
    ('kindercreche.html', 'Vaste kindercreche'),
    ('orgel.html', 'Vaste orgel'),
    ('index.html', 'Vaste voorpagina'),
)

# Set some extra options for pages
FIBER_METADATA_PAGE_SCHEMA = {
  'hide_title': {
    'widget': 'select',
    'values': ['nee (standaard)', 'ja'],
  },
}

# Set some extra options for contentitems (especially for jaarthema items)
FIBER_METADATA_CONTENT_SCHEMA = {
  'hide_jaarthema': {
    'widget': 'select',
    'values': ['nee (standaard)', 'ja'],
  },
  'jaarthema_background_url': {
    'widget': 'textfield',
  }
}

# Disable Fiber on most backend pages
FIBER_EXCLUDE_URLS = [
  '^rooster*',
  '^adresboek*',
  '^forum*',
  '^profiel*',
  '^team*',
]

# Configure compressor
STATICFILES_FINDERS = [
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
  'compressor.finders.CompressorFinder',
]


#
# localsettings loading
#

localsettingspath = os.path.join(BASE_DIR, "cgkv/localsettings.py")
if os.path.exists(localsettingspath):
    from cgkv.localsettings import *
