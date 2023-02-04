"""
Django settings for MyWeb project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
# import time
from os import environ

if environ.get('ENV', None) == 'SERVER':
    from .server import *
else:
    from .dev import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

# ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.0.150', '192.168.50.211', '*']


# Application definition

INSTALLED_APPS = [
    'DataPanel.apps.DatapanelConfig',
    'ApiTest.apps.ApitestConfig',
    'SysAdmin.apps.SysadminConfig',
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

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [os.path.join(BASE_DIR, 'MyWeb/templates')],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

WSGI_APPLICATION = 'MyWeb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     # 'default': {
#     #     'ENGINE': 'django.db.backends.sqlite3',
#     #     # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     #     'NAME': 'D:\\PythonProject\\myweb.sqlite3'
#     # },
#     # aliyun
#     # 'default': {
#     #     'ENGINE': 'django.db.backends.mysql',
#     #     'HOST': '8.136.125.0',
#     #     'PORT': 9306,
#     #     'NAME': 'myweb',
#     #     'USER': environ.get('MYSQL_USER'),
#     #     'PASSWORD': environ.get('MYSQL_PWD'),
#     #     'CONN_MAX_AGE': 30*60,  # 数据库连接空闲时间. 复用连接，避免mysql反向解析主机名耗时太长
#         # 'OPTIONS': {
#         #     'default-character-set': 'utf8'
#         # },
#     # },
#     # local centos7
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'HOST': '192.168.0.103',
#         'PORT': 9306,
#         'NAME': 'myweb',
#         'USER': 'myweb',
#         'PASSWORD': environ.get('MYSQL_PWD'),
#         'CONN_MAX_AGE': 30 * 60,  # 数据库连接空闲时间. 复用连接，避免mysql反向解析主机名耗时太长
#     },
# }

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

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
#
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "layui"),
#     os.path.join(BASE_DIR, "MyWeb/statics"),
#     os.path.join(BASE_DIR, "MyWeb/statics/hightcharts"),
#     os.path.join(BASE_DIR, "Report"),
#     'D:/PythonProject/EasySelenium/Report',
# ]

# 部署生产前运行python manage.py collectstatic
STATIC_ROOT = os.path.join(BASE_DIR, "Statics")

LOGIN_REDIRECT_URL = '/index/'
LOGIN_URL = '/login/'

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60*30

# today = time.strftime("%Y%m%d", time.localtime())
LOG_PATH = os.path.join(BASE_DIR, 'log')
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)
LOG_FILE_NAME = 'http.log'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
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
            'filename': os.path.join(LOG_PATH, LOG_FILE_NAME),
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
# APSCHEDULER = 'off'
# DATA_SOURCE_ROOT = os.path.join(BASE_DIR, 'Upload', 'DS')
# MANAGER_GROUPS = ['管理员']
skycon_dict = {'CLEAR_DAY': '晴', 'CLEAR_NIGHT': '晴', 'PARTLY_CLOUDY_DAY': '多云',
               'PARTLY_CLOUDY_NIGHT': '多云', 'CLOUDY': '阴', 'LIGHT_HAZE': '轻度雾霾',
               'MODERATE_HAZE': '中度雾霾', 'HEAVY_HAZE': '重度雾霾', 'LIGHT_RAIN': '小雨',
               'MODERATE_RAIN': '中雨', 'HEAVY_RAIN': '大雨', 'STORM_RAIN': '暴雨', 'FOG': '雾',
               'LIGHT_SNOW': '小雪', 'MODERATE_SNOW': '中雪', 'HEAVY_SNOW': '大雪', 'STORM_SNOW': '暴雪',
               'DUST': '浮尘', 'SAND': '沙尘', 'WIND': '大风'}
skycon_icon_dict = {'CLEAR_DAY': 'icon-sunny', 'CLEAR_NIGHT': 'icon-moon',
                    'PARTLY_CLOUDY_DAY': 'icon-a-partlycloudy_01',
                    'PARTLY_CLOUDY_NIGHT': 'icon-a-cloudyatnight', 'CLOUDY': 'icon-cloudy',
                    'LIGHT_HAZE': 'icon-a-lighthaze', 'MODERATE_HAZE': 'icon-haze', 'HEAVY_HAZE': 'icon-a-moderatesmog',
                    'LIGHT_RAIN': 'icon-a-lightrain', 'MODERATE_RAIN': 'icon-a-moderaterain',
                    'HEAVY_RAIN': 'icon-a-heavyrain', 'STORM_RAIN': 'icon-rainstorm', 'FOG': 'icon-fog',
                    'LIGHT_SNOW': 'icon-a-slightsnow', 'MODERATE_SNOW': 'icon-a-mediumsnow',
                    'HEAVY_SNOW': 'icon-a-heavysnow', 'STORM_SNOW': 'icon-a-great-heavysnow',
                    'DUST': 'icon-dust', 'SAND': 'icon-a-sandblowing', 'WIND': 'icon-a-Strongduststorm'}
