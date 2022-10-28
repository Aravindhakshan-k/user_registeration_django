from django.contrib import admin
from django.urls import path
from registerApp import views

urlpatterns = [
    path('',views.welcome, name='welcome'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout),
    path('activate/<uidb64>/<token>', views.activate, name='activate')
]