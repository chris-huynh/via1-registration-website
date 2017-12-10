from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone

# Need these for email activation
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from registration.tokens import account_activation_token, member_school_verification_token, refund_request_token
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text


# Need to change client ID and client secret to live ids (also found in settings.py)
import paypalrestsdk
paypalrestsdk.configure({
    "mode": "sandbox",  # sandbox or live
    "client_id": settings.PAYPAL_SANDBOX_CLIENT_ID,
    "client_secret": settings.PAYPAL_SANDBOX_CLIENT_SECRET})


import datetime
from registration import regutils


# Import models
from registration.models import ConferenceVars
from registration.models import UserInfo


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

        context = {'is_early_reg_open': is_early_reg_open, 'is_regular_reg_open': is_regular_reg_open, 'is_alumni_reg_open': is_alumni_reg_open,
                   'refund_deadline': regutils.refund_deadline, 'todays_date': todays_date, 'open_date': regutils.early_reg_open_date,
                   'member_school_names': regutils.member_school_names, 'attendee_types': regutils.AttendeeTypes,
                   'register_types': regutils.RegisterTypes, 'register_prices': regutils.RegisterPrices,
                   'register_caps': regutils.RegisterCaps}
        return render(request, 'registration/home.html', context)
    else:
        return redirect('/registration/login')


@login_required()
def profile(request):
    if request.user.is_authenticated:
        user_info = UserInfo.objects.get(pk=request.user.id)

        member_school_names = regutils.member_school_names
        graduation_years = regutils.graduation_years

        # If the current value in user_info.school is not null/blank and not in the list of member schools, the Other choice was chosen
        other_selected = 'false' if (user_info.school in member_school_names) else 'true'

        context = {'user_info': user_info, 'member_school_names': member_school_names, 'other_selected': other_selected,
                   'graduation_years': graduation_years}
        return render(request, 'registration/profile.html', context)
    else:
        return redirect('/registration/login')


@login_required()
def submit_profile(request):
    if request.method == 'POST':
        form = request.POST

        user = request.user
        user_info = UserInfo.objects.get(pk=request.user.id)

        # If user.middle_name is null and the user leaves the field blank, we don't want to replace Null with an empty string
        # Also, if user previously had something saved in the field but then decides to blank it out, we want the db to
        # use null, not an empty string
        if user.middle_name != form['middle_name'] and not (user.middle_name is None and form['middle_name'] == ''):
            if form['middle_name'] == '':
                user.middle_name = None
            else:
                user.middle_name = form['middle_name']
            user.save()

        if user_info.phone_number != form['phone_number'] and not (user_info.phone_number is None and form['phone_number'] == ''):
            if form['phone_number'] == '':
                user_info.phone_number = None
            else:
                user_info.phone_number = form['phone_number']

        if user_info.birth_date != form['birth_date'] and not (user_info.birth_date is None and form['birth_date'] == ''):
            if form['birth_date'] == '':
                user_info.birth_date = None
            else:
                user_info.birth_date = form['birth_date']

        if form.get('school', False) and form['school'] == 'other':
            if user_info.school != form['other_school'] and not (user_info.school is None and form['other_school'] == ''):
                if form['other_school'] == '':
                    user_info.school = None
                else:
                    user_info.school = form['other_school']
        else:
            if form.get('school', False) and user_info.school != form['school']:
                user_info.school = form['school']

        if user_info.grad_year != form['grad_year']:
            if form['grad_year'] == '':
                user_info.grad_year = None
            else:
                user_info.grad_year = form['grad_year']

        if user_info.major != form['major'] and not (user_info.major is None and form['major'] == ''):
            if form['major'] == '':
                user_info.major = None
            else:
                user_info.major = form['major']

        if form.get('pronouns', False) and user_info.pronouns != form['pronouns']:
            if form['pronouns'] == '':
                user_info.pronouns = None
            else:
                user_info.pronouns = form['pronouns']

        if user_info.facebook != form['facebook'] and not (user_info.facebook is None and form['facebook'] == ''):
            if form['facebook'] == '':
                user_info.facebook = None
            else:
                user_info.facebook = form['facebook']

        if user_info.instagram != form['instagram'] and not (user_info.instagram is None and form['instagram'] == ''):
            if form['instagram'] == '':
                user_info.instagram = None
            else:
                user_info.instagram = form['instagram']

        if user_info.twitter != form['twitter'] and not (user_info.twitter is None and form['twitter'] == ''):
            if form['twitter'] == '':
                user_info.twitter = None
            else:
                user_info.twitter = form['twitter']

        if user_info.snapchat != form['snapchat'] and not (user_info.snapchat is None and form['snapchat'] == ''):
            if form['snapchat'] == '':
                user_info.snapchat = None
            else:
                user_info.snapchat = form['snapchat']

        if user_info.linkedin != form['linkedin'] and not (user_info.linkedin is None and form['linkedin'] == ''):
            if form['linkedin'] == '':
                user_info.linkedin = None
            else:
                user_info.linkedin = form['linkedin']

        if form.get('banquet_meal', False) and user_info.banquet_meal != form['banquet_meal']:
            if form['banquet_meal'] == '':
                user_info.banquet_meal = None
            else:
                user_info.banquet_meal = form['banquet_meal']

        if user_info.food_allergies != form['food_allergies'] and not (user_info.food_allergies is None and form['food_allergies'] == ''):
            if form['food_allergies'] == '':
                user_info.food_allergies = None
            else:
                user_info.food_allergies = form['food_allergies']

        if user_info.emergency_contact != form['emergency_contact'] and not (user_info.emergency_contact is None and form['emergency_contact'] == ''):
            if form['emergency_contact'] == '':
                user_info.emergency_contact = None
            else:
                user_info.emergency_contact = form['emergency_contact']

        if user_info.emergency_contact_number != form['emergency_contact_number'] and not (user_info.emergency_contact_number is None and form['emergency_contact_number'] == ''):
            if form['emergency_contact_number'] == '':
                user_info.emergency_contact_number = None
            else:
                user_info.emergency_contact_number = form['emergency_contact_number']

        if user_info.emergency_contact_relation != form['emergency_contact_relation'] and not (user_info.emergency_contact_relation is None and form['emergency_contact_relation'] == ''):
            if form['emergency_contact_relation'] == '':
                user_info.emergency_contact_relation = None
            else:
                user_info.emergency_contact_relation = form['emergency_contact_relation']

        if form.get('shirt_size', False) and user_info.shirt_size != form['shirt_size']:
            if form['shirt_size'] == '':
                user_info.shirt_size = None
            else:
                user_info.shirt_size = form['shirt_size']

        user_info.save()

        return JsonResponse({})


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

        # Once the user activates, we also want to create a user_info table for them
        # NOTE: super users created with createsuperuser will NOT get a UserInfo table --
        # so do not try to use the profile page with an superuser account
        user_info = UserInfo(user_id=user)
        user_info.save()

        login(request, user)
        return redirect('/')
    else:
        return redirect('/registration/account_activation_invalid')


