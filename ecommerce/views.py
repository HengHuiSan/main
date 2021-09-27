from datetime import datetime
from django.shortcuts import get_object_or_404, render
from ecommerce.models import *
from django.core.paginator import Paginator
from django.shortcuts import render, redirect 
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q 
import json
from ecommerce.recommendation import recommendToCustomer, recommendToNormalUser, recommendToNewUser

states = ['Johor','Kedah','Kelantan','Malacca',
          'Negeri Sembilan','Pahang','Perak','Perlis',
          'Pinang','Sabah','Sarawak','Selangor','Terangganu']


" ========== Homepage ========== "  

# @login_required(login_url='ecommerce:login')
def goHompage(request):
    # if user is customer, he will receive 3 types of recommendation
    if Order.objects.filter(userId=request.user).exists():
        cb_recommend_list, furniture_name, cf_recommend_list, popularity_recommend_list = recommendToCustomer(request.user, "customer")

        # because cb_recommend_list is a 2D array,
        # so require loop to get the objects based on furnitureIds
        # and then append the list of objects into cb_recommend_query[]
        cb_recommend_query = []
        for i in cb_recommend_list:
            cb_recommend_query.append(Furniture.objects.filter(pk__in=i))

        context = {
            'zip_data': zip(furniture_name, cb_recommend_query),
            'cf_recommend_list':Furniture.objects.filter(pk__in=cf_recommend_list), 
            'popularity_recommend_list':Furniture.objects.filter(pk__in=popularity_recommend_list)
        }

    # if user is normal user, he will receive 2 types of recommendation
    elif User_Views.objects.filter(userId=request.user):
        cf_recommend_list, popularity_recommend_list = recommendToNormalUser(request.user,'normal user')
        context = {
            'cf_recommend_list':Furniture.objects.filter(pk__in=cf_recommend_list), 
            'popularity_recommend_list':Furniture.objects.filter(pk__in=popularity_recommend_list)
        }
    # if user is normal user, he will receive one recommendation
    else:
        popularity_recommend_list = recommendToNewUser()
        context = {
            'popularity_recommend_list':Furniture.objects.filter(pk__in=popularity_recommend_list)
        }

    return render(request,'user/homepage.html', context)


" ========== Catalog ========== "  

def goCatalog(request): 
    # check URL parameter value - category ID(cid)   
    if request.method == 'GET' and 'cid' in request.GET:
        # when user changes the page for the first category
        # so need to set cid=1 because the URL has no value for cid
        # e.g. http://127.0.0.1:8000/ecommerce/catalog/?cid=&page=2
        if request.GET.get('cid') == '':
            cid = 1
        # get cid from URL parameter
        else:
            cid = request.GET.get('cid')       
        furniture = Furniture.objects.filter(categoryId_id=cid)

    # the first time displaying, URL has no parameter
    # e.g. http://127.0.0.1:8000/ecommerce/catalog/
    else:
        cid = 1
        furniture = Furniture.objects.filter(categoryId_id='1')
    
    # set page paging where one page can show 15 items
    paginator = Paginator(furniture, 15)
    page_number = request.GET.get('page')
    # return a Page object with the given index(page_number)  
    page = paginator.get_page(page_number)
    next_url = ''
    prev_url = ''

    # refresh URL while page changing
    if page.has_next():
        next_url = f'?cid='+str(cid)+'&page='+str(page.next_page_number())

    if page.has_previous():
        prev_url = f'?cid='+str(cid)+'&page='+str(page.previous_page_number())

    context = {"furniture":page.object_list, 
               "categories":Category.objects.all(), 
               "page":page,
               "next_page_url":next_url,
               "prev_page_url":prev_url}

    return render(request,'user/catalog.html', context)


" ========== Product Listings ========== " 

# showing product listing page
def showProduct(request, slug):
    # slug is retrieve from URL which can help identify the furniture by id
    item = get_object_or_404(Furniture, slug=slug)

    # get the top 8 items that similar to the selcted item
    related_items = Furniture.objects.filter(furnitureGenres__icontains = item.furnitureGenres)[:8]

    context = {
        'object': item, 
        'related_items': related_items
    }
    return render(request, 'user/product.html', context)

# Update item's view after clicking
def updateViewToItem(request, slug):
    item = get_object_or_404(Furniture, slug=slug)

    viewed_item = User_Views.objects.filter(userId=request.user, furnitureId=item)

    # if item exists in view table, its view count is added with one
    if viewed_item.exists():
        get_viewed_item = User_Views.objects.get(userId=request.user, furnitureId=item)
        get_viewed_item.viewCount += 1       
        get_viewed_item.save()
    # else, create a new record in 'view' table
    else:
        view = User_Views.objects.create(userId=request.user, furnitureId=item, viewCount=1)

    return redirect('ecommerce:product', slug=slug)


