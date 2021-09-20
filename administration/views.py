from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, redirect, render
from ecommerce.models import *
import os


# Create your views here.

def loginView(request):
    msg = ''
    if request.method == 'POST':
        uname = request.POST.get('txtUname')
        passwd = request.POST.get('txtPasswd')

        if uname != '' and passwd != '':
            user = authenticate(request, username=uname, password=passwd)

            if user is not None:
                login(request, user)
                return redirect('administration:dashboard')
            else:
                msg = messages.error(request, 'Invalid username or password!')

    context = {'msg':msg}

    return render(request, 'account/login.html', context)

def prodManagement(request):
        context = {
            'furniture':Furniture.objects.all(),
            'category':Category.objects.all()
        }
        return render(request, 'admin/prod_management.html', context)


def orderManagement(request):
    context = {
        'order':Order.objects.all(),
    }
    return render(request, 'admin/order_management.html', context)

def donationManagement(request):
    context = {
        'donation':Donation.objects.all()
    }
    return render(request, 'admin/donation_management.html', context)


def saveProduct(request):
    if request.method == 'POST':
        id = str(request.POST['txtFid']).lstrip()
        print(id)

        full_path = request.get_full_path()
        print(full_path)

        if Furniture.objects.filter(furnitureId=id).exists():
            item = Furniture.objects.get(furnitureId=id)
            if len(request.FILES) != 0:
                # remove old image
                if os.path.exists(item.furnitureImg.path):
                    os.remove(item.furnitureImg.path)  

            messages.success(request, 'Item is updated.')
        else:
            item = Furniture()
            messages.success(request, 'Item is added.')

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
    else:
        fid = str(random.randint(10000000, 99999999))

        while Furniture.objects.filter(furnitureId=fid).exists():
            fid = str(random.randint(10000000, 99999999))

        category = Category.objects.all()

        context = {
            'fid':fid,
            'category':category
        }

        return render(request, 'admin/item.html', context)
    
    
def editProduct(request, slug):
    item = get_object_or_404(Furniture, slug=slug)
    category = Category.objects.all()

    context = {
        'object':item, 
        'category':category
    }

    return render(request, 'admin/item.html', context)

def deleteItem(request, slug):
    print('here')
    item = get_object_or_404(Furniture, slug=slug)

    if os.path.exists(item.furnitureImg.path):
        os.remove(item.furnitureImg.path)  

    item.delete()

    messages.success(request, 'Item is deleted.')
    return redirect('administration:dashboard')


def processOrder(request, slug, action):   
    order = get_object_or_404(Order, slug=slug)

    if action == 'view':
        item = Order_Products.objects.filter(orderId = order.orderId)
        context = {
            'object':order,
            'item':item
        }
        return render(request, 'admin/order.html', context)
    else :
        order.isDelivered = True
        order.save()
    
    return redirect('administration:order')


def processDonation(request, slug, approve):
    donation = get_object_or_404(Donation, slug=slug)

    if approve == 'True':
        donation.isApproved = True
    else :
        donation.isApproved = False
    
    donation.save()

    return redirect('administration:donation')
