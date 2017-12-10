"""
Django settings for via1 project on Heroku. For more info, see:
https://github.com/heroku/heroku-django-template

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "n9cxfco)5l_u73_4=0z5^-rr878t)2%c&t6%f83nvz73d(al))"

# SECURITY WARNING: don't run with debug turned on in production!
# TODO Turn this to False once we officially deploy
DEBUG = True

# Application definition

INSTALLED_APPS = [
    'registration.apps.RegistrationConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'via1.urls'

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
                'django.template.context_processors.request',
            ],
            'debug': DEBUG,
            'builtins': [
                'django.contrib.staticfiles.templatetags.staticfiles',      # Makes it so we don't have to {% load static %} on every template
            ],
        },
    },
]

WSGI_APPLICATION = 'via1.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    # Uncomment this one and comment out the other ones before pushing code to Heroku
    #'default': dj_database_url.config()

    # I recommend using this setting (Postgres) for dev because it matches the prod environment
     'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'via1',
         'USER': 'postgres',
         'PASSWORD': 'postgres',
         'HOST': 'localhost',
         'PORT': 5432
     }

    # This is the default setting. Leaving this here in-case you want to test with SQLite
    # 'default': {
    #         'ENGINE': 'django.db.backends.sqlite3',
    #         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
}

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Change 'default' database configuration with $DATABASE_URL.
DATABASES['default'].update(dj_database_url.config(conn_max_age=500))

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
]

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Where the user will be redirected upon a successful login
LOGIN_REDIRECT_URL = '/registration/home'

# Points to the location of the custom User (in Models.py)
AUTH_USER_MODEL = 'registration.User'

# For testing
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# NEED TO CHANGE THIS TO THE OFFICIAL UVSA-EMAIL WHEN WE LAUNCH
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@uvsamidwest.org'
EMAIL_HOST_PASSWORD = 'NoReplyxD'   # If this password doesn't work, ask an ED to reset it
EMAIL_USE_TLS = True


PAYPAL_SANDBOX_CLIENT_ID = "Ab27EY00zHVJxLJOXzg5qsD-BPhmZN5eKEtl9t-JZLx3FWDedGCcv_dY3ThY0WyokpArcbGNB-fKmHOV"
PAYPAL_SANDBOX_CLIENT_SECRET = "EAUCTgUATGWkIRJGMJBp1iYJ9AnvJPcoOxr-hL8FOuvTOTFsLeeSWIc5DhZlVONwxOLJKRjw5hgtLYA3"

PAYPAL_LIVE_CLIENT_ID = "AcX7YmOuHyEA6dZhpNEYeaU1hni05wB3dVyPFEEReHgzByz3B-BA8YXclcsY_WiCws3k-2K99JRRl_5I"
PAYPAL_LIVE_CLIENT_SECRET = "EACFieh0hoaWUjw5NFEGKeg5LTeiOtMrxQUBl7oocj0kgLmGnuChT5LHCbb7SlVHK9bGRK78MwOWZyya"