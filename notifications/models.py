from django.db import models
from django.contrib.auth import get_user_model
from events.models import Events, EventComments
from userprofile.models import UserImages

User = get_user_model()
# Create your models here.


class DeviceRegistry(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="device_registry")
    device_token = models.TextField(
        help_text="Unique token Generate Per device by Firebase FCM")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user.user_profile.full_name)


class Notification(models.Model):
    """
    - notification_user
        - activity_type
        - activity_name (event_name)
        - activity_id (event_id)
        - activity_user_id (comment_user_id, interested_user_id, follower_user_id)
        - activity_user_name (comment_user_name, interested_user_name, follower_user_name)
        - date-time
    """
    # Previous Query
    # TYPES = [('comment', 'comment'), ('following',  'following'), ('event', 'event')]
    #New Query
    TYPES = [('comment', 'comment'), ('following', 'following'), ('event', 'event'),('event_interested','event_interested'),('event_created','event_created')]
    ACTIVITY_TYPES = [('event','event'),('user','user')]
    SUB_TYPES = [('event_interested','event_interested'),('event_created','event_created'),('event_comment','event_comment'),('following','following'),('message','message'),('event_going','event_going'),('event_yettodecide','event_yettodecide'),('userimage_liked','userimage_liked'),('userimage_comment','userimage_comment'),('userimage_comment_liked','userimage_comment_liked')]
    notification_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification")
    activity_type = models.CharField(
        max_length=20, choices=ACTIVITY_TYPES, help_text="Notification Type")
    activity_sub_type = models.CharField(max_length=25,choices=SUB_TYPES,help_text="notification sub type")
    activity_name = models.CharField(
        max_length=250, blank=True, null=True, help_text="Activity Name use to Store Events Name")
    activity_id = models.ForeignKey(
        Events, on_delete=models.CASCADE, blank=True, null=True)
    activity_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="activity_user")
    activity_user_name = models.CharField(
        max_length=250, blank=True, null=True, help_text="User name who perform activity")
    message = models.CharField(
        max_length=250, blank=True, null=True, help_text="Text Message")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    flag = models.BooleanField(default=False)
    user_image_id = models.ForeignKey(UserImages,on_delete=models.CASCADE,blank=True,null=True)

    def __str__(self):
        return str(self.notification_user.user_profile.full_name)
