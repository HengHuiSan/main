from django.urls import path
from administration import views

app_name = 'administration'

urlpatterns = [
    # For showing product management
    path('products/',views.prodManagement,name='dashboard'),
    # For deleting items
    path('delete-item/<slug>/',views.deleteItem, name='delete-item'),
    # For setting default field values in product details page based on item selected 
    path('edit-item/<slug>/',views.editProduct, name='edit-item'),
    # For saving the updated and new items
    path('save-item/',views.saveProduct,name='save-item'),

    # For showing order management 
    path('orders/',views.orderManagement,name='order'),
    # For processing customer orders
    path('process-order/<slug>/<action>/',views.processOrder, name='process-order'),

    # For showing donation management 
    path('donations/',views.donationManagement,name='donation'),
    # For processing the donation requests
    path('process-donation/<slug>/<approve>/',views.processDonation, name='process-donation'),

]

