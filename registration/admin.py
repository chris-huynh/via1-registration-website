from django.contrib import admin

from registration.models import ConferenceVars, Workshops, User, UserInfo, Families, SpecialRegCodes


admin.site.site_header = 'VIA-1 Administration'


class UserAdmin(admin.ModelAdmin):
    list_filter = ['has_paid', 'has_paid_hotel', 'is_staff', 'hotel_type']
    search_fields = ['first_name', 'last_name', 'email']


class UserInfoAdmin(admin.ModelAdmin):
    list_filter = ['school', 'family', 'banquet_meal', 'shirt_size', 'pronouns']
    list_max_show_all = 1000


# Register your models here.
admin.site.register(ConferenceVars)
admin.site.register(User, UserAdmin)
admin.site.register(UserInfo, UserInfoAdmin)
admin.site.register(Workshops)
admin.site.register(Families)
admin.site.register(SpecialRegCodes)
