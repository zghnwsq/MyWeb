"""
Django settings for MyWeb project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import time

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h%nbdt8e$0iyz_x-&us*@jhr&qqggiy2txbf4*vx)5*-$_2h!='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.0.*']


# Application definition

INSTALLED_APPS = [
    'autotest.apps.AutotestConfig',
    'login.apps.LoginConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'mod_wsgi.server',  # apache+mod_wsgi in windows
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

ROOT_URLCONF = 'MyWeb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'MyWeb/templates'), os.path.join('D:/PythonProject/zbh/Report'),
                 os.path.join('D:/PythonProject/EasySelenium/Report'), os.path.join('D:/PythonProject/MyWeb/Report')],  # 加入报告路径，用于展示报告
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

WSGI_APPLICATION = 'MyWeb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    # 'autotest': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # },
    # 'autotest': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': 'D:\\PythonProject\\zbh\\autotest.sqlite',
    # }
    'autotest': {
        'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': 'D:\\PythonProject\\EasySelenium\\autotest.db',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    # 'mysql': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'HOST': '',
    #     'PORT': '',
    #     'NAME': '',
    #     'USER': '',
    #     'PASSWORD': '',
    #     'OPTIONS': {
    #         'default-character-set': 'utf8'
    #     },
    # }
}

DATABASE_ROUTERS = []

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'UTC'
# TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "layui"),
    os.path.join(BASE_DIR, "MyWeb/statics"),
    os.path.join(BASE_DIR, "MyWeb/statics/hightcharts"),
    os.path.join(BASE_DIR, "Report"),
    'D:/PythonProject/EasySelenium/Report',
    # os.path.join(BASE_DIR, "layui/imges/face"),
    # os.path.join(BASE_DIR, "layui/css/modules/laydate/default"),
    # os.path.join(BASE_DIR, "layui/css/modules/layer/default"),
]

# STATIC_ROOT = 'D:/PythonProject/MyWeb/Statics'

LOGIN_REDIRECT_URL = '/index/'
LOGIN_URL = '/login/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60*30

# today = time.strftime("%Y%m%d", time.localtime())
LOG_FILE = os.path.join(BASE_DIR, 'log')
if not os.path.exists(os.path.join(BASE_DIR, 'log')):
    os.mkdir(os.path.join(BASE_DIR, 'log'))
LOG_FILE_NAME = 'http.log'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{asctime} {filename:s} {module} {funcName:s} {levelname} {message}',
            'style': '{',
        },
        'detail': {
            'format': '{asctime} {process:d} {thread:d} {pathname:s} {module} {funcName:s} {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            # 'class': 'logging.FileHandler',
            'class': 'logging.handlers.TimedRotatingFileHandler',  # 改为日志滚动
            'formatter': 'default',
            'filename': os.path.join(LOG_FILE, LOG_FILE_NAME),
            'when': 'H',
            'interval': 6,
            'backupCount': 100,
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'formatter': 'default',
            'propagate': True,
        },
        # 'django.request': {
        #     'handlers': ['file'],
        #     'level': 'INFO',
        #     'formatter': 'default',
        #     'propagate': True,
        # },
        # 'django.server': {
        #     'handlers': ['file'],
        #     'level': 'INFO',
        #     'formatter': 'default',
        #     'propagate': True,
        # },
    },
}

# 自定义参数
WEATHER_API_KEY = 'aJkb6gTZrkEqnAQh'
CITY_LOCATION = '121.46924,31.22986'

