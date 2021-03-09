from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class UserAdminConfig(UserAdmin):
    search_fields = ('email','username','name')
    ordering = ('-start_date',)
    list_display = ('email','username','name','is_active','is_staff')

    fieldsets = (
        (None,{'fields':('email','username','name')}),
        ('Permissions',{'fields':('is_staff','is_active')}),
        ('Personal',{'fields':('about','friends')})
    )

    add_fieldsets = (
        (None, {
            'classes':('wide',),
            'fields':('email','username','name','password1','password2','friends','is_active','is_staff')
        }),
    )

admin.site.register(User,UserAdminConfig)