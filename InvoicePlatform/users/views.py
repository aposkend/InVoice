from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib import auth
from .forms import LoginForm, PasswordForm, SignupForm

# Create your views here.


def getHomePage(request):
    return redirect('users:signup')


def signUp(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '註冊成功！請重新登入')
            return redirect('users:login')

    else:
        form = SignupForm()

    errors = form.errors

    return render(request, 'register.html', {'form': form, 'errors': errors})


def logIn(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(request, username=username, password=password)
            if user:
                auth.login(request, user)
                return redirect('main:getMainpage')
            else:
                messages.error(request, '帳號或密碼錯誤')
                return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logOut(request):
    logout(request)
    return redirect('users:getHomePage')


def changePassword(request):
    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '密碼已更新!')
            return render(request, 'UpdatePassword.html', {'form': form})
    else:
        form = PasswordForm(request.user)
    return render(request, 'UpdatePassword.html', {'form': form})
