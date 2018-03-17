from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import base64
import io
from ftplib import FTP

# Need these for email activation
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from registration.tokens import account_activation_token, member_school_verification_token, refund_request_token, alumni_verification_token, refund_hotel_request_token
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text

import datetime
from datetime import timedelta
from random import randint

from registration import regutils

# Import models
from registration.models import ConferenceVars
from registration.models import UserInfo
from registration.models import SpecialRegCodes
from registration.models import Workshops
from registration.models import Families

# Need to change client ID and client secret to live ids (also found in settings.py)
import paypalrestsdk
paypalrestsdk.configure({
    "mode": "live",  # sandbox or live
    "client_id": settings.PAYPAL_LIVE_CLIENT_ID,
    "client_secret": settings.PAYPAL_LIVE_CLIENT_SECRET})


# Need to use get_user_model() because we have a custom auth user model
User = get_user_model()


def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        return redirect('/registration/login')


def home(request):
    if request.user.is_authenticated:
        todays_date = datetime.datetime.now()
        is_early_reg_open = True if (regutils.early_reg_open_date < todays_date < regutils.early_reg_close_date) else False
        is_regular_reg_open = True if (regutils.regular_reg_open_date < todays_date < regutils.regular_reg_close_date) else False
        is_alumni_reg_open = True if (regutils.alumni_reg_open_date < todays_date < regutils.alumni_reg_close_date) else False

        conference_caps = ConferenceVars.objects.get(pk=1)
        # TODO Gonna leave this as Full indefinitely for now. Since we want it to say Sold Out permanently even if someone refunds
        is_early_reg_full = True  # if conference_caps.early_attendee_count >= regutils.RegisterCaps.EARLY_REG_CAP else False
        is_regular_reg_full = True  # if conference_caps.regular_attendee_count >= regutils.RegisterCaps.REGULAR_REG_CAP else False
        is_alumni_reg_full = True if conference_caps.alumni_attendee_count >= regutils.RegisterCaps.ALUMNI_REG_CAP else False

        is_refund_open = True if todays_date < regutils.payment_refund_deadline else False

        # Very hacky. We don't want to have a hardcoded string -- perhaps add it to regutils and replace all instances
        # This string is used in the creation of the invoice in Home.html and Hotel.html
        if request.user.payment_invoice:
            if 'via1-2018-' in request.user.payment_invoice:
                is_paid_with_pp = True
            else:
                is_paid_with_pp = False
        else:
            is_paid_with_pp = False

        context = {'is_early_reg_open': is_early_reg_open, 'is_regular_reg_open': is_regular_reg_open, 'is_alumni_reg_open': is_alumni_reg_open,
                   'is_early_reg_full': is_early_reg_full, 'is_regular_reg_full': is_regular_reg_full, 'is_alumni_reg_full': is_alumni_reg_full,
                   'payment_refund_deadline': regutils.payment_refund_deadline, 'is_refund_open': is_refund_open,
                   'member_school_names': regutils.member_school_names, 'register_types': regutils.RegisterTypes,
                   'register_prices': regutils.RegisterPrices, 'is_paid_with_pp': is_paid_with_pp}
        return render(request, 'registration/home.html', context)
    else:
        return redirect('/registration/login')


def profile(request):
    if request.user.is_authenticated:
        if UserInfo.objects.filter(pk=request.user).exists():
            user_info = UserInfo.objects.get(pk=request.user.id)

            member_school_names = regutils.member_school_names
            graduation_years = regutils.graduation_years
            default_pronouns = regutils.default_pronouns

            # If the current value in user_info.school is not null/blank and not in the list of member schools, the Other choice was chosen
            other_selected = 'false' if (user_info.school in member_school_names) else 'true'
            other_pronouns_selected = 'false' if (user_info.pronouns in default_pronouns) else 'true'

            context = {'user_info': user_info, 'member_school_names': member_school_names, 'other_selected': other_selected,
                       'other_pronouns_selected': other_pronouns_selected, 'graduation_years': graduation_years,
                       'terms_accepted': user_info.waiver_policy_agreement}
            return render(request, 'registration/profile.html', context)
        else:
            user_info = UserInfo(user_id_id=request.user.id)
            user_info.save()
            return redirect('profile')
    else:
        return redirect('/registration/login')


