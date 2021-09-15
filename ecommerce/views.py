from datetime import date, datetime
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from ecommerce.models import *
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import render, redirect 
from .forms import UserRegistrationForm, DonationForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm


from django.db.models import Q # new

import json
from .recommendation import recommendToCustomer, recommendToNormalUser, recommendToNewUser


# ======= Account Authentication ======= #

def registerView(request):
    msg = ''
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                msg = messages.success(request, 'Register Successfully!')
            except ValidationError as e:
                print(e)
    else:
        form = UserRegistrationForm()

    context = {'form':form, 'msg':msg}

    return render(request, 'account/register.html', context)


def loginView(request):
    msg = ''
    if request.method == 'POST':
        uname = request.POST.get('txtUname')
        passwd = request.POST.get('txtPasswd')

        if uname != '' and passwd != '':
            user = authenticate(request, username=uname, password=passwd)

            if user is not None:
                login(request, user)
                return redirect('ecommerce:homepage')
            else:
                msg = messages.error(request, 'Invalid username or password!')

    context = {'msg':msg}

    return render(request, 'account/login.html', context)
    

def logoutUser(request):
    # try:
    #     del request.session['userId']
    # except KeyError:
    #     pass

	logout(request)
	return redirect('ecommerce:login')


# ======= Homepage ======= #

@login_required(login_url='ecommerce:login')
def goHompage(request):
    if Order.objects.filter(userId=request.user).exists():
        cb_recommend_list, furniture_name, cf_recommend_list, popularity_recommend_list = recommendToCustomer(request.user, "customer")

        cb_recommend_query = []
        for i in cb_recommend_list:
            cb_recommend_query.append(Furniture.objects.filter(pk__in=i))

        context = {
            'zip_data': zip(furniture_name, cb_recommend_query),
            'cf_recommend_list':Furniture.objects.filter(pk__in=cf_recommend_list), 
            'popularity_recommend_list':Furniture.objects.filter(pk__in=popularity_recommend_list)
        }
        print(furniture_name)
        print('here')
    elif User_Views.objects.filter(userId=request.user):
        cf_recommend_list, popularity_recommend_list = recommendToNormalUser(request.user,'normal user')
        context = {
            'cf_recommend_list':Furniture.objects.filter(pk__in=cf_recommend_list), 
            'popularity_recommend_list':Furniture.objects.filter(pk__in=popularity_recommend_list)
        }
        print('andsjaks')        
    else:
        popularity_recommend_list = recommendToNewUser()
        context = {
            'popularity_recommend_list':Furniture.objects.filter(pk__in=popularity_recommend_list)
        }
        print('dasds')

    return render(request,'user/homepage.html', context)


# ======= Catalog ======= #

def goCatalog(request): 
    page_number = request.GET.get('page', 1)
    cid=1
    
    if request.method == 'GET' and 'cid' in request.GET:
        if request.GET.get('cid') == '':
            cid = 1
        else:
            cid = request.GET.get('cid')       
        furniture = Furniture.objects.filter(categoryId_id=cid)
    else:
        furniture = Furniture.objects.filter(categoryId_id=1)
        
    paginator = Paginator(furniture, 15)
    page = paginator.get_page(page_number)
    category = Category.objects.all()


    if page.has_next():
        next_url = f'?cid='+str(cid)+'&page='+str(page.next_page_number())
    else:
        next_url = ''

    if page.has_previous():
        prev_url = f'?cid='+str(cid)+'&page='+str(page.previous_page_number())
    else:
        prev_url = ''

    context = {"furniture":page.object_list, 
               "categories":category, 
               "page":page,
               "next_page_url":next_url,
               "prev_page_url":prev_url}

    return render(request,'user/catalog.html', context)


# ======= Product Listings ======= #

