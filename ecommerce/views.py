from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render
from ecommerce.models import *
from django.core.paginator import Paginator

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from django.shortcuts import render, redirect 
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin


from .recommendation import recommendToCustomer, recommendToNormalUser, recommendToNewUser


# ======= Views for Account Authentication ======= #

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

    return render(request, 'register.html', context)


def loginView(request):
    msg = ''
    if request.method == 'POST':
        uname = request.POST.get('txtUname')
        passwd = request.POST.get('txtPasswd')

        if uname != '' and passwd != '':
            user = authenticate(request, username=uname, password=passwd)

            if user is not None:
                login(request, user)
                # active_user = User.objects.get(username=request.user.username)
                # request.session['userId']= active_user.id
                return redirect('ecommerce:homepage')
            else:
                msg = messages.error(request, 'Invalid username or password!')

    context = {'msg':msg}

    return render(request, 'login.html', context)


def logoutUser(request):
    # try:
    #     del request.session['userId']
    # except KeyError:
    #     pass

	logout(request)
	return redirect('ecommerce:login')

# ======= Views for Homepage ======= #

@login_required(login_url='ecommerce:login')
def goHompage(request):
    if Order.objects.filter(userId=request.user).exists():
        cb_recommend_list, furniture_name, cf_recommend_list, popularity_recommend_list = recommendToCustomer(request.user, "customer")

        cb_recommend_query = []
        for i in cb_recommend_list:
            cb_recommend_query.append(Furniture.objects.filter(pk__in=i))

        context = {
            'zipped_data': zip(furniture_name, cb_recommend_query),
            'cf_recommend_list':Furniture.objects.filter(pk__in=cf_recommend_list), 
            'popularity_recommend_list':Furniture.objects.filter(pk__in=popularity_recommend_list)
        }
    elif User_Views.objects.filter(userId=request.user):
        cf_recommend_list, popularity_recommend_list = recommendToNormalUser(request.user,'normal user')
        context = {
            'cf_recommend_list':Furniture.objects.filter(pk__in=cf_recommend_list), 
            'popularity_recommend_list':Furniture.objects.filter(pk__in=popularity_recommend_list)
        }        
    else:
        popularity_recommend_list = recommendToNewUser()
        context = {
            'popularity_recommend_list':Furniture.objects.filter(pk__in=popularity_recommend_list)
        }

    return render(request,'homepage.html', context)


# ======= Views for Catalog ======= #

def goCatalog(request): 
    cid = request.GET.get('cid', 1)       
    page_number = request.GET.get('page', 1)

    furniture = Furniture.objects.filter(categoryId_id=cid)
    paginator = Paginator(furniture, 12)
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

    return render(request,'catalog.html', context)

def goDonate(request):
    return render(request,'donate.html')

def goAbout(request):
    return render(request,'about.html')

def goCart(request):
    return render(request, 'cart.html')

def goProfile(request):
    return render(request, 'profile.html')

def goProduct(request):
    return render(request, 'item.html')

class ItemDetailView(DetailView):
    model = Furniture
    template_name = "item.html"

class CartDetailView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            cart = Cart_Products.objects.filter(userId=self.request.user)
            amount = sum(item.quantity*item.furnitureId.unitPrice for item in cart)
            context = {
                'cart': cart, 
                'amount':amount
                }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Your cart is empty")
            return redirect('ecommerce:cart')


def updateViewToItem(request, slug):
    item = get_object_or_404(Furniture, slug=slug)

    # item that has been viewed before
    viewed_item = User_Views.objects.filter(userId=request.user, furnitureId=item)

    if viewed_item.exists():
        get_viewed_item = User_Views.objects.get(userId=request.user, furnitureId=item)
        get_viewed_item.viewCount += 1       
        get_viewed_item.save()
        # print(get_viewed_item)
    else:
        User_Views.objects.create(userId=request.user, furnitureId=item, viewCount=1)
        # print(view)

    return redirect('ecommerce:product', slug=slug)

    
# ====================================================================================== # 


def addToCart(request, slug):
    item = get_object_or_404(Furniture, slug=slug)
    item_in_cart = Cart_Products.objects.filter(userId=request.user, furnitureId=item)
    
    if item_in_cart.exists():
        item_in_cart = Cart_Products.objects.get(userId=request.user, furnitureId=item)
        item_in_cart.quantity += 1
        item_in_cart.save()
        messages.info(request, "This item quantity was updated.")
    else:
        Cart_Products.objects.create(userId=request.user, furnitureId=item, quantity=1,slug=item.furnitureId)
        messages.info(request, "This item was added to your cart.")
    
    return redirect('ecommerce:homepage')

def removeFromCart(request, slug):
    item = get_object_or_404(Cart_Products, slug=slug)
    cart_item = Cart_Products.objects.filter(userId=request.user, furnitureId=item.furnitureId)
    cart_item.delete()
    messages.info(request, "This item was removed from your cart.")

    return redirect('ecommerce:cart')


def updateCart(request):
    print()
    if request.method == 'POST':
        cart_item = Cart_Products.objects.get(furnitureId=request.POST['furnitureId'])
        print(cart_item)
        cart_item.quantity =  request.POST['quantity']
        cart_item.save()
        # messages.info(request, "qty updated")

    return redirect('ecommerce:cart')



# def testing(request):
#     # df = contentBasedRec()
#     # category_list = popularityBasedFiltering()
#     # furniture = Furniture.objects.all()
#     # category = Category.objects.all()

#     # for i in category:
#     #     category_list.append(i.categoryName)

#     # context = {"getData":furniture, "categories":category_list}
#     return HttpResponse(category_list)





