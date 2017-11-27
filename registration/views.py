from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from paypal.standard.forms import PayPalPaymentsForm
from django.core.mail import send_mail

# Need these for email activation
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from registration.tokens import account_activation_token, member_school_verification_token
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
        todays_date = datetime.datetime.now()
        is_early_reg_open = True if (regutils.early_reg_open_date < todays_date < regutils.early_reg_close_date) else False
        is_regular_reg_open = True if (regutils.regular_reg_open_date < todays_date < regutils.regular_reg_close_date) else False
        is_alumni_reg_open = True if (regutils.alumni_reg_open_date < todays_date < regutils.alumni_reg_close_date) else False

        early_reg_pp_dict = {
            "business": regutils.pp_sandbox_merchant_email,
            "amount": regutils.early_reg_price, # Might not need this now that there's a dropdown. Maybe wanna keep if we pass in the hotel price
            "item_name": (regutils.event_name + ' Early Registration'),
            "invoice": ('via1-2018-reg-' + str(request.user.id)),
            "notify_url": request.build_absolute_uri(reverse('payment_listener')),
            "return_url": request.build_absolute_uri(reverse('payment_processing')),
            "cancel_return": request.build_absolute_uri(reverse('payment_canceled')),
            "custom": "early_registration",  # Custom command to correlate to some function later
        }

        regular_reg_pp_dict = {
            "business": regutils.pp_sandbox_merchant_email,
            "amount": regutils.regular_reg_price,
            "item_name": (regutils.event_name + ' Regular Registration'),
            "invoice": ('via1-2018-reg-' + str(request.user.id)),
            "notify_url": request.build_absolute_uri(reverse('payment_listener')),
            "return_url": request.build_absolute_uri(reverse('payment_processing')),
            "cancel_return": request.build_absolute_uri(reverse('payment_canceled')),
            "custom": "regular_registration",  # Custom command to correlate to some function later
        }

        alumni_reg_pp_dict = {
            "business": regutils.pp_sandbox_merchant_email,
            "amount": regutils.alumni_reg_price,
            "item_name": (regutils.event_name + ' Alumni Registration'),
            "invoice": ('via1-2018-reg-' + str(request.user.id)),
            "notify_url": request.build_absolute_uri(reverse('payment_listener')),
            "return_url": request.build_absolute_uri(reverse('payment_processing')),
            "cancel_return": request.build_absolute_uri(reverse('payment_canceled')),
            "custom": "alumni_registration",  # Custom command to correlate to some function later
        }

        early_reg_pp_button = PayPalPaymentsForm(initial=early_reg_pp_dict)
        regular_reg_pp_button = PayPalPaymentsForm(initial=regular_reg_pp_dict)
        alumni_reg_pp_button = PayPalPaymentsForm(initial=alumni_reg_pp_dict)

        context = {'is_early_reg_open': is_early_reg_open, 'is_regular_reg_open': is_regular_reg_open, 'is_alumni_reg_open': is_alumni_reg_open,
                   'todays_date': todays_date, 'open_date': regutils.early_reg_open_date, 'early_reg_pp_button': early_reg_pp_button,
                   'regular_reg_pp_button': regular_reg_pp_button, 'alumni_reg_pp_button': alumni_reg_pp_button,
                   'early_reg_price': regutils.early_reg_price, 'regular_reg_price': regutils.regular_reg_price,
                   'alumni_reg_price': regutils.alumni_reg_price, 'member_school_names': regutils.member_school_names}
        return render(request, 'registration/home.html', context)
    else:
        return redirect('/registration/login')


def profile(request):
    if request.user.is_authenticated:
        return render(request, 'registration/profile.html')
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
    else:
        return redirect('/registration/login')


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


def member_school_verification_processing(request):
    if request.method == 'POST':
        form = request.POST
        user = request.user

        # This lambda expression will always return 1 object because our member_school_presidents list only has unique entries
        president = list(filter(lambda x: x.school == form['school_association'], regutils.member_school_presidents))[0]

        current_site = get_current_site(request)
        subject = 'A VIA-1 Attendee Requests Member School Approval'
        message = render_to_string('registration/mem_school_verif_email.html', {
            'name': user.get_full_name(),
            'email': form['email'],
            'phone_number': form['phone_number'],
            'school': form['school_association'],
            'president_name': president.name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': member_school_verification_token.make_token(user),
        })
        send_mail(subject, "", None, [president.email], False, None, None, None, message)

        messages.info(request, 'Your verification request has been submitted. You will receive an email upon approval.')
        return redirect('index')
    else:
        return redirect('index')


def member_school_verification_approve(request, uidb64, token, school):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and member_school_verification_token.check_token(user, token):
        user.is_member_school = True
        user.school = school
        user.save()

        subject = 'Your VIA-1 Member School Verification Has Been Approved'
        message = render_to_string('registration/mem_school_verif_approved_email.html', {
            'name': user.first_name,
            'email': user.email,
            'school': school,
        })
        send_mail(subject, "", None, [user.email], False, None, None, None, message)

        return redirect('/registration/member_school_verification_approved')
    else:
        return redirect('/registration/member_school_verification_invalid')


def member_school_verification_deny(request, uidb64, token, school):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and member_school_verification_token.check_token(user, token):
        # We don't need to do anything here with the data here. Just send an email to the user letting them know they were denied
        subject = 'Your VIA-1 Member School Verification Has Been Denied'
        message = render_to_string('registration/mem_school_verif_denied_email.html', {
            'name': user.first_name,
            'email': user.email,
            'school': school,
        })
        send_mail(subject, "", None, [user.email], False, None, None, None, message)

        return redirect('/registration/member_school_verification_denied')
    else:
        return redirect('/registration/member_school_verification_invalid')
