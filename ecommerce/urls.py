from django.urls import path
from . import views
from . import recommendation
from .views import ItemDetailView, CartDetailView

app_name = 'ecommerce'

urlpatterns = [
    path('register/',views.registerView,name='register'),
    path('login/',views.loginView,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('homepage/',views.goHompage,name='homepage'),
    path('catalog/',views.goCatalog, name='catalog'),
    path('donate/',views.goDonate, name='donate'),
    path('about/',views.goAbout, name='about'),
    path('cart/',CartDetailView.as_view(), name='cart'),
    path('profile/',views.goProfile, name='profile'),
    path('view/<slug>/', views.updateViewToItem, name='view'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/',views.addToCart, name='add-to-cart'),
    path('remove-from-cart/<slug>/',views.removeFromCart, name='remove-from-cart'),
    path('update-cart', views.updateCart, name='update-cart')


]