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
        help_text=_('Designates whether the user can log into this site.'),
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

    has_paid = models.BooleanField(default=False)
    has_paid_hotel = models.BooleanField(default=False)
    time_paid = models.DateTimeField(default=None, null=True)
    reg_type = models.CharField(_('registration type'), max_length=50, blank=True, null=True)


    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


# For variables that need to persist
class ConferenceVars(models.Model):
    early_attendee_count = models.IntegerField(default=0, null=True)
    regular_attendee_count = models.IntegerField(default=0, null=True)
    alumni_attendee_count = models.IntegerField(default=0, null=True)
    staff_attendee_count = models.IntegerField(default=0, null=True)


#class Families(models.Model):


#class Workshops(models.Model):


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
    food_allergies = models.CharField(_('food allergies'), max_length=65, blank=True, null=True)
    emergency_contact = models.CharField(_('emergency contact'), max_length=50, blank=True, null=True)
    emergency_contact_number = models.CharField(_('emergency contact phone number'), max_length=10, blank=True, null=True)
    emergency_contact_relation = models.CharField(_('emergency contact relation'), max_length=20, blank=True, null=True)
    shirt_size = models.CharField(_('shirt size'), max_length=15, blank=True, null=True)
    coed_roommates = models.BooleanField(default=False)
    #photo_name = models.CharField(_('photo name'), max_length=25, blank=True, null=True)