" ========== Shopping Cart ========== " 

# displaying shopping cart
def showCart(request):
    cart = Cart_Products.objects.filter(userId=request.user)
    amount = sum(item.quantity*item.furnitureId.unitPrice for item in cart)
    context = {
        'cart': cart, 
        'amount':amount
        }
    return render(request, 'user/cart.html', context)

def addToCart(request, slug):
    item = get_object_or_404(Furniture, slug=slug)
    item_in_cart = Cart_Products.objects.filter(userId=request.user, furnitureId=item)
    
    # if item exists, update quantity of the item
    if item_in_cart.exists():
        item_in_cart = Cart_Products.objects.get(userId=request.user, furnitureId=item)
        target_item = Furniture.objects.get(furnitureId=item_in_cart.furnitureId.furnitureId)

        if item_in_cart.quantity < target_item.stock:
            item_in_cart.quantity += 1
            item_in_cart.save()
            messages.success(request, "This item quantity was updated.")
        else:
            messages.info(request, "The quantity of " + item_in_cart.furnitureId.furnitureName + " is not sufficient.")
    # else create a new record to cart 'table'
    else:
        Cart_Products.objects.create(userId=request.user, furnitureId=item, quantity=1,slug=item.furnitureId)
        messages.success(request, "This item was added to your cart.")

    previous_url = request.META.get('HTTP_REFERER')

    if "homepage" in previous_url:
        return redirect('ecommerce:homepage')
    elif "catalog" in previous_url:
        return redirect('ecommerce:catalog')
    elif "product" in previous_url:
        return redirect('ecommerce:cart')

def removeFromCart(request, slug):
    # get the item of the target user based on slug(furnitureId)
    item = get_object_or_404(Cart_Products, userId=request.user.id, slug=slug)
    # retrieve the item from 'cart' table
    cart_item = Cart_Products.objects.filter(userId=request.user, furnitureId=item.furnitureId)

    cart_item.delete()
    messages.info(request, "This item was removed from your cart.")

    return redirect('ecommerce:cart')

# update modified quantity in cart page
def updateCart(request):
    if request.method == 'POST':
        cart_item = Cart_Products.objects.get(furnitureId=request.POST['furnitureId'], userId=request.user.id)
        cart_item.quantity =  request.POST['quantity']
        cart_item.save()

    return redirect('ecommerce:cart')


" ========== Checkout ========== "   

def showOrderSummary(request):
    cart = Cart_Products.objects.filter(userId=request.user)
    # calculate total amount
    amount = sum(item.quantity*item.furnitureId.unitPrice for item in cart)

    context = {
        'object': cart, 
        'amount':amount,
        'states':states,
        'profile':Customer_Profile.objects.get(custId=request.user.id)
        }

    return render(request, 'user/checkout.html', context)

def checkOrderId(id):
    if Order.objects.filter(orderId=id).exists():
        order_id = str(random.randint(1000000, 9999999))
        print("3" , order_id)
        checkOrderId(order_id)
    else:
        print("3" , id)
        return id

def payment_complete(request):
    # create order id
    order_id = str(random.randint(1000000, 9999999))
    print("asdas" , order_id)
    order_id = checkOrderId(order_id)

    body = json.loads(request.body)

    customer_name = body['form']['fname'] + ' ' + body['form']['lname']
    shipping_address = body['shipping']['addressLine1'] + ', ' + body['shipping']['addressLine2'] + ', ' + body['shipping']['postcode'] + ' ' + body['shipping']['town'] + ', ' + body['shipping']['state']
    
    # Create order and save order
    order = Order(
        orderId = order_id,
        orderDate = datetime.today(),
        name = customer_name,
        shippingAddress = shipping_address,
        phoneNo = body['form']['phoneNo'],
        email = body['form']['email'],
        amount = body['form']['total'], 
        userId = request.user,
        isDelivered = False,
        isReceived = False
    )
    order.save()

    # Change items in cart to order items
    # Insert list of order items into 'Order_Product' table
    order_items = Cart_Products.objects.filter(userId=request.user.id)
    Order_Products.objects.bulk_create([Order_Products(orderId=Order.objects.get(orderId=order_id), furnitureId=item.furnitureId, quantity=item.quantity) for item in order_items])
    
    # Clear cart
    clear_cart = Cart_Products.objects.filter(userId=request.user.id)
    clear_cart.delete()


" ========== Donation ========== " 

