from django.http.response import HttpResponse
from django.shortcuts import render
from ecommerce.models import *
from django.core.paginator import Paginator

from django.core.exceptions import ValidationError

from django.shortcuts import render, redirect 
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .recommendation import getAllRecommendation, contentBasedRec


# ======= Views for Account Authentication ======= #

def registerView(request):
    msg = ''
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                msg = messages.success(request, 'register successful')
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
                return redirect('homepage')
            else:
                msg = messages.error(request, 'Invalid username or password')

    context = {'msg':msg}

    return render(request, 'login.html', context)


def logoutUser(request):
	logout(request)
	return redirect('login')

# ======= Views for Homepage ======= #

@login_required(login_url='login')
def goHompage(request):
    # result = Furniture.objects.all()
    # result = pd.DataFrame(list(Order.objects.get(userId=1)))
    # return HttpResponse(result.to_html())

    # if request.method == 'POST':
    #     if request.POST.get('btnViewMore'):
    #         recommendation_number = 20
    # else:
    #     recommendation_number = 10


    # fid_list = getAllRecommendation()
    fid_list = contentBasedRec()

    context = {"furniture":Furniture.objects.filter(pk__in=fid_list)}

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

def goProfile(request):
    return render(request, 'profile.html')

# ====================================================================================== # 

def generate_recommendation(request):
    if request.method == 'POST':
        if(request.POST.get('btnTopPicks')):
            user = 1
        elif(request.POST.get('btnPopular')):
            user = 2
        elif(request.POST.get('btnAll')):
            getAllRecommendation()





def testing(request):
    # df = contentBasedRec()
    category_list = []
    furniture = Furniture.objects.all()
    category = Category.objects.all()

    for i in category:
        category_list.append(i.categoryName)

    context = {"getData":furniture, "categories":category_list}
    return HttpResponse("sda")





