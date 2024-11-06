from django.contrib import admin
from matching.models import UserContacts, UserScore, UserLocation, CloseFriendList
from userprofile.models import ProfileDetails
# Register your models here.

class UserContactsAdmin(admin.ModelAdmin):

    list_display = ("get_following", "get_follower")
    def get_following(self, obj):
        profile = ProfileDetails.objects.get(uuid=obj.following)
        return profile
    def get_follower(self, obj):
        profile = ProfileDetails.objects.get(uuid=obj.follower)
        return profile

class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_location', 'place', 'unit')
    search_fields = ('last_location', 'user', 'place')


admin.site.register(UserContacts, UserContactsAdmin)
admin.site.register(UserScore)
admin.site.register(UserLocation, UserLocationAdmin)
admin.site.register(CloseFriendList)