"""MyWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from MyWeb import settings
from MyWeb.APScheduler import start_scheduler

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    path('login/', include('login.urls')),
    path('autotest/', include('autotest.urls', namespace='autotest')),
    path('sysadmin/', include('SysAdmin.urls', namespace='sysadmin')),
    path('apitest/', include('ApiTest.urls', namespace='apitest')),
    path('datapanel/', include('DataPanel.urls', namespace='datapanel')),
]

# 随项目启动运行
if settings.APSCHEDULER == 'on':
    start_scheduler()
