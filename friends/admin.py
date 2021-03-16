from friends.models import FriendList, FriendRequest
from django.contrib import admin
from django.db import models

# Register your models here.
class FriendListadmin(admin.ModelAdmin):
    list_filter = ['user']
    list_display = ['user']
    search_fields = ['user']
    readonly_fields = ['user']


    class Meta:
        model = FriendList
admin.site.register(FriendList,FriendListadmin)


class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ['sender', 'receiver']
    list_display = ['sender', 'receiver']
    search_fields = ['sender__username', 'receiver__username']

    class Meta:
        model = FriendRequest


admin.site.register(FriendRequest,FriendRequestAdmin)