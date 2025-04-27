from django.urls import path
from . import views
from .views import (
    dataexplorer_upload_view,
    dataexplorer_select_view,
    dataexplorer_graph_view,
    dataexplorer_download_view
)



urlpatterns = [
    path('', views.home,name='home'),
    path('login/', views.login,name='login'),
    path('logout/', views.logout_user,name='logout_user'),
    #path('register/', views.register_user,name='register_user'),
    path('habits/', views.habits,name='habits'),
    path('analytics/', views.analytics,name='analytics'),
    path('add_record/', views.add_record,name='add_record'),
    path('edit/<int:habit_id>/', views.edit_habit, name='edit_habit'),
    path('delete/<int:habit_id>/', views.delete_habit, name='delete_habit'),
    path('toggle/<int:habit_id>/', views.toggle_habit_completion, name='toggle_habit'),
    path('dataexplorer/upload/', views.dataexplorer_upload_view, name='dataexplorer_upload'),
    path('dataexplorer/select/', views.dataexplorer_select_view, name='dataexplorer_select'),
    path('dataexplorer/graph/', dataexplorer_graph_view, name='dataexplorer_graph'),
    path('dataexplorer/download/', dataexplorer_download_view, name='dataexplorer_download'),


]