def member_school_verification_request(request):
    if request.method == 'POST':
        form = request.POST
        user = request.user

        # This lambda expression will search for contact information of the chosen school. If found, a list is returned
        president = list(filter(lambda x: x.school == form['school_association'], regutils.member_school_presidents))
        if president:
            # If a president was found, take index 0 because the lambda function only ever returns 1 president
            president = president[0]

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
            messages.info(request, 'The school you have selected does not have a point of contact. Please email conference.executive@uvsamidwest.org')
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


# Passes back a json object containing a boolean for every attendee type
def is_conference_full(request):
    conf_vars = ConferenceVars.objects.get(pk=1)

    data = {
        'is_early_reg_full': True if (conf_vars.early_attendee_count >= regutils.RegisterCaps.EARLY_REG_CAP) else False,
        'is_regular_reg_full': True if (conf_vars.regular_attendee_count >= regutils.RegisterCaps.REGULAR_REG_CAP) else False,
        'is_alumni_reg_full': True if (conf_vars.alumni_attendee_count >= regutils.RegisterCaps.ALUMNI_REG_CAP) else False,
        'is_conference_full': True if (conf_vars.early_attendee_count >= regutils.RegisterCaps.EARLY_REG_CAP and
                                       conf_vars.regular_attendee_count >= regutils.RegisterCaps.REGULAR_REG_CAP) else False
    }
    return JsonResponse(data)


@login_required()
def update_paid_attendee(request):
    if request.is_ajax():
        user = User.objects.get(pk=request.user.id)

        # if the user's has_paid status is already true, then we don't want to do anything. This will only occur in
        # situations where someone tries to send a fake request to this endpoint
        if not user.has_paid:
            # Need to check if that paymentID exists so that people can't send fake calls to this endpoint
            if paypalrestsdk.Payment.find(request.GET.get('paymentID')):
                reg_type = request.GET.get('reg_type')

                user.has_paid = True
                user.time_paid = timezone.now()  # This is a timezone aware method. It'll use the server's timezone (set to CST in settings.py)
                user.reg_type = reg_type

                if (reg_type == regutils.RegisterTypes.EARLY_REG_HOTEL or
                            reg_type == regutils.RegisterTypes.REGULAR_REG_HOTEL or
                            reg_type == regutils.RegisterTypes.ALUMNI_REG_HOTEL or
                            reg_type == regutils.RegisterTypes.STAFF_REG_HOTEL):
                    user.has_paid_hotel = True

                # TODO Will most likely have to add more fields to this later if we add additional user fields

                user.save()

                # increment attendee count for appropriate attendee_type
                conf_vars = ConferenceVars.objects.get(pk=1)
                if reg_type == regutils.RegisterTypes.EARLY_REG or regutils.RegisterTypes.EARLY_REG_HOTEL:
                    conf_vars.early_attendee_count += 1
                elif reg_type == regutils.RegisterTypes.REGULAR_REG or regutils.RegisterTypes.REGULAR_REG_HOTEL:
                    conf_vars.regular_attendee_count += 1
                elif reg_type == regutils.RegisterTypes.ALUMNI_REG or regutils.RegisterTypes.ALUMNI_REG_HOTEL:
                    conf_vars.alumni_attendee_count += 1
                elif reg_type == regutils.RegisterTypes.STAFF_REG or regutils.RegisterTypes.STAFF_REG_HOTEL:
                    conf_vars.staff_attendee_count += 1
                conf_vars.save()

                # Just need to send an empty JSON response
                return JsonResponse({})


