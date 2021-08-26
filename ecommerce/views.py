from django.http.response import HttpResponse
from django.shortcuts import render
from ecommerce.models import *
from django.core.paginator import Paginator

from django.core.exceptions import ValidationError

from django.shortcuts import render, redirect 
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, sessions
from django.contrib.auth.decorators import login_required


from .recommendation import collaborativeFiltering, contentBasedFiltering, popularityBasedFiltering


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
                active_user = User.objects.get(username=request.user.username)
                request.session['userId']= active_user.id
                return redirect('homepage')
            else:
                msg = messages.error(request, 'Invalid username or password')

    context = {'msg':msg}

    return render(request, 'login.html', context)


def logoutUser(request):
    # try:
    #     del request.session['userId']
    # except KeyError:
    #     pass

	logout(request)
	return redirect('login')

# ======= Views for Homepage ======= #

@login_required(login_url='login')
def goHompage(request):
    if 'userId' in request.session:
        furniture_id_list = generateRecommendation(request)
        
    context = {"furniture":Furniture.objects.filter(pk__in=furniture_id_list)}

    return render(request,'homepage.html', context)

def generateRecommendation(request):
    if request.method == 'POST':
        if(request.POST.get('btnInspiredBy')):
            fid_list = contentBasedFiltering(request.session['userId'])
        elif(request.POST.get('btnTopPicks')):
            fid_list = collaborativeFiltering(request.session['userId'])
        elif(request.POST.get('btnTrending')):
            fid_list = popularityBasedFiltering()
    else:
        fid_list = contentBasedFiltering(request.session['userId'])
    
    print(User.objects.get(id=request.session['userId']).username)
    
    return fid_list



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






def testing(request):
    # df = contentBasedRec()
    category_list = popularityBasedFiltering()
    # furniture = Furniture.objects.all()
    # category = Category.objects.all()

    # for i in category:
    #     category_list.append(i.categoryName)

    # context = {"getData":furniture, "categories":category_list}
    return HttpResponse(category_list)