def requestDonation(request):
    if request.method == "POST":
        # save the donation request data
        donation = Donation(
            donationId = 'D' + str(random.randint(10000, 99999)),
            dateCreated = datetime.today(),
            name = request.POST.get('txtFname') + ' ' + request.POST.get('txtLname'),
            itemType = request.POST.get('txtType'),
            description = request.POST.get('txtDescription'),
            image = request.FILES['imgDonation'],
            yearPurchased = request.POST.get('txtYearPurchased'),
            originalPrice = request.POST.get('txtOriginalPrice'),
            userId = request.user,
            slug = 'D' + str(random.randint(10000, 99999))
        )
        donation.save()

        messages.success(request, "Donation Request Created Successfully!")
        return redirect('ecommerce:donate')

    return render(request, 'user/donation.html')


" ========== Profile ========== " 

def goProfile(request, section):
    if request.method == "POST":
        if (request.POST.get('btnUpdate')):
            updateProfile(request)
            return redirect('ecommerce:profile', section='account')
        elif (request.POST.get('btnReceive')):
            receiveOrder(request)
            return redirect('ecommerce:profile', section='order')
        elif (request.POST.get('btnSave')):
            updateAccount(request)
            return redirect('ecommerce:profile', section='settings')
    else:
        context = get_profile_data(request)

        return render(request,'user/profile.html', context)

def updateProfile(request):
    # update data in User modal
    user = User.objects.get(id = request.user.id)
    user.username = request.POST.get('txtUname')
    user.first_name = request.POST.get('txtFname')
    user.last_name = request.POST.get('txtLname')
    user.email = request.POST.get('txtEmail')
    user.save()

    # update data in Customer_Profile modal
    customer_profile = Customer_Profile.objects.filter(custId = request.user)

    if customer_profile.exists():
        customer = Customer_Profile.objects.get(custId = request.user)
        if len(request.FILES) != 0:
            # remove old image
            import os
            if os.path.exists(customer.profile_pic.path):
                os.remove(customer.profile_pic.path)
    else:
        customer = Customer_Profile()    
        customer.custId = request.user
    
    
    customer.phoneNo = request.POST['txtPhoneNo']
    customer.gender = request.POST['rbtnGender']
    customer.dob = request.POST['txtDOB']
    customer.address1 = request.POST['txtAddress1']
    customer.address2 = request.POST['txtAddress2']
    customer.town = request.POST['txtTown']
    customer.postcode = request.POST['txtPostCode']
    customer.state = request.POST['ddlState']
    customer.profile_pic = request.FILES['imgProfile']

    customer.save()

    return messages.success(request, "Your profile is updated!")

def updateAccount(request):
    # get the form data
    form = PasswordChangeForm(request.user, request.POST)
    
    if form.is_valid():
        user = form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one if
        # django.contrib.auth.middleware.SessionAuthenticationMiddleware
        # is enabled.
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Your password was successfully updated!')
        return redirect('ecommerce:profile', section='settings')
    else:
        messages.error(request, 'Please correct the error below.')

def receiveOrder(request):
    id = request.POST.get('hdfOrderId')
    order = Order.objects.get(orderId = id)
    order.isReceived = True
    order.save()

    return messages.success(request, "Thank you for supporting our business!")

def get_profile_data(request):
    # get the change password form
    form = PasswordChangeForm(request.user)

    # if user hasn't filled in the profile
    if Customer_Profile.objects.filter(custId=request.user).exists():
        # get user profile data
        profile_data = Customer_Profile.objects.get(custId=request.user)

        # get user's order records
        orders = Order.objects.filter(userId = request.user).order_by('-orderDate')
        items_list = []
        for order in orders:
            query = Order_Products.objects.filter(orderId = order.orderId)
            if(query.exists()):
                items_list.append(query)

        # get user's donation requests
        donations = Donation.objects.filter(userId = request.user).order_by('-dateCreated')

        context = {
            'customer':profile_data,
            'states':states,
            'order_data': zip(orders, items_list),
            'donations':donations,
            'form': form,
        }
    else:
        context = {
            'states':states,
            'form': form,
        }

    return context


" ========== Search Items ========== " 
def searchProduct(request):
    if request.method == 'POST':
        keyword = request.POST.get('txtSearch')
        # search if the keywords is case-insensitive matched with the name and genres
        furniture = Furniture.objects.filter(Q(furnitureName__icontains=keyword) | Q(furnitureGenres__icontains=keyword))

        if furniture.exists():
            context = {
                'furniture':furniture,
                'keyword':keyword
            }
            return render(request, 'user/search.html', context)
        else:
            messages.error(request, "Item not found")

    return render(request, 'user/search.html')







