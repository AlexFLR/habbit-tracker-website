from django.urls import path
from . import views


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




]