def hotel(request):
    if request.user.is_authenticated:
        user = request.user

        if user.has_paid:
            todays_date = datetime.datetime.now()
            is_hotel_payment_refund_open = True if (todays_date < regutils.payment_refund_deadline) else False
            is_roommate_choosing_open = True if (todays_date < regutils.roommate_deadline) else False

            # Very hacky. We don't want to have a hardcoded string -- perhaps add it to regutils and replace all instances of it
            # This string is used in the creation of the invoice in Home.html and Hotel.html
            # For now, we know that the paypal invoice is going to start with "via1-2018-" (and hotel starts with via1-2018-reg-hotel-),
            # so we'll use that to determine if an attendee paid with PayPal
            if user.hotel_payment_invoice:
                if 'via1-2018-reg-hotel-' in user.hotel_payment_invoice:
                    can_use_refund_button = False
                    purchased_bundle = True
                else:
                    purchased_bundle = False
                    if 'via1-2018-' in user.hotel_payment_invoice:
                        can_use_refund_button = True
                    else:
                        can_use_refund_button = False
            else:
                can_use_refund_button = False
                purchased_bundle = False

            user_info = UserInfo.objects.get(pk=user.id)

            if user_info.room_code:
                # Get all users in the database with this user's room code
                roommates = User.objects.filter(userinfo__room_code=user_info.room_code)
                room_capacity = user_info.room_code[-1:]     # Get the last character of the room code (last character is the room size)
            else:
                roommates = []
                room_capacity = 0

            # For pre-populating roommate name fields for people who bought whole_room
            roommate_one = ''
            roommate_two = ''
            roommate_three = ''
            if user.hotel_type == regutils.HotelPaymentTypes.WHOLE_ROOM:
                if user_info.roommate_list and not user_info.roommate_list == '':
                    whole_room_roommates = user_info.roommate_list.split(',')
                    for i in range(len(whole_room_roommates)):
                        if i == 0:
                            roommate_one = whole_room_roommates[i].strip()
                        if i == 1:
                            roommate_two = whole_room_roommates[i].strip()
                        if i == 2:
                            roommate_three = whole_room_roommates[i].strip()

            context = {'hotel_price': regutils.RegisterPrices.HOTEL_PRICE,
                       'hotel_price_whole': regutils.RegisterPrices.HOTEL_PRICE * 4,
                       'hotel_payment_types': regutils.HotelPaymentTypes,
                       'payment_deadline': regutils.payment_refund_deadline,
                       'roommate_deadline': regutils.roommate_deadline,
                       'is_hotel_payment_refund_open': is_hotel_payment_refund_open,
                       'can_use_refund_button': can_use_refund_button,
                       'purchased_bundle': purchased_bundle,
                       'is_roommate_choosing_open': is_roommate_choosing_open,
                       'is_coed_checked': user_info.coed_roommates,
                       'is_room_leader': user_info.is_room_leader,
                       'room_code': user_info.room_code,
                       'roommates': roommates,
                       'room_capacity': room_capacity,
                       'current_room_size': roommates.count,
                       'roommate_one': roommate_one,
                       'roommate_two': roommate_two,
                       'roommate_three': roommate_three}

            return render(request, 'registration/hotel.html', context)
        else:
            messages.info(request, 'You must be registered for conference to access the hotel page')
            return redirect('home')
    else:
        return redirect('login')


def workshops(request):
    if request.user.is_authenticated():
        if request.user.has_paid:
            session_one_workshops = Workshops.objects.filter(session=1).order_by('id')
            session_two_workshops = Workshops.objects.filter(session=2).order_by('id')

            # Flexbox behaves strangely and mis-aligns the workshop cards on the last row if the row isn't full.
            # To fix the alignment, we figure out how many "hidden" cards we need to make by taking the remainder of mod 3 and
            # subtracting it from 3. See logic in workshops.html to see how these numbers are used.
            session_one_remainder = 3 - session_one_workshops.count() % 3
            session_two_remainder = 3 - session_two_workshops.count() % 3

            todays_date = datetime.datetime.now()
            is_workshops_released = True if (todays_date > regutils.workshop_release_date) else False
            is_workshops_open = True if (todays_date < regutils.workshop_deadline) else False

            user = request.user

            # Explicitly compare vias_attended to None because 0 also evaluates to "false", which we don't want
            if (user.userinfo.photo_name and user.userinfo.school and user.userinfo.pronouns and user.userinfo.banquet_meal
                and user.userinfo.banquet_dessert and user.userinfo.shirt_size and user.userinfo.vias_attended is not None
                and user.userinfo.emergency_contact and user.userinfo.emergency_contact_number
                    and user.userinfo.emergency_contact_relation and user.userinfo.waiver_policy_agreement):
                user_profile_complete = True
            else:
                user_profile_complete = False

            context = {'is_workshops_open': is_workshops_open, 'is_workshops_released': is_workshops_released,
                       'workshops_release_date': regutils.workshop_release_date, 'workshops_deadline': regutils.workshop_deadline,
                       'session_one': session_one_workshops, 'session_two': session_two_workshops,
                       'session_one_remainder': range(session_one_remainder), 'session_two_remainder': range(session_two_remainder),
                       'user_profile_complete': user_profile_complete}
            return render(request, 'registration/workshops.html', context)
        else:
            messages.info(request, 'You must be registered for conference to access the workshops page')
            return redirect('home')
    else:
        return redirect('login')


@login_required()
def families(request):
    # Alternatively, we could've retrieved Family.objects.all() and went from there...
    family_leaders = User.objects.filter(userinfo__is_family_leader=True)

    fl_objects = []
    animation_delay = 0
    for fl in family_leaders:
        if fl.userinfo.family is not None:
            if fl.userinfo.photo_name:
                photo_name = fl.userinfo.photo_name[:-5] + '_big.jpeg'
            else:
                photo_name = None

            animation_delay += 0.15

            fl_objects.append(regutils.FamilyLeader(fl.first_name, fl.last_name, fl.userinfo.family_id, fl.userinfo.family.name, photo_name, animation_delay))

    context = {'family_leaders': fl_objects}

    return render(request, 'registration/families.html', context)


@login_required()
def family(request, fid):
    family = Families.objects.get(pk=fid)

    family_members = User.objects.filter(userinfo__family=family).order_by('pk')

    family_member_objects = []
    animation_delay = 0
    for member in family_members:
        if member.userinfo.photo_name:
            photo_name = member.userinfo.photo_name[:-5] + '_big.jpeg'
        else:
            photo_name = None

        if member.userinfo.is_family_leader is False:
            animation_delay += 0.15

            family_member_objects.append(regutils.FamilyMember(member.first_name, member.last_name, member.userinfo.pronouns,
                                                               member.userinfo.school, member.userinfo.major, member.userinfo.facebook,
                                                               member.userinfo.instagram, member.userinfo.twitter, member.userinfo.snapchat,
                                                               member.userinfo.linkedin, photo_name, animation_delay))
        else:
            fl_object = regutils.FamilyMember(family.leader.first_name, family.leader.last_name,
                                              family.leader.userinfo.pronouns,
                                              family.leader.userinfo.school, family.leader.userinfo.major,
                                              family.leader.userinfo.facebook,
                                              family.leader.userinfo.instagram, family.leader.userinfo.twitter,
                                              family.leader.userinfo.snapchat,
                                              family.leader.userinfo.linkedin, photo_name, None)

    context = {'family_name': family.name, 'family_leader': fl_object, 'family_members': family_member_objects}

    return render(request, 'registration/family.html', context)


