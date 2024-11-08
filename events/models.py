# from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from userprofile.models import Interest
from PIL import Image
from io import BytesIO
from django.core.files import File


# Create your models here.

class ReportEventsDetails(models.Model):
    user_id = models.IntegerField(help_text="User Id")
    event_id = models.IntegerField(help_text="Event Id")
    report_reason = models.CharField(
        max_length=1000, blank=True, help_text="report reason")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


def compress(image):
    im = Image.open(image)
    # create a BytesIO object
    im_io = BytesIO()
    # save image to BytesIO object
    # im = im.resize([500,500])
    im = im.convert("RGB")
    im = im.save(im_io, 'JPEG', quality=20, optimize=True)
    # create a django-friendly Files object
    new_image = File(im_io, name=image.name)
    return new_image


class Events(models.Model):
    TYPES = [('Private', 'Private'), ('Public', 'Public'),
             ('Close Friends', 'Close Friends')]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="event_creator")
    event_id = models.BigAutoField(primary_key=True, unique=True)
    event_name = models.CharField(max_length=240, help_text="Name of Events")
    event_type = models.CharField(
        max_length=50, choices=TYPES, help_text="Type of Events")
    description = models.TextField(help_text="Description of Events")
    event_city = models.CharField(max_length=100, null=True, blank=True, help_text="City of Events")
    location = models.CharField(
        max_length=240, help_text="Location of Events, Inclues City and Country Code")
    event_location = models.PointField(null=True, blank=True)
    event_address = models.TextField(
        help_text="Event Address", blank=True, null=True)
    event_date = models.DateField()
    event_time_from = models.TimeField(null=True, blank=True)
    event_time_to = models.TimeField(null=True, blank=True)
    event_price = models.FloatField(
        null=True, blank=True, help_text="Creator Can add Price of Events")
    event_interest = models.ManyToManyField(
        Interest, related_name="event_interest", null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    interested_users = models.ManyToManyField(
        User, related_name="interested_user", blank=True, null=True)
    invited_users = models.ManyToManyField(
        User, related_name="invited_users", blank=True, null=True)
    event_end_date = models.DateField(blank=True, null=True)

    #  Added Going and Yet to decide options
    going_users = models.ManyToManyField(User, related_name="going_users", blank=True, null=True)
    yet_to_decide_users = models.ManyToManyField(User, related_name="yet_to_decide_users", blank=True, null=True)

    def __str__(self):
        return str(self.event_name)


class EventImages(models.Model):
    IMG_TYPE = [('cover', 'cover'), ('event', 'event')]

    event = models.ForeignKey(
        Events, on_delete=models.CASCADE, related_name="images")

    image_type = models.CharField(
        max_length=50, choices=IMG_TYPE, help_text="Type of Image", default='event')
    event_img = models.ImageField(upload_to='event_images/')

    def __str__(self):
        return str(self.event.event_name)

    def save(self, *args, **kwargs):
        print("before saving", self.event_img)
        if self.event_img:
            print("self.event_img", self.event_img)
            if self.event_img.size > 1000000:
                # call the compress function
                new_image = compress(self.event_img)
                # set self.image to new_image
                self.event_img = new_image
                # save
        super().save(*args, **kwargs)


class ImagesUpload(models.Model):
    IMG_TYPE = [('cover', 'cover'), ('event', 'event')]

    image_type = models.CharField(
        max_length=50, choices=IMG_TYPE, help_text="Type of Image", default='event')
    event_img = models.ImageField(upload_to='event_images/')

    def __str__(self):
        return str(self.event_img)

    def save(self, *args, **kwargs):
        if self.event_img:
            if self.event_img.size > 1000000:
                # call the compress function
                new_image = compress(self.event_img)
                # set self.image to new_image
                self.event_img = new_image
                # save
        super().save(*args, **kwargs)


class CuratedEvents(models.Model):
    event_name = models.CharField(max_length=240, help_text="Name of Events")
    description = models.TextField(
        help_text="Description of Events", blank=True, null=True)
    categoery = models.ManyToManyField(
        Interest, related_name="categoery", blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.event_name)


class CurateImages(models.Model):
    curated_event = models.ForeignKey(
        CuratedEvents, on_delete=models.CASCADE, related_name="currated_images")
    image = models.ImageField(upload_to='currated_images/')

    def __str__(self):
        return str(self.curated_event)


class EventComments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        Events, related_name='event_comments', on_delete=models.CASCADE)
    comment_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comment_user')
    comment = models.TextField()
    reply = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['create_at']

    def __str__(self):
        return "Comment by {}".format(self.comment_user)


class EventInterestedUsers(models.Model):
    event = models.ForeignKey(
        Events, on_delete=models.CASCADE)
    interested_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="event_interested_user")
    hosted_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="event_hosted_user")
    user_accepted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.event)
