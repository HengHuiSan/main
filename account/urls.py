from django.urls import path
from account import views

app_name = 'account'

urlpatterns = [
    path('register/',views.registerView,name='register'),
    path('login/',views.loginView,name='login'),
    path('logout/',views.logoutUser,name='logout'),
]
