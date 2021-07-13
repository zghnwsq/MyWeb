from django.urls import path
from MyWeb import settings
from . import views

app_name = 'ApiTest'
urlpatterns = [
    path('groups/', views.ApiGroupV.as_view(), name='api_group'),
    path('groups/get/', views.get_groups, name='get_group'),
    path('group/update/', views.update_group, name='update_group'),
    path('group/del/', views.del_group, name='del_group'),
    path('group/new/', views.new_group, name='new_group'),
    path('cases/', views.ApiCaseV.as_view(), name='api_case'),
    path('cases/get/', views.get_cases, name='get_case'),
    path('case/update/', views.update_case, name='update_case'),
    path('case/del/', views.del_case, name='del_case'),
    path('case/new/', views.new_case, name='new_case'),
    path('case/edit/', views.edit_case, name='edit_case'),
    path('case/steps/', views.get_steps, name='get_step'),
    path('job/', views.ApiJobV.as_view(), name='api_job'),
    path('job/exec/', views.exec_job, name='exec_job'),
    path('results/', views.ApiResultV.as_view(), name='api_result'),
    path('result/get/', views.get_result, name='get_result'),
    path('result/case/', views.get_case_result, name='case_result'),
    path('result/steps/', views.get_steps_result, name='steps_result'),
    ]



