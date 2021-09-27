from django.urls import path
from ecommerce import views

app_name = 'ecommerce'

urlpatterns = [
    # For recommendation and showing homepage
    path('homepage/',views.goHompage,name='homepage'),

    # For showing catalog page
    path('catalog/',views.goCatalog, name='catalog'),

    # For showing product listing page
    path('product/<slug>/',views.showProduct, name='product'),

    # For updating the view of a product
    path('view/<slug>/', views.updateViewToItem, name='view'),

    # For searching products
    path('search/', views.searchProduct, name="search"),

    # For showing cart page
    path('cart/',views.showCart, name='cart'),

    # For adding, updating and deleting cart items 
    path('update-cart/', views.updateCart, name='update-cart'),
    path('add-to-cart/<slug>/',views.addToCart, name='add-to-cart'),
    path('remove-from-cart/<slug>/',views.removeFromCart, name='remove-from-cart'),

    # For checkout all the cart items and direct to payment page
    path('checkout/', views.showOrderSummary, name='checkout'),
    # For making payment
    path('complete/', views.payment_complete, name="complete"),

    # For requesting furniture donation
    path('donate/',views.requestDonation, name='donate'),

    # For showing profile page
    path('profile/<slug:section>/',views.goProfile, name='profile'),
    # For updating profile
    path('update/', views.updateProfile, name='update'),
]

