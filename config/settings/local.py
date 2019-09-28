import os

from django.conf import settings

import environ

from .base import *


env = environ.Env()
env.read_env(os.path.join(settings.BASE_DIR, '.env'))

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

DEBUG = True

SECRET_KEY = '3g-z%u7v(tsf($o15e8dt2q$(p*uh3hlxs5d_osk74_h@#fmiy'


ALLOWED_HOSTS = ['*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'postgres',
        'PORT': '5432',
        'ATOMIC_REQUEST': True,
    }
}

if DEBUG:
    def show_toolbar(request):
        return True

    INSTALLED_APPS += (
        'debug_toolbar',
        'django_extensions'
    )
    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    }

# AWS設定
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')

# staticファイル・mediaファイル共通
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = 'd1dh5gex9go1bi.cloudfront.net'

# staticファイル設定
# 静的ファイル配信用ディレクトリで、URLの一部になる
''' STATIC_URL = '/static/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
AWS_STORAGE_BUCKET_NAME = 'kyne-book-review.cf-static'

# mediaファイル設定
MEDIA_URL = '/media/'
# MEDIA_ROOTの代わりとなり、メディアファイルはここにアップロードされる
DEFAULT_FILE_STORAGE = 'config.storage_backends.S3MediaStorage'
MEDIA_AWS_STORAGE_BUCKET_NAME = 'kyne-book-review.cf-media'
MEDIAFILES_LOCATION = 'images/' '''


STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
