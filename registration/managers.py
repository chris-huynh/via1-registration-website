from django.contrib.auth.base_user import BaseUserManager

from registration import regutils

class UserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """
    def _create_user(self, email, password, first_name, last_name, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name

        email_handle = email.split("@", 1)[1]
        if email_handle in regutils.member_school_emails:
            user.is_member_school = True

        user.save()
        return user

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        # Not exactly sure if all of these need to be here?
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_member_school', False)
        extra_fields.setdefault('is_alumni', False)
        # Set them to non-active because they need to verify email first
        extra_fields.setdefault('is_active', False)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

    def create_superuser(self, email, password, first_name=None, last_name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        # When we create super users, we don't really care if their email works. Only admins will be creating superusers
        extra_fields.setdefault('email_confirmed', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, first_name, last_name, **extra_fields)

