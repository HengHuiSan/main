from django.urls import path
from account import views

app_name = 'account'

urlpatterns = [
    path('register/',views.registerView,name='register'),
    path('user/login/',views.loginView,name='user_login'),
    path('admin/login/',views.loginView,name='admin_login'),
    path('logout/',views.logoutUser,name='logout'),
]
