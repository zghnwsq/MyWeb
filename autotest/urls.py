from django.urls import path
from . import views

app_name = 'autotest'
urlpatterns = [
    path('run_his/', views.RunHisV.as_view(), name='run_his'),
    path('run_his/get/', views.get_run_his, name='get'),
    path('run_his/report/', views.get_report, name='report')
]

