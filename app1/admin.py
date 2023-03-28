# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser,Avatar

class AvatarAdmin(admin.ModelAdmin):
    list_display = ('child_name', 'avatar_image')

admin.site.register(Avatar, AvatarAdmin)


class MyUserAdmin(UserAdmin):
    model = MyUser
    list_display = ['mobile_number']

admin.site.register(MyUser, MyUserAdmin)

