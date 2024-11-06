from django.contrib import admin
from events.models import Events, EventImages, CuratedEvents, EventComments, CurateImages, ImagesUpload, EventInterestedUsers
# Register your models here.


class EventsAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'user', 'event_location', 'event_city', 'location')
    search_fields = ('event_name', 'user')


admin.site.register(Events, EventsAdmin)
admin.site.register(EventImages)
admin.site.register(CuratedEvents)
admin.site.register(EventComments)
admin.site.register(CurateImages)
admin.site.register(ImagesUpload)
admin.site.register(EventInterestedUsers)