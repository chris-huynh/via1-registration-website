from django.contrib import admin

from registration.models import ConferenceVars, Workshops, User, UserInfo, Families


class UserAdmin(admin.ModelAdmin):
    list_filter = ['has_paid', 'has_paid_hotel']


# Register your models here.
admin.site.register(ConferenceVars)
admin.site.register(User, UserAdmin)
admin.site.register(UserInfo)
admin.site.register(Workshops)
admin.site.register(Families)
