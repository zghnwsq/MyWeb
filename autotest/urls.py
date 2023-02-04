from django.urls import path
from . import views

app_name = 'autotest'
urlpatterns = [
    path('run_his/', views.RunHisV.as_view(), name='run_his'),
    path('run_his/get/', views.get_run_his, name='get_his'),
    path('run_his/report/', views.get_report, name='report'),
    path('run_his/comment/', views.update_runhis_comment, name='update_runhis_comment'),
    path('execution/', views.ExecutionV.as_view(), name='execution'),
    path('jobs/get/', views.get_jobs, name='get_jobs'),
    path('job/exec/', views.exec_job, name='exec_job'),
    path('job/new_layer/', views.new_job_html, name='new_job_html'),
    path('job/save/', views.save_new_job, name='save_new_job'),
    path('job/del/', views.del_job, name='del_job'),
    path('node/register/', views.regsiter_node, name='register_node'),
    path('suite/count/', views.update_suite_cases_count, name='update_suite_case_count'),
    path('datasource/update/', views.update_ds, name='update_ds'),
    path('datasource/', views.DataSourceV.as_view(), name='datasource'),
    path('datasource/get/', views.get_ds, name='get_ds'),
    path('datasource/download/', views.download_ds, name='download_ds'),
    path('datasource/preview/', views.DataSourcePreviewV.as_view(), name='ds_preview'),
]

