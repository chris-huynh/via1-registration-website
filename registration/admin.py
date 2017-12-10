from django.contrib import admin

from registration.models import ConferenceVars, Workshops, User, UserInfo, Families

# Register your models here.
admin.site.register(ConferenceVars)
admin.site.register(User)
admin.site.register(UserInfo)
admin.site.register(Workshops)
admin.site.register(Families)