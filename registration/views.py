from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.http import HttpResponseRedirect
from django import forms
from .forms import UserRegistrationForm

# Need to use get_user_model() because we have a custom auth user model
User = get_user_model()


def index(request):
    if request.user.is_authenticated:
        return redirect('/registration/home')
    else:
        return redirect('/registration/login')


def home(request):
    return render(request, 'registration/home.html')


def register(request):
    if request.method == 'POST':
        valid_form = True

        form = request.POST
        email = form['email']
        password = form['password']
        retype_password = form['retype_password']
        first_name = form['first_name']
        last_name = form['last_name']

        if password != retype_password:
            valid_form = False
            messages.error(request, 'Your passwords did not match. Please try again.')

        if valid_form and not (User.objects.filter(email=email).exists()):
            User.objects.create_user(email, first_name, last_name, password)
            user = authenticate(username=email, password=password)
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            return redirect('/registration/login')


def user_login(request, **kwargs):
    if request.user.is_authenticated:
        return redirect('/registration/home', **kwargs)
    else:
        return login(request)


def page_not_found(request):
    return HttpResponse('This is a custom 404 page')