@login_required()
def choose_workshop(request, wid):
    if request.method == 'GET':
        if datetime.datetime.now() < regutils.workshop_deadline:
            workshop = Workshops.objects.get(pk=wid)
            if workshop.attendee_count < workshop.capacity:
                user_info = request.user.userinfo

                with transaction.atomic():
                    if workshop.session == 1:
                        if user_info.workshop_one == workshop:
                            messages.info(request, 'You are already signed up for this workshop.')
                            return redirect('workshops')

                        if user_info.workshop_one is not None:
                            prev_workshop = Workshops.objects.get(pk=user_info.workshop_one.id)
                            prev_workshop.attendee_count -= 1
                            prev_workshop.save()

                        user_info.workshop_one = workshop
                    elif workshop.session == 2:
                        if user_info.workshop_two == workshop:
                            messages.info(request, 'You are already signed up for this workshop.')
                            return redirect('workshops')

                        if user_info.workshop_two is not None:
                            prev_workshop = Workshops.objects.get(pk=user_info.workshop_two.id)
                            prev_workshop.attendee_count -= 1
                            prev_workshop.save()

                        user_info.workshop_two = workshop
                    elif workshop.session == 3:
                        if user_info.workshop_three == workshop:
                            messages.info(request, 'You are already signed up for this workshop.')
                            return redirect('workshops')

                        if user_info.workshop_three is not None:
                            prev_workshop = Workshops.objects.get(pk=user_info.workshop_three.id)
                            prev_workshop.attendee_count -= 1
                            prev_workshop.save()

                        user_info.workshop_three = workshop

                    user_info.save()

                    workshop.attendee_count += 1
                    workshop.save()

                    messages.info(request, 'Workshop choice saved!')
                    return redirect('workshops')
            else:
                messages.error(request, 'This workshop is already at capacity.')
                return redirect('workshops')
        else:
            messages.error(request, 'The deadline to choose workshops has passed.')
            return redirect('workshops')
    else:
        return redirect('workshops')


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

        if form.get('pronouns', False) and form['pronouns'] == 'other':
            if user_info.pronouns != form['other_pronouns'] and not (user_info.pronouns is None and form['other_pronouns'] == ''):
                if form['other_pronouns'] == '':
                    user_info.pronouns = None
                else:
                    user_info.pronouns = form['other_pronouns']
        else:
            if form.get('pronouns', False) and user_info.pronouns != form['pronouns']:
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

        if form.get('banquet_dessert', False) and user_info.banquet_dessert != form['banquet_dessert']:
            if form['banquet_dessert'] == '':
                user_info.banquet_dessert = None
            else:
                user_info.banquet_dessert = form['banquet_dessert']

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

        if user_info.vias_attended != form['vias_attended']:
            if form['vias_attended'] == '':
                user_info.vias_attended = None
            else:
                user_info.vias_attended = int(form['vias_attended'])

        user_info.save()

        return JsonResponse({})


@login_required()
@csrf_exempt
def upload_picture(request):
    if request.method == 'POST':
        with transaction.atomic():
            cropped_image = request.POST['croppedImage']
            cropped_image_big = request.POST['croppedImage_big']
            user_info = request.user.userinfo
            file_name = str(randint(100000, 999999)) + str(request.user.id)

            ftp = FTP(settings.FTP_HOST)
            ftp.login(settings.FTP_USERNAME, settings.FTP_PASSWORD)
            ftp.cwd(settings.FTP_PATH)

            bytes_io = io.BytesIO(base64.b64decode(cropped_image))
            bytes_io_big = io.BytesIO(base64.b64decode(cropped_image_big))
            ftp.storbinary('STOR ' + file_name + '.jpeg', bytes_io)
            ftp.storbinary('STOR ' + file_name + '_big.jpeg', bytes_io_big)

            # Delete old photo
            if user_info.photo_name:
                ftp.delete(user_info.photo_name)
                # Remove last 5 characters from the name (".jpeg") and append "_big.jpeg"
                ftp.delete(user_info.photo_name[:-5] + '_big.jpeg')

            ftp.quit()

            user_info.photo_name = file_name + '.jpeg'
            user_info.save()

        return HttpResponse('')
    else:
        return HttpResponse('')


@login_required()
def remove_picture(request):
    if request.method == 'GET':
        user_info = request.user.userinfo

        if user_info.photo_name:
            with transaction.atomic():
                ftp = FTP(settings.FTP_HOST)
                ftp.login(settings.FTP_USERNAME, settings.FTP_PASSWORD)
                ftp.cwd(settings.FTP_PATH)

                ftp.delete(user_info.photo_name)
                ftp.delete(user_info.photo_name[:-5] + '_big.jpeg')
                ftp.quit()

                user_info.photo_name = None
                user_info.save()

                return HttpResponse('')

        else:
            return redirect('profile')

    else:
        return redirect('profile')


@login_required()
def change_waiver_policy_agreement(request):
    if request.is_ajax():
        user_info = UserInfo.objects.get(pk=request.user.id)
        # We do not want to allow people to "un-accept" the terms
        if user_info.waiver_policy_agreement is False:
            waiver_policy_agreement = request.GET.get('waiver_policy_agreement')
            if waiver_policy_agreement == 'checked':
                user_info.waiver_policy_agreement = True
            else:
                user_info.waiver_policy_agreement = False

            user_info.save()
            return JsonResponse({'success': True})
        else:
            response = HttpResponse(content_type='application/json')
            response.status_code = 400
            return response


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
            context = {'user_email': user.email}
            return render(request, 'registration/account_activation_sent.html', context)
        else:
            # Render the login page again and pass back the fields that the user inputted
            # (so we can auto-populate the form)
            return render(request, 'registration/login.html', {'reg_form': form})
    else:
        return redirect('/registration/login')


