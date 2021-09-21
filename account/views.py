from account.forms import UserRegistrationForm
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from ecommerce.models import *

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

                if user.is_staff == True:
                    return redirect('administration:dashboard')
                else:
                    return redirect('ecommerce:homepage')
            else:
                msg = messages.error(request, 'Invalid username or password!')

    context = {'msg':msg}

    return render(request, 'account/login.html', context)
    

def logoutUser(request):
	logout(request)
	return redirect('account:login')

