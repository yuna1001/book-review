import os

BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
PROJECT_NAME = os.path.basename(BASE_DIR)


SECRET_KEY = '3g-z%u7v(tsf($o15e8dt2q$(p*uh3hlxs5d_osk74_h@#fmiy'

DEBUG = True

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'accounts.apps.AccountsConfig',
    'book.apps.BookConfig',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.github',
    'bootstrap4',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

# HTTP→HTTPSにリダイレクト
#SECURE_SSL_REDIRECT = True

# フラッシュメッセージ設定
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'templates', 'allauth')],
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

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
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


LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1

# Staticファイル
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]


# メディアファイル
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# allauth setting
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Accountモデル ログアウト設定
AUTH_USER_MODEL = 'accounts.CustomUser'
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True  # ユーザ登録時の必須項目とする
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_USERNAME_REQUIRED = True  # ユーザ登録時の必須項目とする
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'

# SocialAccountモデル
SOCIALACCOUNT_EMAIL_VERIFICATION = ACCOUNT_EMAIL_VERIFICATION
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSocialSignupForm',
}
SOCIALACCOUNT_ADAPTER = 'accounts.adapter.CustomSocialAccountAdapter'
LOGIN_ON_EMAIL_CONFIRMATION = True
SOCIALACCOUNT_QUERY_EMAIL = False

# ログイン・ログアウト
LOGIN_REDIRECT_URL = 'book:search'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'

# Email
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_FORMS = {
    'signup': 'accounts.forms.CustomSignupForm',
}
ACCOUNT_ADAPTER = 'accounts.adapter.CustomAccountAdapter'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
