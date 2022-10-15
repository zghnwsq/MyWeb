from django.urls import path
from . import views

app_name = 'ApiTest'
urlpatterns = [
    path('groups/', views.ApiGroupV.as_view(), name='api_group'),
    path('groups/get/', views.get_groups, name='get_group'),
    path('group/update/', views.update_group, name='update_group'),
    path('group/del/', views.del_group, name='del_group'),
    path('group/new/', views.new_group, name='new_group'),
    path('group/env/', views.get_group_env, name='group_env'),
    path('group/env/edit/', views.edit_group_env, name='edit_group_env'),
    path('group/env/del/', views.del_group_env, name='del_group_env'),
    path('cases/', views.ApiCaseV.as_view(), name='api_case'),
    path('cases/get/', views.get_cases, name='get_case'),
    path('case/duplicate/', views.duplicate_case, name='duplicate_case'),
    path('case/update/', views.update_case, name='update_case'),
    path('case/del/', views.del_case, name='del_case'),
    path('case/new/', views.new_case, name='new_case'),
    path('case/edit/', views.edit_case, name='edit_case'),
    path('case/steps/', views.get_steps, name='get_step'),
    path('case/attachment/', views.upload_attachment, name='upload_attachment'),
    path('case/ds/', views.case_ds_layer, name='case_ds'),
    path('case/ds/edit/', views.edit_case_ds, name='edit_case_ds'),
    path('case/ds/upload/', views.upload_case_param, name='upload_case_param'),
    path('case/ds/del/param/', views.del_case_param, name='del_case_ds_param'),
    path('case/ds/value/', views.case_ds_value_layer, name='case_ds_value'),
    path('case/ds/value/edit/', views.edit_case_ds_value, name='edit_case_ds_value'),
    path('case/ds/del/value/', views.del_case_ds_value, name='del_case_ds_value'),
    path('job/', views.ApiJobV.as_view(), name='api_job'),
    path('job/exec/', views.exec_job, name='exec_job'),
    path('results/', views.ApiResultV.as_view(), name='api_result'),
    path('result/get/', views.get_result, name='get_result'),
    path('result/case/', views.get_case_result, name='case_result'),
    path('result/steps/', views.get_steps_result, name='steps_result'),
    ]



