from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail


from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=False, null=True)
    middle_name = models.CharField(_('middle name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=False, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Currently gives the user access to the code generator page. Will need to repurpose later'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    email_confirmed = models.BooleanField(default=False)
    is_member_school = models.BooleanField(default=False)
    is_alumni = models.BooleanField(default=False)
    alumni_verif_in_prog = models.BooleanField(default=False)
    mem_school_verif_in_prog = models.BooleanField(default=False)
    has_paid = models.BooleanField(default=False)
    time_paid = models.DateTimeField(default=None, blank=True, null=True)
    reg_type = models.CharField(_('registration type'), max_length=50, blank=True, null=True)
    payment_invoice = models.CharField(_('payment invoice id'), max_length=40, blank=True, null=True)
    has_paid_hotel = models.BooleanField(default=False)
    hotel_type = models.CharField(_('hotel type'), max_length=15, blank=True, null=True)
    hotel_payment_invoice = models.CharField(_('hotel payment invoice id'), max_length=40, blank=True, null=True,
                                             help_text='This field is also used for method of payment (if the user didnt register the standard way (e.g. reg code, bulk pay, etc.))')

    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return self.get_full_name() + ' (' + self.email + ')'

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        # sends an email to this user
        send_mail(subject, message, from_email, [self.email], **kwargs)


# For variables that need to persist
class ConferenceVars(models.Model):
    early_attendee_count = models.IntegerField(default=0, null=True)
    regular_attendee_count = models.IntegerField(default=0, null=True)
    alumni_attendee_count = models.IntegerField(default=0, null=True)
    staff_attendee_count = models.IntegerField(default=0, null=True)


class Families(models.Model):
    name = models.CharField(_('family name'), max_length=30, blank=True, null=True)
    leader = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name + ' (FL: ' + self.leader.get_full_name() + ')'


class Workshops(models.Model):
    name = models.CharField(_('workshop name'), max_length=100, blank=True, null=True)
    first_name = models.CharField(_('presenter first name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('presenter last name'), max_length=30, blank=True, null=True)
    presenter_description = models.TextField(_('presenter description'), blank=True, null=True)
    description = models.TextField(_('workshop description'), blank=True, null=True)
    capacity = models.IntegerField(_('workshop capacity'), blank=True, null=True)
    attendee_count = models.IntegerField(
        _('attendee count'),
        default=0,
        blank=True,
        null=True,
        help_text=_(
            'This value should be 0 for new workshops. DO NOT adjust this number after a workshop is created.'
        ),
    )
    SESSION_ONE = 1
    SESSION_TWO = 2
    SESSION_THREE = 3
    SESSION_CHOICES = (
        (SESSION_ONE, '1'),
        (SESSION_TWO, '2'),
        (SESSION_THREE, '3'),
    )
    session = models.IntegerField(choices=SESSION_CHOICES, default=SESSION_ONE)
    presenter_photo = models.CharField(_('presenter photo name'), max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


# Additional user fields
# Don't forget 3 workshop columns(foreign), family_id (foreign?)
class UserInfo(models.Model):
    user_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    phone_number = models.CharField(_('phone number'), max_length=10, blank=True, null=True)
    birth_date = models.DateField(_('birth date'), default=None, blank=True, null=True)
    school = models.CharField(_('school'), max_length=65, blank=True, null=True)
    grad_year = models.IntegerField(_('graduation year'), default=None, blank=True, null=True)
    major = models.CharField(_('major'), max_length=65, blank=True, null=True)
    pronouns = models.CharField(_('gender pronouns'), max_length=25, blank=True, null=True)
    facebook = models.CharField(_('facebook handle'), max_length=25, blank=True, null=True)
    instagram = models.CharField(_('instagram handle'), max_length=25, blank=True, null=True)
    twitter = models.CharField(_('twitter handle'), max_length=25, blank=True, null=True)
    snapchat = models.CharField(_('snapchat handle'), max_length=25, blank=True, null=True)
    linkedin = models.CharField(_('linkedin handle'), max_length=25, blank=True, null=True)
    banquet_meal = models.CharField(_('banquet meal'), max_length=50, blank=True, null=True)
    banquet_dessert = models.CharField(_('banquet dessert'), max_length=50, blank=True, null=True)
    food_allergies = models.CharField(_('food allergies'), max_length=65, blank=True, null=True)
    emergency_contact = models.CharField(_('emergency contact'), max_length=50, blank=True, null=True)
    emergency_contact_number = models.CharField(_('emergency contact phone number'), max_length=10, blank=True, null=True)
    emergency_contact_relation = models.CharField(_('emergency contact relation'), max_length=20, blank=True, null=True)
    shirt_size = models.CharField(_('shirt size'), max_length=15, blank=True, null=True)
    vias_attended = models.IntegerField(_('VIA-1s attended'), default=None, blank=True, null=True)
    workshop_one = models.ForeignKey(Workshops, on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='workshop_one')
    workshop_two = models.ForeignKey(Workshops, on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='workshop_two')
    workshop_three = models.ForeignKey(Workshops, on_delete=models.SET_NULL, blank=True, null=True, default=None, related_name='workshop_three')
    is_family_leader = models.BooleanField(default=False)
    family = models.ForeignKey(Families, on_delete=models.SET_NULL, blank=True, null=True, default=None)
    photo_name = models.CharField(_('photo name'), max_length=20, blank=True, null=True)
    coed_roommates = models.BooleanField(
        default=False,
        help_text=_(
            'Whether or not the attendee is okay with having co-ed roommates.'
        ),
    )
    is_room_leader = models.BooleanField(default=False)
    room_code = models.CharField(_('room code'), max_length=15, blank=True, null=True)
    roommate_list = models.CharField(
        _('roommate list'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_(
            'This will only be used by people who purchased a whole room.'
        ),
    )

    def __str__(self):
        return str(self.user_id)


class SpecialRegCodes(models.Model):
    code = models.CharField(_('special code'), max_length=25, blank=True, null=True)
    usages_left = models.IntegerField(_('number of usages left'), default=0, null=True)
    code_type = models.CharField(_('code type'), max_length=30, blank=True, null=True)
    method_of_payment = models.CharField(_('method of payment'), max_length=20, blank=True, null=True)
    includes_hotel = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=None, blank=True, null=True)
    date_expired = models.DateTimeField(default=None, blank=True, null=True)

    def __str__(self):
        return self.code
