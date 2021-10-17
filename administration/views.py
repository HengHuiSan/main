from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from ecommerce.models import *
import os


# For displaying the product management page
def prodManagement(request):
    context = {
        'furniture':Furniture.objects.all(),
        'category':Category.objects.all()
    }
    return render(request, 'admin/prod_management.html', context)


def saveProduct(request):
    # When admin is saving the new or updated product records
    if request.method == 'POST':
        id = str(request.POST['txtFid']).lstrip()

        # Admin updates the product
        if Furniture.objects.filter(furnitureId=id).exists():
            item = Furniture.objects.get(furnitureId=id)
            if len(request.FILES) != 0:
                # remove old image
                if os.path.exists(item.furnitureImg.path):
                    os.remove(item.furnitureImg.path)  

            messages.success(request, 'Item is updated.')
        # Admin adds new product
        else:
            item = Furniture()
            messages.success(request, 'Item is added.')

        # Save product data into database
        item.furnitureId = id
        item.furnitureName = request.POST['txtName']
        item.furnitureGenres = request.POST['txtGenres']
        item.unitPrice = request.POST['txtUnitPrice']
        item.stock = request.POST['txtStock']
        item.categoryId = Category.objects.get(categoryId=request.POST['ddlCategory'])
        item.slug = id
        item.furnitureImg = request.FILES['imgFurniture']
        item.save()

        return redirect('administration:dashboard')
    # When admin opens the 'add new product' page
    else:
        # random-generated an ID for new product
        fid = str(random.randint(10000000, 99999999))

        # Check whether the ID exist in 'Furniture' table
        while Furniture.objects.filter(furnitureId=fid).exists():
            fid = str(random.randint(10000000, 99999999))

        category = Category.objects.all()

        context = {
            'fid':fid,
            'category':category
        }

        return render(request, 'admin/item.html', context)
    
# For displaying product details page with default field values of the item selected  
def editProduct(request, slug):
    item = get_object_or_404(Furniture, slug=slug)
    category = Category.objects.all()

    context = {
        'object':item, 
        'category':category
    }

    return render(request, 'admin/item.html', context)

# For deleting seleted product
def deleteItem(request, slug):
    item = get_object_or_404(Furniture, slug=slug)

    # remove item's image in local file
    if os.path.exists(item.furnitureImg.path):
        os.remove(item.furnitureImg.path)  

    # delete item
    item.delete()

    messages.success(request, 'Item is deleted.')
    return redirect('administration:dashboard')

# For displaying order management page
def orderManagement(request):
    context = {
        'order':Order.objects.all().order_by('-orderDate')
    }
    return render(request, 'admin/order_management.html', context)

# For managing customer order
def processOrder(request, slug, action):   
    order = get_object_or_404(Order, slug=slug)

    # if admin just views the order
    if action == 'view':
        item = Order_Products.objects.filter(orderId = order.orderId)
        context = {
            'object':order,
            'item':item
        }
        return render(request, 'admin/order.html', context)
    # if the order items are ready to be delivered
    else:
        order.isDelivered = True
        order.save()
    
    return redirect('administration:order')

# For displaying donation request management page
def donationManagement(request):
    context = {
        'donation':Donation.objects.all().order_by('-dateCreated')
    }
    return render(request, 'admin/donation_management.html', context)

# For managing donation request
def processDonation(request, slug, approve):
    donation = get_object_or_404(Donation, slug=slug)

    if approve == 'True':
        donation.isApproved = True
    else :
        donation.isApproved = False
    
    donation.save()

    return redirect('administration:donation')





