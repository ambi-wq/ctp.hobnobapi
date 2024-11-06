from django.contrib import admin
from .models import DeviceRegistry, Notification

# Register your models here.
admin.site.register(DeviceRegistry)
admin.site.register(Notification)
