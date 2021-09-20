from django.urls import path
from ecommerce import views
from ecommerce import recommendation
from ecommerce.views import ItemDetailView, CartDetailView, OrderSummaryView

app_name = 'ecommerce'

urlpatterns = [
    path('register/',views.registerView,name='register'),
    path('login/',views.loginView,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('homepage/',views.goHompage,name='homepage'),
    path('catalog/',views.goCatalog, name='catalog'),
    path('donate/',views.requestDonation, name='donate'),
    path('cart/',CartDetailView.as_view(), name='cart'),
    path('profile/<slug:section>/',views.goProfile, name='profile'),
    path('view/<slug>/', views.updateViewToItem, name='view'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('update-cart/', views.updateCart, name='update-cart'),
    path('add-to-cart/<slug>/',views.addToCart, name='add-to-cart'),
    path('remove-from-cart/<slug>/',views.removeFromCart, name='remove-from-cart'),
    path('checkout/', OrderSummaryView.as_view(), name='checkout'),
    path('update/', views.updateProfile, name='update'),
    path('complete/', views.payment_complete, name="complete"),
    path('search/', views.searchProduct, name="search"),
]

    # path('about/',views.goAbout, name='about'),