# class ItemDetailView(DetailView):
#     model = Furniture
#     template_name = "user/product.html"
class ItemDetailView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            item = get_object_or_404(Furniture, slug=self.kwargs['slug'])
            related_items = Furniture.objects.filter(furnitureGenres__icontains = item.furnitureGenres)[:8]

            context = {
                'object': item, 
                'related_items': related_items
            }
            return render(self.request, 'user/product.html', context)
        except ObjectDoesNotExist:
            return redirect(self.request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

# View the item after clicking
def updateViewToItem(request, slug):
    item = get_object_or_404(Furniture, slug=slug)
    print(item)
    print("posttt")

    viewed_item = User_Views.objects.filter(userId=request.user, furnitureId=item)

    if viewed_item.exists():
        get_viewed_item = User_Views.objects.get(userId=request.user, furnitureId=item)
        get_viewed_item.viewCount += 1       
        get_viewed_item.save()
    else:
        view = User_Views.objects.create(userId=request.user, furnitureId=item, viewCount=1)

    return redirect('ecommerce:product', slug=slug)

# You may also like
def getRelatedItems(item):
    related_items = Furniture.objects.filter(furnitureGenres__icontains = item.furnitureGenres)

    return related_items


# ======= Shopping Cart ======= #

class CartDetailView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            cart = Cart_Products.objects.filter(userId=self.request.user)
            amount = sum(item.quantity*item.furnitureId.unitPrice for item in cart)
            context = {
                'cart': cart, 
                'amount':amount
                }
            return render(self.request, 'user/cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Your cart is empty")
            return redirect('ecommerce:cart')


def addToCart(request, slug):
    item = get_object_or_404(Furniture, slug=slug)
    item_in_cart = Cart_Products.objects.filter(userId=request.user, furnitureId=item)
    
    if item_in_cart.exists():
        item_in_cart = Cart_Products.objects.get(userId=request.user, furnitureId=item)
        target_item = Furniture.objects.get(furnitureId=item_in_cart.furnitureId.furnitureId)

        if item_in_cart.quantity < target_item.stock:
            item_in_cart.quantity += 1
            item_in_cart.save()
            messages.success(request, "This item quantity was updated.")
        else:
            messages.info(request, "The quantity of " + item_in_cart.furnitureId.furnitureName + " is not sufficient.")
    else:
        Cart_Products.objects.create(userId=request.user, furnitureId=item, quantity=1,slug=item.furnitureId)
        messages.success(request, "This item was added to your cart.")
    
    previous_url = request.META.get('HTTP_REFERER')
    # print(previous_url)

    if "homepage" in previous_url:
        return redirect('ecommerce:homepage')
    elif "catalog" in previous_url:
        return redirect('ecommerce:catalog')
    elif "product" in previous_url:
        return redirect('ecommerce:cart')


def removeFromCart(request, slug):
    item = get_object_or_404(Cart_Products, userId=request.user.id, slug=slug)
    # print(item)
    cart_item = Cart_Products.objects.filter(userId=request.user, furnitureId=item.furnitureId)
    cart_item.delete()
    messages.info(request, "This item was removed from your cart.")

    return redirect('ecommerce:cart')


# update modified quantity in cart page
def updateCart(request):
    if request.method == 'POST':
        cart_item = Cart_Products.objects.get(furnitureId=request.POST['furnitureId'], userId=request.user.id)
        # print(cart_item)
        cart_item.quantity =  request.POST['quantity']
        cart_item.save()

    return redirect('ecommerce:cart')


# ======= Checkout ======= #    

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            states = ['Johor','Kedah','Kelantan','Malacca','Negeri Sembilan','Pahang','Perak','Perlis','Pinang','Sabah','Sarawak','Selangor','Terangganu']
            cart = Cart_Products.objects.filter(userId=self.request.user)
            amount = sum(item.quantity*item.furnitureId.unitPrice for item in cart)
            context = {
                'object': cart, 
                'amount':amount,
                'states':states
                }
            customer_profile = Customer_Profile.objects.filter(custId=self.request.user.id)
            if customer_profile.exists():                
                context.update({
                    'profile':Customer_Profile.objects.get(custId=self.request.user.id)
                })
            return render(self.request, 'user/checkout.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Your cart is empty")
            return redirect('ecommerce:cart')
    
    def post(self, *args, **kwargs):
        try:
            order_id = str(random.randint(1000000, 9999999))

            while Order.objects.filter(orderId=order_id).exists():
                order_id = str(random.randint(1000000, 9999999))

            # name = self.request.POST['fname'] + ' ' + self.request.POST['lname']

            # order = Order(
            #     orderId = order_id,
            #     orderDate = datetime.today(),
            #     name = customer_name,
            #     shippingAddress = shipping_address,
            #     phoneNo = self.request.POST['txtPhoneNo'].rstrip(),
            #     email = self.request.POST['txtEmail'].rstrip(),
            #     amount = self.request.POST['hdfAmount'],
            #     userId = self.request.user,
            #     isDelivered = False,
            #     isReceived = False
            # )
            # order.save()

            data = json.loads(self.request.body)

            print(data['email'])
            print(data['phoneNo'])

            order_items = Cart_Products.objects.filter(userId=self.request.user.id)

            Order_Products.objects.bulk_create([Order_Products(orderId=Order.objects.get(orderId=order_id), furnitureId=item.furnitureId, quantity=item.quantity) for item in order_items])
            
            # delete items in cart
            clear_cart = Cart_Products.objects.filter(userId = self.request.user.id)
            clear_cart.delete()
            
            # print(order)
            messages.success(self.request, 'Order Successfully!')
            return render(self.request, 'user/homepage.html')
        except ObjectDoesNotExist:
            messages.warning(self.request, "Order Failed")
            return redirect("ecommerce:cart")


def payment_complete(request):
    order_id = str(random.randint(1000000, 9999999))

    while Order.objects.filter(orderId=order_id).exists():
        order_id = str(random.randint(1000000, 9999999))

    body = json.loads(request.body)
    print('BODY', body)

    customer_name = body['form']['fname'] + ' ' + body['form']['lname']
    shipping_address = body['shipping']['addressLine1'] + ', ' + body['shipping']['addressLine2'] + ', ' + body['shipping']['postcode'] + ' ' + body['shipping']['town'] + ', ' + body['shipping']['state']
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

    order_items = Cart_Products.objects.filter(userId=request.user.id)

    Order_Products.objects.bulk_create([Order_Products(orderId=Order.objects.get(orderId=order_id), furnitureId=item.furnitureId, quantity=item.quantity) for item in order_items])
    
    # delete items in cart
    clear_cart = Cart_Products.objects.filter(userId=request.user.id)
    clear_cart.delete()
    
    # print(order)
    # messages.success(request, 'Order Successfully!')

    # return redirect("ecommerce:profile")


# ======= Donation ======= #

def goDonate(request):
    if request.method == 'POST':
        form = DonationForm(request.POST, request.FILES)
        print(form.cleaned_data('firstname'))

        if form.is_valid():
            try:
                print("aaksbdkas")

                # firstname = form.cleaned_data['firstname']
                # lastname = form.cleaned_data['lastname']
                # form.save()
                # send_mail(subject, message, sender, recipients)
                # msg = messages.success(request, 'Donate Successfully!')
                donation = Donation()
                donation = form.save(commit=False)
                print("aaksbdkas")

            except ValidationError as e:
                print(e)
    else:
        print('form start')
        form = DonationForm()

    context = {'form':form}

    return render(request, 'user/donate.html', context)


def requestDonation(request):
    if request.method == "POST":
        
        donation = Donation(
            donationId = 'D' + str(random.randint(10000, 99999)),
            dateCreated = datetime.today(),
            name = request.POST.get('txtFname') + ' ' + request.POST.get('txtLname'),
            itemType = request.POST.get('txtType'),
            description = request.POST.get('txtDescription'),
            image = request.FILES['imgDonation'],
            yearPurchased = request.POST.get('txtYearPurchased'),
            originalPrice = request.POST.get('txtOriginalPrice'),
            userId = request.user
        )
        donation.save()

        messages.success(request, "Donation Request Created Successfully!")
        return redirect('ecommerce:donate')

    return render(request, 'user/donation.html')



# ======= testing ======= #

# def goAbout(request):
#     # return render(request, 'admin/login.html')
#     return -


# ======= Profile ======= #

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


def receiveOrder(request):
    id = request.POST.get('hdfOrderId')
    order = Order.objects.get(orderId = id)
    order.isReceived = True
    order.save()

    return messages.success(request, "Thank you for supporting our business!")

def updateAccount(request):
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)  # Important!
        
        messages.success(request, 'Your password was successfully updated!')
        return redirect('ecommerce:profile', section='settings')
    else:
        messages.error(request, 'Please correct the error below.')


def updateProfile(request):
    # update data in User modal
    user = User.objects.get(id = request.user.id)

    user.username = request.POST.get('txtUname')
    user.first_name = request.POST.get('txtFname')
    user.last_name = request.POST.get('txtLname')
    user.email = request.POST.get('txtEmail')

    user.save()

    # update data in Customer_Profile modal
    customer = Customer_Profile.objects.get(custId = request.user)

    customer.phoneNo = request.POST.get('txtPhoneNo')
    customer.gender = request.POST.get('rbtnGender')
    customer.dob = request.POST.get('txtDOB')
    customer.address1 = request.POST.get('txtAddress1')
    customer.address2 = request.POST.get('txtAddress2')
    customer.town = request.POST.get('txtTown')
    customer.postcode = request.POST.get('txtPostCode')
    customer.state = request.POST.get('ddlState')

    if len(request.FILES) != 0:
        # remove old image
        import os
        if os.path.exists(customer.profile_pic.path):
            os.remove(customer.profile_pic.path)        
        customer.profile_pic = request.FILES['imgProfile']

    customer.save()

    return messages.success(request, "Your profile is updated!")


def get_profile_data(request):
    profile_data = Customer_Profile.objects.get(custId=request.user)
    states = ['Johor','Kedah','Kelantan','Malacca','Negeri Sembilan','Pahang',
            'Perak','Perlis','Pinang','Sabah','Sarawak','Selangor','Terangganu']

    orders = Order.objects.filter(userId = request.user).order_by('-orderDate')
    items_list = []

    for order in orders:
        query = Order_Products.objects.filter(orderId = order.orderId)
        if(query.exists()):
            items_list.append(query)
        
    donations = Donation.objects.filter(userId = request.user).order_by('-dateCreated')
    
    form = PasswordChangeForm(request.user)

    context = {
        'customer':profile_data,
        'states':states,
        'order_data': zip(orders, items_list),
        'donations':donations,
        'form': form,
    }

    return context


# ======= Search Items ======= #

def searchProduct(request):
    if request.method == 'POST':
        keyword = request.POST.get('txtSearch')
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


