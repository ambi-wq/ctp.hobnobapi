# from django.db import models
from django.contrib.gis.db import models
from userprofile.models import ProfileDetails
from django.contrib.auth.models import User

# Create your models here.
class UserContacts(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_following')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_follower')
    hosted_events = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_hosted_events', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.following)


class UserScore(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="score")
    desirable_score = models.FloatField(default=0.0, blank=False, help_text="Desirable Score based on Profile and Network")
    events_score = models.FloatField(default=0.0, blank=False, help_text="Events Score use to decide attaction of user toward events created by user")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-desirable_score']

    def __str__(self):
        return str(self.user)


class UserLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="geo_location")
    last_location = models.PointField()
    place = models.TextField(help_text="Name of Place of last location", blank=True, null=True)
    unit = models.CharField(max_length=10, default="km", help_text="Unit of Distance")

    def __str__(self):
        return str(self.user)


class CloseFriendList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friends_list")
    close_friend = models.ForeignKey(User, related_name='close_friend', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.close_friend)


class SuggesstedUser(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user")
    suggessted_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="suggessted_user")

    def __str__(self):
        return str(self.user)