from django.urls import path
from administration import views

app_name = 'administration'

urlpatterns = [
    path('',views.loginView,name='ad_login'),
    path('products/',views.prodManagement,name='dashboard'),
    path('orders/',views.orderManagement,name='order'),
    path('donations/',views.donationManagement,name='donation'),
    path('save-item/',views.saveProduct,name='save-item'),
    path('process-order/<slug>/<action>/',views.processOrder, name='process-order'),
    path('process-donation/<slug>/<approve>/',views.processDonation, name='process-donation'),
    path('edit-item/<slug>/',views.editProduct, name='edit-item'),
    path('delete-item/<slug>/',views.deleteItem, name='delete-item'),
]

