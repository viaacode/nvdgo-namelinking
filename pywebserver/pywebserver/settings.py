"""
Django settings for pywebserver project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import dj_database_url
from pythonmodules.config import Config


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'arm5qft%(q#w3*41^6xyhe1*0-^myo=$cm!$p!pd2!22wdx^03'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'do-tst-mke-01.do.viaa.be',
    '::1',
    'localhost',
    '127.0.0.1',
    'nvdgo-linking.py',
    'web'
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'attestation.apps.AttestationConfig',
    'static_precompiler'
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'static_precompiler.finders.StaticPrecompilerFinder',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pywebserver.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'pywebserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

conf = Config(section='db')

DATABASES = {
    'default': dj_database_url.config(default=conf.connection_url)
}
# DATABASES['default']['ENGINE'] = 'psqlextra.backend'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/pywebserver_cache',
    },
    'MediaHaven': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/tmp/pywebserver_cache/mediahaven',
        'TIMEOUT': 31536000,  # cache for a year
        'OPTIONS': {
            'MAX_ENTRIES': 10000
        }
    },
    'stats': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAXENTRIES': 50,
        },
        'VERSION': 9
    }
}
#disable for a bit
# CACHES['stats']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'

log_screen = {
    'level': 'DEBUG',
    'handlers': ['console'],
    'propagate': False,
}

log_all = {
    'level': 'DEBUG',
    'handlers': ['console', 'file'],
    'propagate': False,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s @ %(filename)s(%(funcName)s):%(lineno)d',
        },
        'console': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(asctime)s %(name)-12s %(log_color)s%(levelname)-8s %(message)s @ %(filename)s:%(lineno)d (%(funcName)s)',
            'log_colors': {
                'DEBUG': 'bold_black',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
    },

    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django-debug.log'),
            'formatter': 'file',
        },

        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },

    'loggers': {
        'pythonmodules.mediahaven': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        'requests.packages.urllib3': log_all,
        'http_client.HTTPConnection': log_all,
        'pythonmodules': log_screen,
        'attestation.stats': log_all,
        'pythonmodules.decorators': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'lib.matcher': log_screen,
        'pysolr': {
            'level': 'WARN',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


