from account.forms import UserRegistrationForm
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from ecommerce.models import *

" ========== Register ========== " 

def registerView(request):
    # get the inputs from UserRegistrationForm
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        # if the inputs are valid
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Register Successfully!')
            except ValidationError as e:
                print(e)
    form = UserRegistrationForm()
    context = {'form':form}
    return render(request, 'account/register.html', context)


" ========== Login & Logout ========== " 

def loginView(request):
    msg = ''
    url =  request.path # get the current URL path
    
    if request.method == 'POST':
        uname = request.POST.get('txtUname')
        passwd = request.POST.get('txtPasswd')

        # verify  whether the user enter correct username and password
        user = authenticate(request, username=uname, password=passwd)

        # the user is authenticated 
        if user is not None:
            login(request, user)

            if user.is_staff == True:
                return redirect('administration:dashboard')
            else:
                return redirect('ecommerce:homepage')
        else:
            msg = messages.error(request, 'Invalid username or password!')

    # if the current URL does not contains 'user', direct to admin login
    if url.find('user') == -1:
        return render(request, 'account/ad_login.html', {'msg':msg})
    # else, direct to user login
    else:
        return render(request, 'account/login.html', {'msg':msg})
    

def logoutUser(request):
    # get the previous URL path
    previous_url = request.META.get('HTTP_REFERER')
    logout(request)
    # if the current URL contains 'user'
    if previous_url.find('ecommerce') == -1: 
        return redirect('account:admin_login')
    else:
	    return redirect('account:user_login')


# def loginView(request):
#     url =  request.path
#     if request.method == 'POST':
#         proceedLogin(request)
#     elif url.find('ecommerce') == -1:
#         return render(request, 'account/ad_login.html')
#     else:
#         return render(request, 'account/login.html')

# def proceedLogin(request):
#         msg = ''
#         uname = request.POST.get('txtUname')
#         passwd = request.POST.get('txtPasswd')

#         if uname != '' and passwd != '':
#             user = authenticate(request, username=uname, password=passwd)

#             if user is not None:
#                 login(request, user)

#                 if user.is_staff == True:
#                     return redirect('administration:dashboard')
#                 else:
#                     return redirect('ecommerce:homepage')
#             else:
#                 msg = messages.error(request, 'Invalid username or password!')

#                 context = {'msg':msg}


# def logoutUser(request):
#     url =  request.path
#     logout(request)
    
#     if url.find('ecommerce') == -1:
# 	    return redirect('account:admin_login')
#     else:
# 	    return redirect('account:user_login')


