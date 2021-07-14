from django.urls import path
from MyWeb import settings
from . import views

app_name = 'DataPanel'
urlpatterns = [
    path('run_count/', views.RunCountV.as_view(), name='run_count'),
    path('run_count/get/', views.get_run_count, name='get_count'),
    path('run_his_chart/', views.RunHisChartV.as_view(), name='run_his_chart'),
    path('run_his_chart/data/', views.get_run_his_chart_data, name='run_his_chart_data'),
    ]

