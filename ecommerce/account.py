
from django.core.exceptions import ValidationError

from django.shortcuts import render, redirect 
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


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