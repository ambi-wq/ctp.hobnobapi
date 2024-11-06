from django.contrib import admin
from .models import ProfileDetails, Interest, UserImages, UserPreference, InstagramConnect, SpotifyConnect, DisplayPicture, UserPromptQA, PromptQuestions, UserContactList, UsersContacts,UserImagesComment
# Register your models here.
class ProfileDetailsAdmin(admin.ModelAdmin):
    list_display = ("username", "uuid", )

admin.site.register(ProfileDetails, ProfileDetailsAdmin)
admin.site.register(Interest)
admin.site.register(UserImages)
admin.site.register(UserPreference)
admin.site.register(InstagramConnect)
admin.site.register(SpotifyConnect)
admin.site.register(DisplayPicture)
admin.site.register(UserPromptQA)
admin.site.register(PromptQuestions)

admin.site.register(UserContactList)
admin.site.register(UsersContacts)

admin.site.register(UserImagesComment)
