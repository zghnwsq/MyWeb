from django.urls import path
from . import views

app_name = 'sysadmin'
urlpatterns = [
    path('nodes/', views.NodesV.as_view(), name='node_manage'),
    path('nodes/get/', views.get_nodes, name='get_nodes'),
    path('nodes/stop/', views.stop_node, name='stop_node'),
    path('nodes/update/', views.update_node, name='update_node'),
    path('nodes/del/', views.del_node, name='del_node'),

]
