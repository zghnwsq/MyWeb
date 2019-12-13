from django.urls import path
from . import views

app_name = 'login'
urlpatterns = [
    path('', views.LoginV.as_view(), name='login'),
    path('index/', views.IndexV.as_view(), name='index')
]

