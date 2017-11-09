from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect


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

        if User.objects.filter(email=email).exists():
            valid_form = False
            messages.error(request, 'That email is already in use. Please try again.')
        elif password != retype_password:
            valid_form = False
            messages.error(request, 'Your passwords did not match. Please try again.')

        if valid_form and not (User.objects.filter(email=email).exists()):
            User.objects.create_user(email, first_name, last_name, password)
            user = authenticate(request, username=email, password=password)
            login(request, user)
            # This will send them to the index view, which will then redirect again appropriately
            return HttpResponseRedirect('/')
        else:
            # Render the login page again and pass back the fields that the user inputted (so we can auto-populate the form)
            return render(request, 'registration/login.html', {'reg_form': form})


