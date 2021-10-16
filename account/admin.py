from django.contrib import admin
from .models import User, UserOtp


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    model = User
    search_fields = ('mobile_number', 'email')
    list_filter = ('is_admin','is_professor')
    list_display = ('mobile_number', 'first_name','email','is_active')

class OtpAdmin(admin.ModelAdmin):
    model = UserOtp
    search_fields = ('user__mobile_number', 'user__email_address')








admin.site.register(User, UserAdmin)

admin.site.register(UserOtp,OtpAdmin)
