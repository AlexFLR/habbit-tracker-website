from django.urls import path
from . import views


urlpatterns = [
    path('', views.home,name='home'),
    path('login/', views.login,name='login'),
    path('logout/', views.logout_user,name='logout_user'),
    #path('register/', views.register_user,name='register_user'),
    path('habits/', views.habits,name='habits'),
    path('analytics/', views.analytics,name='analytics'),



]