def refund_request(request):
    if request.method == 'POST':
        form = request.POST
        user = request.user

        # Only proceed if the user has paid
        if user.has_paid:
            current_site = get_current_site(request)
            subject = '[REFUND REQUEST] A VIA-1 Attendee Requests A Registration Refund'
            message = render_to_string('registration/refund_request_email.html', {
                'name': user.get_full_name(),
                'email': user.email,
                'pp_name': form['pp_name'],
                'pp_email': form['pp_email'],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': refund_request_token.make_token(user),
            })
            # TODO change to_email to Finance uvsa email
            send_mail(subject, "", None, ['tomng2012@gmail.com'], False, None, None, None, message)

            messages.info(request, 'Your refund request has been submitted. You will receive an email once the Finance committee has issued your refund.')
            return redirect('index')
    else:
        return redirect('index')


def refund_request_complete(request, uidb64, token, pp_email):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and refund_request_token.check_token(user, token):
        if user.reg_type == regutils.RegisterTypes.EARLY_REG:
            amount = regutils.RegisterPrices.EARLY_REG_PRICE
        elif user.reg_type == regutils.RegisterTypes.EARLY_REG_HOTEL:
            amount = regutils.RegisterPrices.EARLY_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
        elif user.reg_type == regutils.RegisterTypes.REGULAR_REG:
            amount = regutils.RegisterPrices.REGULAR_REG_PRICE
        elif user.reg_type == regutils.RegisterTypes.REGULAR_REG_HOTEL:
            amount = regutils.RegisterPrices.REGULAR_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
        elif user.reg_type == regutils.RegisterTypes.ALUMNI_REG:
            amount = regutils.RegisterPrices.ALUMNI_REG_PRICE
        elif user.reg_type == regutils.RegisterTypes.ALUMNI_REG_HOTEL:
            amount = regutils.RegisterPrices.ALUMNI_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
        elif user.reg_type == regutils.RegisterTypes.STAFF_REG:
            amount = regutils.RegisterPrices.STAFF_REG_PRICE
        elif user.reg_type == regutils.RegisterTypes.STAFF_REG_HOTEL:
            amount = regutils.RegisterPrices.STAFF_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE

        # Decrement attendee count for appropriate attendee_type
        conf_vars = ConferenceVars.objects.get(pk=1)
        if user.reg_type == regutils.RegisterTypes.EARLY_REG or regutils.RegisterTypes.EARLY_REG_HOTEL:
            conf_vars.early_attendee_count -= 1
        elif user.reg_type == regutils.RegisterTypes.REGULAR_REG or regutils.RegisterTypes.REGULAR_REG_HOTEL:
            conf_vars.regular_attendee_count -= 1
        elif user.reg_type == regutils.RegisterTypes.ALUMNI_REG or regutils.RegisterTypes.ALUMNI_REG_HOTEL:
            conf_vars.alumni_attendee_count -= 1
        elif user.reg_type == regutils.RegisterTypes.STAFF_REG or regutils.RegisterTypes.STAFF_REG_HOTEL:
            conf_vars.staff_attendee_count -= 1
        conf_vars.save()

        # Need to change user's payment status
        user.has_paid = False
        user.time_paid = None
        # This has to be done before reg_type gets set to None
        if (user.reg_type == regutils.RegisterTypes.EARLY_REG_HOTEL or user.reg_type == regutils.RegisterTypes.REGULAR_REG_HOTEL or
                    user.reg_type == regutils.RegisterTypes.ALUMNI_REG_HOTEL or regutils.RegisterTypes.STAFF_REG_HOTEL):
            user.has_paid_hotel = False
        user.reg_type = None

        user.save()

        # Send an email to the user letting them know that their refund has been fulfilled
        subject = 'Your VIA-1 Registration Refund Has Been Fulfilled'
        message = render_to_string('registration/refund_request_complete_email.html', {
            'name': user.first_name,
            'pp_email': pp_email,
            'amount': str(amount)
        })
        send_mail(subject, "", None, [user.email], False, None, None, None, message)

        return redirect('/registration/refund_request_complete')