def resend_activation_email(request):
    if request.method == 'GET':
        form = request.GET
        email = form['email']

        try:
            user = User.objects.get(email=email)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and user.email_confirmed is False:
            current_site = get_current_site(request)
            subject = 'Activate Your VIA-1 Account'
            message = render_to_string('registration/account_activation_email.html', {
                'user': user.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            context = {'user_email': email}
            return render(request, 'registration/account_activation_sent.html', context)
        else:
            context = {'email': email}
            if user is None:
                messages.error(request, 'This email was not found. Please make sure you typed the correct email.')
            else:
                messages.error(request, 'An account using this email has already been activated.')
            return render(request, 'registration/account_activation_resend.html', context)
    else:
        return redirect('index')


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

            user.mem_school_verif_in_prog = True
            user.save()

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
        user.mem_school_verif_in_prog = False
        user.save()

        subject = 'Your VIA-1 Member School Verification Has Been Approved'
        message = render_to_string('registration/mem_school_verif_approved_email.html', {
            'name': user.first_name,
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
        # Just need to change in_prog field to false
        user.mem_school_verif_in_prog = False
        user.save()

        subject = 'Your VIA-1 Member School Verification Has Been Denied'
        message = render_to_string('registration/mem_school_verif_denied_email.html', {
            'name': user.first_name,
            'school': school,
        })
        send_mail(subject, "", None, [user.email], False, None, None, None, message)

        return redirect('/registration/member_school_verification_denied')
    else:
        return redirect('/registration/member_school_verification_invalid')


def alumni_verification_request(request):
    if request.method == 'POST':
        form = request.POST
        user = request.user

        if form['alumni_school'] == 'other':
            school = form['other_alumni_school']
        else:
            school = form['alumni_school']

        if form.get('sponsor', False):
            sponsor = form['sponsor']
        else:
            sponsor = 'not interested'

        if form.get('mentorship_program', False):
            mentorship_program = form['mentorship_program']
        else:
            mentorship_program = 'not interested'

        current_site = get_current_site(request)
        subject = '[ALUMNI VERIFICATION] A VIA-1 Attendee Requests Alumni Verification'
        message = render_to_string('registration/alumni_verif_email.html', {
            'name': user.get_full_name(),
            'email': user.email,
            'positions': form['positions'],
            'school': school,
            'staff_email': form['staff_email'],
            'sponsor': sponsor,
            'mentorship_program': mentorship_program,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': alumni_verification_token.make_token(user),
        })
        send_mail(subject, "", None, ['alumni.programming@uvsamidwest.org'], False, None, None, None, message)

        user.alumni_verif_in_prog = True
        user.save()

        messages.info(request, 'Your verification request has been submitted. You will receive an email upon approval.')
        return redirect('index')
    else:
        return redirect('index')


def alumni_verification_approve(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and alumni_verification_token.check_token(user, token):
        user.is_alumni = True
        user.alumni_verif_in_prog = False
        user.save()

        subject = 'Your VIA-1 Alumni Verification Has Been Approved'
        message = render_to_string('registration/alumni_verification_approved_email.html', {
            'name': user.first_name,
        })
        send_mail(subject, "", None, [user.email], False, None, None, None, message)

        return redirect('/registration/alumni_verification_approved')
    else:
        return redirect('/registration/alumni_verification_invalid')


def alumni_verification_deny(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and alumni_verification_token.check_token(user, token):
        # Just need to change the in_prog field to False
        user.alumni_verif_in_prog = False
        user.save()

        subject = 'Your VIA-1 Alumni Verification Has Been Denied'
        message = render_to_string('registration/alumni_verification_denied_email.html', {
            'name': user.first_name,
        })
        send_mail(subject, "", None, [user.email], False, None, None, None, message)

        return redirect('/registration/alumni_verification_denied')
    else:
        return redirect('/registration/alumni_verification_invalid')


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


# TODO: Check date against deadline
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
                invoice = request.GET.get('payment_invoice')

                user.has_paid = True
                user.time_paid = timezone.now()  # This is a timezone aware method. It'll use the server's timezone (set to CST in settings.py)
                user.reg_type = reg_type
                user.payment_invoice = invoice

                if (reg_type == regutils.RegisterTypes.EARLY_REG_HOTEL or
                            reg_type == regutils.RegisterTypes.REGULAR_REG_HOTEL or
                            reg_type == regutils.RegisterTypes.ALUMNI_REG_HOTEL or
                            reg_type == regutils.RegisterTypes.STAFF_REG_HOTEL):
                    user.has_paid_hotel = True
                    user.hotel_type = regutils.HotelPaymentTypes.SINGLE_SPOT

                user.save()

                # increment attendee count for appropriate attendee_type
                conf_vars = ConferenceVars.objects.get(pk=1)
                if reg_type == regutils.RegisterTypes.EARLY_REG or reg_type == regutils.RegisterTypes.EARLY_REG_HOTEL:
                    conf_vars.early_attendee_count += 1
                elif reg_type == regutils.RegisterTypes.REGULAR_REG or reg_type == regutils.RegisterTypes.REGULAR_REG_HOTEL:
                    conf_vars.regular_attendee_count += 1
                elif reg_type == regutils.RegisterTypes.ALUMNI_REG or reg_type == regutils.RegisterTypes.ALUMNI_REG_HOTEL:
                    conf_vars.alumni_attendee_count += 1
                elif reg_type == regutils.RegisterTypes.STAFF_REG or reg_type == regutils.RegisterTypes.STAFF_REG_HOTEL:
                    conf_vars.staff_attendee_count += 1
                conf_vars.save()

                if reg_type == regutils.RegisterTypes.EARLY_REG:
                    amount = regutils.RegisterPrices.EARLY_REG_PRICE
                    package = 'Early Registration'
                elif reg_type == regutils.RegisterTypes.EARLY_REG_HOTEL:
                    amount = regutils.RegisterPrices.EARLY_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
                    package = 'Early Registration + Hotel Bundle'
                elif reg_type == regutils.RegisterTypes.REGULAR_REG:
                    amount = regutils.RegisterPrices.REGULAR_REG_PRICE
                    package = 'Regular Registration'
                elif reg_type == regutils.RegisterTypes.REGULAR_REG_HOTEL:
                    amount = regutils.RegisterPrices.REGULAR_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
                    package = 'Regular Registration + Hotel Bundle'
                elif reg_type == regutils.RegisterTypes.ALUMNI_REG:
                    amount = regutils.RegisterPrices.ALUMNI_REG_PRICE
                    package = 'Alumni Registration'
                elif reg_type == regutils.RegisterTypes.ALUMNI_REG_HOTEL:
                    amount = regutils.RegisterPrices.ALUMNI_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
                    package = 'Alumni Registration + Hotel Bundle'
                elif reg_type == regutils.RegisterTypes.STAFF_REG:
                    amount = regutils.RegisterPrices.STAFF_REG_PRICE
                    package = 'Staff Registration'
                elif reg_type == regutils.RegisterTypes.STAFF_REG_HOTEL:
                    amount = regutils.RegisterPrices.STAFF_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
                    package = 'Staff Registration + Hotel Bundle'

                subject = 'Thank you for registering for the Vietnamese Interacting As One Conference!'
                message = render_to_string('registration/thanks_for_registering_email.html', {
                    'name': user.first_name,
                    'package': package,
                    'amount': amount
                })
                send_mail(subject, "", None, [user.email], False, None, None, None, message)

                # Just need to send an empty JSON response
                return JsonResponse({})


# TODO: Check date against deadline? Probably wanna do the date check in javascript, too (to prevent them from even accessing the payment)
@login_required()
def update_hotel_paid(request):
    if request.is_ajax():
        user = request.user

        if not user.has_paid_hotel:
            if paypalrestsdk.Payment.find(request.GET.get('paymentID')):
                hotel_type = request.GET.get('hotel_type')
                invoice = request.GET.get('payment_invoice')

                user.has_paid_hotel = True
                user.hotel_type = hotel_type
                user.hotel_payment_invoice = invoice

                user.save()

                if hotel_type == regutils.HotelPaymentTypes.SINGLE_SPOT:
                    amount = regutils.RegisterPrices.HOTEL_PRICE
                    package = 'Hotel - Single Spot'
                elif hotel_type == regutils.HotelPaymentTypes.WHOLE_ROOM:
                    amount = regutils.RegisterPrices.HOTEL_PRICE * 4
                    package = 'Hotel - Whole Room'

                subject = 'Your VIA-1 Hotel Payment Confirmation'
                message = render_to_string('registration/hotel_payment_confirmation_email.html', {
                    'name': user.first_name,
                    'package': package,
                    'amount': amount
                })
                send_mail(subject, "", None, [user.email], False, None, None, None, message)

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
                'pp_invoice': user.payment_invoice,
                'pp_hotel_invoice': user.hotel_payment_invoice,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': refund_request_token.make_token(user),
            })

            send_mail(subject, "", None, ['via1.finance@uvsamidwest.org'], False, None, None, None, message)

            messages.info(request, 'Your refund request has been submitted. You will receive an email once the Finance committee has issued your refund.')
            return redirect('index')
    else:
        return redirect('index')


# This gets called from the email sent to the Finance committee when they hit the "Complete Refund" button.
# Note that this method only handles cases where the user pays through the website (and thus PayPal).
# e.g. If a user pays manually (say Venmo) and gets a custom payment invoice ID, this method will NOT know what to do.
def refund_request_complete(request, uidb64, token, pp_email):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and refund_request_token.check_token(user, token):
        # Decrement attendee count for appropriate attendee_type
        conf_vars = ConferenceVars.objects.get(pk=1)
        if user.reg_type == regutils.RegisterTypes.EARLY_REG or user.reg_type == regutils.RegisterTypes.EARLY_REG_HOTEL:
            conf_vars.early_attendee_count -= 1
        elif user.reg_type == regutils.RegisterTypes.REGULAR_REG or user.reg_type == regutils.RegisterTypes.REGULAR_REG_HOTEL:
            conf_vars.regular_attendee_count -= 1
        elif user.reg_type == regutils.RegisterTypes.ALUMNI_REG or user.reg_type == regutils.RegisterTypes.ALUMNI_REG_HOTEL:
            conf_vars.alumni_attendee_count -= 1
        elif user.reg_type == regutils.RegisterTypes.STAFF_REG or user.reg_type == regutils.RegisterTypes.STAFF_REG_HOTEL:
            conf_vars.staff_attendee_count -= 1
        conf_vars.save()

        hotel_amount = 'None'
        amount = 'None'
        if user.reg_type == regutils.RegisterTypes.EARLY_REG:
            amount = regutils.RegisterPrices.EARLY_REG_PRICE
            if user.hotel_type == regutils.HotelPaymentTypes.SINGLE_SPOT:
                hotel_amount = regutils.RegisterPrices.HOTEL_PRICE
            elif user.hotel_type == regutils.HotelPaymentTypes.WHOLE_ROOM:
                hotel_amount = regutils.RegisterPrices.HOTEL_PRICE * 4
        elif user.reg_type == regutils.RegisterTypes.EARLY_REG_HOTEL:
            amount = regutils.RegisterPrices.EARLY_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
        elif user.reg_type == regutils.RegisterTypes.REGULAR_REG:
            amount = regutils.RegisterPrices.REGULAR_REG_PRICE
            if user.hotel_type == regutils.HotelPaymentTypes.SINGLE_SPOT:
                hotel_amount = regutils.RegisterPrices.HOTEL_PRICE
            elif user.hotel_type == regutils.HotelPaymentTypes.WHOLE_ROOM:
                hotel_amount = regutils.RegisterPrices.HOTEL_PRICE * 4
        elif user.reg_type == regutils.RegisterTypes.REGULAR_REG_HOTEL:
            amount = regutils.RegisterPrices.REGULAR_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
        elif user.reg_type == regutils.RegisterTypes.ALUMNI_REG:
            amount = regutils.RegisterPrices.ALUMNI_REG_PRICE
            if user.hotel_type == regutils.HotelPaymentTypes.SINGLE_SPOT:
                hotel_amount = regutils.RegisterPrices.HOTEL_PRICE
            elif user.hotel_type == regutils.HotelPaymentTypes.WHOLE_ROOM:
                hotel_amount = regutils.RegisterPrices.HOTEL_PRICE * 4
        elif user.reg_type == regutils.RegisterTypes.ALUMNI_REG_HOTEL:
            amount = regutils.RegisterPrices.ALUMNI_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE
        elif user.reg_type == regutils.RegisterTypes.STAFF_REG:
            amount = regutils.RegisterPrices.STAFF_REG_PRICE
            if user.hotel_type == regutils.HotelPaymentTypes.SINGLE_SPOT:
                hotel_amount = regutils.RegisterPrices.HOTEL_PRICE
            elif user.hotel_type == regutils.HotelPaymentTypes.WHOLE_ROOM:
                hotel_amount = regutils.RegisterPrices.HOTEL_PRICE * 4
        elif user.reg_type == regutils.RegisterTypes.STAFF_REG_HOTEL:
            amount = regutils.RegisterPrices.STAFF_REG_PRICE + regutils.RegisterPrices.HOTEL_BUNDLE_PRICE

        # Need to change user's payment status
        user.has_paid = False
        user.time_paid = None
        user.reg_type = None
        user.payment_invoice = None

        if user.has_paid_hotel:
            user.has_paid_hotel = False
            user.hotel_type = None
            user.hotel_payment_invoice = None

        user.save()

        # Send an email to the user letting them know that their refund has been fulfilled
        subject = 'Your VIA-1 Registration Refund Has Been Fulfilled'
        message = render_to_string('registration/refund_request_complete_email.html', {
            'name': user.first_name,
            'pp_email': pp_email,
            'amount': str(amount),
            'hotel_amount': str(hotel_amount)
        })
        send_mail(subject, "", None, [user.email], False, None, None, None, message)

        return redirect('/registration/refund_request_complete')


def refund_hotel_request(request):
    if request.method == 'POST':
        form = request.POST
        user = request.user

        # Only proceed if the user has paid for hotel
        if user.has_paid_hotel:
            current_site = get_current_site(request)
            subject = '[REFUND REQUEST] A VIA-1 Attendee Requests A Hotel Refund'
            message = render_to_string('registration/hotel_refund_request_email.html', {
                'name': user.get_full_name(),
                'email': user.email,
                'pp_name': form['pp_name'],
                'pp_email': form['pp_email'],
                'pp_hotel_invoice': user.hotel_payment_invoice,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': refund_hotel_request_token.make_token(user),
            })

            send_mail(subject, "", None, ['via1.finance@uvsamidwest.org'], False, None, None, None, message)

            messages.info(request, 'Your refund request has been submitted. You will receive an email once the Finance committee has issued your refund.')
            return redirect('hotel')
    else:
        return redirect('index')


def refund_hotel_request_complete(request, uidb64, token, pp_email):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and refund_hotel_request_token.check_token(user, token):
        hotel_amount = 'None'
        if user.hotel_type == regutils.HotelPaymentTypes.SINGLE_SPOT:
            hotel_amount = regutils.RegisterPrices.HOTEL_PRICE
        elif user.hotel_type == regutils.HotelPaymentTypes.WHOLE_ROOM:
            hotel_amount = regutils.RegisterPrices.HOTEL_PRICE * 4

        # Need to change user's hotel payment status
        user.has_paid_hotel = False
        user.hotel_type = None
        user.hotel_payment_invoice = None

        user.save()

        # Send an email to the user letting them know that their refund has been fulfilled
        subject = 'Your VIA-1 Hotel Refund Has Been Fulfilled'
        message = render_to_string('registration/refund_hotel_request_complete_email.html', {
            'name': user.first_name,
            'pp_email': pp_email,
            'hotel_amount': str(hotel_amount)
        })
        send_mail(subject, "", None, [user.email], False, None, None, None, message)

        return redirect('/registration/refund_request_complete')


@login_required()
def change_coed_preference(request):
    if request.is_ajax():
        user_info = UserInfo.objects.get(pk=request.user.id)
        coed_roommates = request.GET.get('coed_roommates')

        if coed_roommates == 'checked':
            user_info.coed_roommates = True
        else:
            user_info.coed_roommates = False

        user_info.save()

        return JsonResponse({})


@login_required()
def create_hotel_room(request):
    if request.method == 'GET':
        user_info = UserInfo.objects.get(pk=request.user.id)
        if not user_info.is_room_leader and user_info.room_code is None:
            group_size = request.GET.get('group_size')
            room_code = str(user_info.user_id.id) + '-' + str(randint(100, 999)) + '-' + group_size

            user_info.is_room_leader = True
            user_info.room_code = room_code
            user_info.save()
            return redirect('hotel')
        else:
            return redirect('hotel')
    else:
        return redirect('index')


@login_required()
def disband_room(request):
    user_info = request.user.userinfo

    is_roommate_choosing_open = True if (datetime.datetime.now() < regutils.roommate_deadline) else False

    if user_info.room_code and user_info.is_room_leader and is_roommate_choosing_open:
        room_code = user_info.room_code

        user_info.room_code = None
        user_info.is_room_leader = False
        user_info.save()

        emails = []
        user_infos = UserInfo.objects.filter(room_code=room_code)
        for ui in user_infos:
            # Only want to send email out to roommates who aren't the group leader
            if not ui.is_room_leader:
                emails.append(ui.user_id.email)
            ui.room_code = None
            ui.save()

        subject = 'Your VIA-1 hotel group has been disbanded'
        message = render_to_string('registration/remove_roommate_email.html', {
            'name': 'VIA-1 Attendee',
            'leader_name': request.user.get_full_name(),
            'leader_email': request.user.email,
            'disbanded': True
        })
        send_mail(subject, "", None, emails, False, None, None, None, message)

    elif user_info.room_code and is_roommate_choosing_open:
        user_info.room_code = None
        user_info.save()

    return redirect('hotel')


@login_required()
def join_room(request):
    is_roommate_choosing_open = True if (datetime.datetime.now() < regutils.roommate_deadline) else False
    if request.method == 'GET' and is_roommate_choosing_open:
        room_code = request.GET.get('room_code')
        if UserInfo.objects.filter(room_code=room_code).exists():
            user_infos = UserInfo.objects.filter(room_code=room_code)

            capacity = room_code[-1:]
            if user_infos.count() < int(capacity):
                user_info = request.user.userinfo
                user_info.room_code = room_code
                user_info.save()
                return redirect('hotel')
            else:
                messages.error(request, 'Sorry, that group is full.')
                return redirect('hotel')

        else:
            messages.error(request, 'Sorry, that group code is invalid.')
            return redirect('hotel')

    else:
        return redirect('hotel')


@login_required()
def remove_roommate(request):
    is_roommate_choosing_open = True if (datetime.datetime.now() < regutils.roommate_deadline) else False
    if request.method == 'GET' and is_roommate_choosing_open:
        if request.user.userinfo.is_room_leader:
            user_info = UserInfo.objects.get(user_id__email=request.GET.get('email'))
            user_info.room_code = None
            user_info.save()

            subject = 'You have been removed from your VIA-1 hotel group'
            message = render_to_string('registration/remove_roommate_email.html', {
                'name': user_info.user_id.first_name,
                'leader_name': request.user.get_full_name(),
                'leader_email': request.user.email
            })
            send_mail(subject, "", None, [user_info.user_id.email], False, None, None, None, message)

            return redirect('hotel')
        else:
            return redirect('hotel')

    else:
        return redirect('hotel')


@login_required()
def whole_room_save_roommates(request):
    is_roommate_choosing_open = True if (datetime.datetime.now() < regutils.roommate_deadline) else False
    if request.method == 'GET' and is_roommate_choosing_open:
        user_info = request.user.userinfo

        list_of_roommates = ''
        if request.GET.get('roommate_one'):
            list_of_roommates += request.GET.get('roommate_one').strip() + ', '

        if request.GET.get('roommate_two'):
            list_of_roommates += request.GET.get('roommate_two').strip() + ', '

        if request.GET.get('roommate_three'):
            list_of_roommates += request.GET.get('roommate_three').strip()

        if list_of_roommates == '':
            user_info.roommate_list = None
        else:
            user_info.roommate_list = list_of_roommates

        user_info.save()

        return JsonResponse({})
    else:
        return redirect('hotel')


@login_required()
def code_generator(request):
    if request.user.is_staff:
        codes = SpecialRegCodes.objects.order_by('-date_created', '-pk')
        context = {'code_types': regutils.CodeTypes, 'code_types_list': regutils.code_types,
                   'methods_of_payment_list': regutils.methods_of_payment, 'codes': codes}
        return render(request, 'registration/code_generator.html', context)
    else:
        return redirect('home')


@login_required()
def generate_code(request):
    if request.user.is_staff:
        if request.method == 'GET':
            code = request.GET.get('code').upper()

            if SpecialRegCodes.objects.filter(code__contains=code).exists():
                messages.info(request, 'That code already exists in the system. Try again.')
                return redirect('code_generator')
            else:
                code_type = request.GET.get('code_type')
                date_created = timezone.now()
                includes_hotel = True if request.GET.get('includes_hotel', False) else False
                number_of_usages = int(request.GET.get('number_of_usages'))

                # Waitlist and Banquet codes should expire within 24 hours of creation by default
                if code_type == regutils.CodeTypes.WAITLIST_REG or code_type == regutils.CodeTypes.BANQUET:
                    date_expired = date_created + timedelta(days=1)
                    method_of_payment = None
                    includes_hotel = False
                elif code_type == regutils.CodeTypes.FAMILY_LEADER:
                    date_expired = regutils.payment_refund_deadline
                    method_of_payment = None
                    includes_hotel = False
                elif code_type == regutils.CodeTypes.STAFF_REG:
                    date_expired = regutils.staff_payment_deadline
                    method_of_payment = request.GET.get('method_of_payment')
                elif code_type == regutils.CodeTypes.REGULAR_REG:
                    date_expired = regutils.regular_reg_close_date
                    method_of_payment = request.GET.get('method_of_payment')
                elif code_type == regutils.CodeTypes.SPECIAL:
                    date_expired = regutils.payment_refund_deadline
                    method_of_payment = request.GET.get('method_of_payment')
                else:
                    date_expired = regutils.payment_refund_deadline
                    method_of_payment = None

                # If extended_deadline option was selected, just overwrite the previously set expiration date
                if request.GET.get('extended_deadline', False):
                    date_expired = date_created + timedelta(days=60)

                if request.GET.get('multi_use', False) or number_of_usages == 1:
                    code_obj = SpecialRegCodes(code=code,
                                               usages_left=number_of_usages,
                                               code_type=code_type,
                                               method_of_payment=method_of_payment,
                                               includes_hotel=includes_hotel,
                                               date_created=date_created,
                                               date_expired=date_expired)
                    code_obj.save()
                else:
                    for i in range(0, number_of_usages):
                        code_obj = SpecialRegCodes(code=code + '_' + str(i+1),
                                                   usages_left=1,
                                                   code_type=code_type,
                                                   method_of_payment=method_of_payment,
                                                   includes_hotel=includes_hotel,
                                                   date_created=date_created,
                                                   date_expired=date_expired)
                        code_obj.save()

                return redirect('code_generator')
        else:
            return redirect('code_generator')
    else:
        return redirect('index')


@login_required()
def remove_code(request):
    if request.user.is_staff:
        if request.method == 'GET':
            code = request.GET.get('code')

            if SpecialRegCodes.objects.filter(code=code).exists():
                code_obj = SpecialRegCodes.objects.get(code=request.GET.get('code'))
                code_obj.delete()

                message = 'The code [' + code + '] has been deleted.'
                messages.info(request, message)
                return redirect('code_generator')
            else:
                messages.info(request, 'That code does not exist.')
                return redirect('code_generator')

        else:
            return redirect('code_generator')
    else:
        return redirect('index')


# TODO: Send confirmation email for registration, similar to update_code_attendee
# Also might want to rename this... to like "consume_code" or "use_code"
@login_required()
def registration_code(request):
    if request.method == 'GET':
        error = None
        # Check if reg code is valid
        if SpecialRegCodes.objects.filter(code=request.GET.get('reg_code')).exists():
            reg_code = SpecialRegCodes.objects.get(code=request.GET.get('reg_code'))
            user = request.user

            # Check if reg code is expired
            if timezone.now() < reg_code.date_expired:
                if (reg_code.code_type == regutils.CodeTypes.WAITLIST_REG or
                        reg_code.code_type == regutils.CodeTypes.BANQUET or
                        reg_code.code_type == regutils.CodeTypes.FAMILY_LEADER):
                    context = {'reg_code': reg_code, 'code_types': regutils.CodeTypes, 'register_prices': regutils.RegisterPrices}
                    return render(request, 'registration/code_payment.html', context)
                else:
                    conf_vars = ConferenceVars.objects.get(pk=1)
                    if ((reg_code.code_type == regutils.CodeTypes.REGULAR_REG and
                        datetime.datetime.now() > regutils.regular_reg_open_date and
                        conf_vars.regular_attendee_count < regutils.RegisterCaps.REGULAR_REG_CAP) or
                            (reg_code.code_type == regutils.CodeTypes.STAFF_REG or reg_code.code_type == regutils.CodeTypes.SPECIAL)):
                        with transaction.atomic():
                            user.has_paid = True
                            user.time_paid = timezone.now()
                            user.reg_type = 'CODE-' + reg_code.code
                            user.payment_invoice = reg_code.method_of_payment

                            if reg_code.includes_hotel:
                                user.has_paid_hotel = True
                                user.hotel_type = regutils.HotelPaymentTypes.SINGLE_SPOT

                            user.save()

                            # Perhaps we wanna add counters into conf_vars for every other missing attendee type
                            # (family leaders, Special code, etc.)
                            # Incrementing regular count for Special Code + Scholarship type is confusing, which
                            # reinforces this idea
                            if reg_code.code_type == regutils.CodeTypes.REGULAR_REG:
                                conf_vars.regular_attendee_count += 1
                                conf_vars.save()
                            elif reg_code.code_type == regutils.CodeTypes.STAFF_REG:
                                conf_vars.staff_attendee_count += 1
                                conf_vars.save()
                            elif reg_code.code_type == regutils.CodeTypes.SPECIAL and reg_code.method_of_payment == 'Scholarship':
                                conf_vars.regular_attendee_count += 1
                                conf_vars.save()

                            reg_code.usages_left -= 1
                            # If the last usage was used, delete the code
                            if reg_code.usages_left <= 0:
                                reg_code.delete()
                            else:
                                reg_code.save()
                    else:
                        error = 'The registration code you provided (' + reg_code.code + ') is valid, however, regular registration is either full or the registration period has not begun.'

            else:
                error = 'The registration code you provided (' + reg_code.code + ') has already expired.'
                # Since the code is expired, delete it
                reg_code.delete()

        else:
            error = 'The code you provided (' + request.GET.get('reg_code') + ') is not valid. Please try again.'

        return render(request, 'registration/reg_code_complete.html', {'error': error, 'code': request.GET.get('reg_code')})

    else:
        return redirect('index')


@login_required()
def update_code_attendee(request):
    if request.is_ajax():
        user = User.objects.get(pk=request.user.id)
        reg_code = SpecialRegCodes.objects.get(code=request.GET.get('code'))

        if not user.has_paid:
            # Need to check if that paymentID exists so that people can't send fake calls to this endpoint
            if paypalrestsdk.Payment.find(request.GET.get('paymentID')):
                with transaction.atomic():
                    user.has_paid = True
                    user.time_paid = timezone.now()
                    user.reg_type = 'CODE-' + reg_code.code
                    user.payment_invoice = request.GET.get('payment_invoice')

                    user.save()

                    if reg_code.code_type == regutils.CodeTypes.WAITLIST_REG:
                        conf_vars = ConferenceVars.objects.get(pk=1)
                        conf_vars.regular_attendee_count += 1
                        conf_vars.save()

                    reg_code.usages_left -= 1
                    # If the last usage was used, delete the code
                    if reg_code.usages_left <= 0:
                        reg_code.delete()
                    else:
                        reg_code.save()

                if reg_code.code_type == regutils.CodeTypes.WAITLIST_REG or reg_code.code_type == regutils.CodeTypes.FAMILY_LEADER:
                    amount = regutils.RegisterPrices.REGULAR_REG_PRICE
                elif reg_code.code_type == regutils.CodeTypes.BANQUET:
                    amount = regutils.RegisterPrices.BANQUET_PRICE

                subject = 'Thank you for registering for the Vietnamese Interacting As One Conference!'
                message = render_to_string('registration/thanks_for_registering_email.html', {
                    'name': user.first_name,
                    'package': reg_code.code_type,
                    'amount': amount
                })
                send_mail(subject, "", None, [user.email], False, None, None, None, message)

                # Just need to send an empty JSON response
                return JsonResponse({})
