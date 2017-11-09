from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail


from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=False, null=True)
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


# class User(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(_('email address'), unique=True)
#     first_name = models.CharField(_('first name'), max_length=30, blank=False)
#     last_name = models.CharField(_('last name'), max_length=30, blank=False)
#     date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
#     is_active = models.BooleanField(_('active'), default=True)
#     portrait_location = models.CharField(_('portrait location'), max_length=50, blank=True)
#     is_staff = models.BooleanField(_('staff'), default=False)
#
#     objects = UserManager()
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
#
#     class Meta:
#         verbose_name = _('user')
#         verbose_name_plural = _('users')
#
#     def get_full_name(self):
#         '''
#         Returns the first_name plus the last_name, with a space in between.
#         '''
#         full_name = '%s %s' % (self.first_name, self.last_name)
#         return full_name.strip()
#
#     def get_short_name(self):
#         '''
#         Returns the short name for the user.
#         '''
#         return self.first_name
#
#     # def email_user(self, subject, message, from_email=None, **kwargs):
#     #     '''
#     #     Sends an email to this User.
#     #     '''
#     #     send_mail(subject, message, from_email, [self.email], **kwargs)