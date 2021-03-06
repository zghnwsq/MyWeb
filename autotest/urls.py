from django.urls import path
from . import views

app_name = 'autotest'
urlpatterns = [
    path('run_his/', views.RunHisV.as_view(), name='run_his'),
    path('run_his/get/', views.get_run_his, name='get_his'),
    path('run_his/report/', views.get_report, name='report'),
    path('run_count/', views.RunCountV.as_view(), name='run_count'),
    path('run_count/get/', views.get_run_count, name='get_count'),
    path('run_his_chart/', views.RunHisChartV.as_view(), name='run_his_chart'),
    path('run_his_chart/data/', views.get_run_his_chart_data, name='run_his_chart_data'),
    path('execution/', views.ExecutionV.as_view(), name='execution'),
    path('jobs/get/', views.get_jobs, name='get_jobs'),
    path('job/exec/', views.exec_job, name='exec_job'),
    path('job/new_layer/', views.new_job_html, name='new_job_html'),
    path('job/save/', views.save_new_job, name='save_new_job'),
    path('job/del/', views.del_job, name='del_job'),
]

