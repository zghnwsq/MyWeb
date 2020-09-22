from django.urls import path
from . import views

app_name = 'login'
# handler403 = views.permission_denied

urlpatterns = [
    path('', views.LoginV.as_view(), name='login'),
    path('index/', views.IndexV.as_view(), name='index'),
    path('logout/', views.logout_v, name='logout'),
    path('403/', views.permission_denied, name='permission_denied'),
]

