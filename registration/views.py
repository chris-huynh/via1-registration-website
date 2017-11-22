from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from paypal.standard.forms import PayPalPaymentsForm

# Need these for email activation
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from registration.tokens import account_activation_token
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text

import datetime
from registration import regutils


# Need to use get_user_model() because we have a custom auth user model
User = get_user_model()


def index(request):
    if request.user.is_authenticated:
        return redirect('/registration/home')
    else:
        return redirect('/registration/login')


def home(request):
    if request.user.is_authenticated:
        # Start Scratch -- Just some scratch code for now... Might use later.
        today = datetime.datetime.now()
        early_reg_open = True if today > regutils.early_reg_date else False
        # End Scratch

        paypal_dict = {
            "business": regutils.pp_sandbox_merchant_email,
            "amount": "1.00",
            "item_name": (regutils.event_name + ' Registration'),
            "invoice": request.user.id,
            "notify_url": request.build_absolute_uri(reverse('payment_listener')),
            "return_url": request.build_absolute_uri(reverse('payment_processing')),
            "cancel_return": request.build_absolute_uri(reverse('payment_canceled')),
            #"custom": "premium_plan",  # Custom command to correlate to some function later (optional)
        }

        pp_button_one = PayPalPaymentsForm(initial=paypal_dict)

        context = {'early_reg_open': early_reg_open, 'today': today, 'open_date': regutils.early_reg_date, 'pp_button_one': pp_button_one}
        return render(request, 'registration/home.html', context)
    else:
        return redirect('/registration/login')


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
            user = User.objects.create_user(email, first_name, last_name, password)

            # The user has been created but they now need to do an email confirmation
            current_site = get_current_site(request)
            subject = 'Activate Your VIA-1 Account'
            message = render_to_string('registration/account_activation_email.html', {
                'user': first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('/registration/account_activation_sent')
        else:
            # Render the login page again and pass back the fields that the user inputted
            # (so we can auto-populate the form)
            return render(request, 'registration/login.html', {'reg_form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('/')
    else:
        return redirect('/registration/account_activation_invalid')


def payment_processing(request):
    return redirect('index')


def payment_listener(request, **kwargs):
    return redirect('index')


def payment_canceled(request):
    return redirect('index')
