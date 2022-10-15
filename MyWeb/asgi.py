"""
@Time ： 2022/10/11 13:52
@Auth ： Ted
@File ：asgi.py.py
@IDE ：PyCharm
ASGI config for ApiHub project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyWeb.settings')

application = get_asgi_application()
