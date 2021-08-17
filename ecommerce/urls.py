from django.urls import path
from . import views

urlpatterns = [
    path('homepage',views.getHompage,name='homepage'),
    path('catalog',views.goCatalog, name='catalog'),
    path('donate',views.goDonate, name='donate'),
    path('about',views.goAbout, name='about'),
    # path('choose',views.generate_recommendation, name='choose'),

]