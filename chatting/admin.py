from django.contrib import admin
from chatting.models import Message, Room

# Register your models here.
admin.site.register(Message)
# admin.site.register(Contact)
admin.site.register(Room)