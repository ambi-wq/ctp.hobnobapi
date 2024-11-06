# from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from firebase_admin import auth
import firebase_admin
from firebase_admin import credentials
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime, date
from PIL import Image
from io import BytesIO
from django.core.files import File
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill,Adjust,ResizeToFit

def date_validation(birthdate):
    today_date = datetime.now().date()
    age_yr = int((today_date - birthdate).days/365)
    if age_yr < 18:
        raise ValidationError(message="Age should be 18 or plus")


def compress(image):
    im = Image.open(image)
    # create a BytesIO object
    im_io = BytesIO()
    # save image to BytesIO object
    #im = im.resize([500,500])
    im = im.convert("RGB")
    im = im.save(im_io, 'JPEG', quality=20, optimize=True)
    # create a django-friendly Files object
    new_image = File(im_io, name=image.name)
    return new_image

class UsersContacts(models.Model):
    # user = models.ForeignKey(
        # User, on_delete=models.CASCADE, related_name="user_id")
    user = models.IntegerField(help_text="User Id")
    contact_name = models.CharField(
        max_length=50, blank=True, null=True, help_text="contact_name")
    contact_number = models.CharField(
        max_length=25, blank=True, null=True, help_text="contact_number")
    last_sync = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.contact_name

class UserContactList(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="User")
    contacts_list = models.TextField(blank=True, help_text="Description of User")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.user)

class Interest(models.Model):
    """This store widelist of interest user can associate with. 
    """
    interest_id = models.AutoField(primary_key=True)
    images = models.ImageField(upload_to='categories/')
    interest_name = models.CharField(
        max_length=50, blank=True, unique=True, help_text="Name of Interest")

    def __str__(self):
        return self.interest_name

    def save(self, *args, **kwargs):
        if self.images:
            if self.images.size > 1000000:
                # call the compress function
                new_image = compress(self.images)
                # set self.image to new_image
                self.images = new_image
                # save
        super().save(*args, **kwargs)

class UserImages(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_profile_image")
    images = models.ImageField(upload_to='user_images/')
    # image_thumbnail = ImageSpecField(source='images',
    #   processors=[ResizeToFill(100,100)],
    #   format='PNG',
    #   options={'quality': 60})
    image_thumbnail = ImageSpecField(source='images',
                                     processors=[Adjust(contrast=1.2, sharpness=1.1),ResizeToFill(200, 200)],
                                     format='PNG',
                                     options={'quality': 90})
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    liked_user = models.ManyToManyField(User,related_name='liked_user',blank=True,null=True)
    height = models.CharField(max_length=50,blank=True,null=True)
    width = models.CharField(max_length=50,blank=True,null=True)


    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.images:
            if self.images.size > 1000000:
                # call the compress function
                new_image = compress(self.images)
                # set self.image to new_image
                self.images = new_image
                # save
        super().save(*args, **kwargs)


class DisplayPicture(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="display_pic")
    images = models.ImageField(upload_to='display_pic/')
    image_thumbnail = ImageSpecField(source="images",
                                     processors=[ResizeToFill(100, 100)],
                                     format='PNG',
                                     options={'quality': 60})

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if self.images:
            if self.images.size > 1000000:
                # call the compress function
                new_image = compress(self.images)
                # set self.image to new_image
                self.images = new_image
                # save
        super().save(*args, **kwargs)


class ProfileDetails(models.Model):
    """Store Profile Details when user Signup with 
    """

    GENDER = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    uuid = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile")
    username = models.CharField(max_length=100, unique=True, null=True,
                                blank=True, help_text="Username associate with Profile")
    gender = models.CharField(max_length=10, choices=GENDER,
                              null=False, blank=False, help_text='Gender of User')
    dob = models.DateField(validators=[date_validation])
    full_name = models.CharField(
        max_length=40, blank=False, null=False, help_text='Full name of User')
    interest = models.ManyToManyField(
        'Interest', related_name='interest', blank=True, null=True)
    home_town = models.CharField(
        max_length=100, blank=True, help_text="Home Town")
    work_as = models.CharField(
        max_length=100, blank=True, help_text="Designation at Work Place")
    company = models.CharField(
        max_length=100, blank=True, help_text="Company")
    education = models.CharField(
        max_length=100, blank=True, help_text="education")
    city = models.CharField(
        max_length=100, blank=True, help_text="lives at")
    bio = models.TextField(blank=True, help_text="Description of User")
    fun_fact = models.TextField(blank=True, help_text="Fun Fact of User")
    enjoy = models.TextField(
        blank=True, help_text="Description of things user enjoy doing")

    phone = models.CharField(
        max_length=15, blank=True, help_text="True")

    is_available = models.BooleanField(default=True)
    spotify_connected = models.BooleanField(default=False)
    recorvery_mail = models.TextField(max_length=100, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.full_name)

    @property
    def contact_details(self):
        """This return contact details of user

        Returns:
            contact: If user signed in with Phone then it will return Phone,
            otherwise it will return email id 
        """
        # cred = credentials.Certificate("credentials/serviceAccountKey.json")
        # firebase_admin.initialize_app(cred)
        uid = self.uuid.username
        firebase_user = auth.get_user(uid)
        if firebase_user.phone_number:
            return firebase_user.phone_number
        else:
            return firebase_user.email

    @property
    def user_age(self):
        today_date = datetime.now().date()
        age_yr = int((today_date - self.dob).days/365)
        return age_yr

    @property
    def profile_photo(self):
        user = self.uuid
        profile_img = UserImages.objects.filter(user=user)
        if len(profile_img) > 0:
            return profile_img[0].images.url
        else:
            return ""


class UserPreference(models.Model):
    GENDER = [('Male', 'Male'), ('Female', 'Female'), ('Both', 'Both')]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preference")
    opposite_gender = models.CharField(max_length=6, choices=GENDER, blank=True, null=True,
                                       help_text="User interested in Opposite Gender. **It is removed that why it's made optional")
    min_age = models.IntegerField(default=18, blank=False, validators=[MaxValueValidator(
        100), MinValueValidator(18)], help_text="Minimum Age group user want to meet")
    max_age = models.IntegerField(default=19, blank=False, validators=[MaxValueValidator(
        100), MinValueValidator(19)], help_text="Maximum Age group user want to meet")
    radius = models.FloatField(default=10.0, validators=[MaxValueValidator(
        161), MinValueValidator(2)], help_text="In maximum radius, user want to meet in KMs")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.max_age > self.min_age:
            super().save(*args, **kwargs)
        else:
            raise ValidationError(
                message="Max Age should be greater than Min Age")

    def __str__(self):
        return str(self.user)


class InstagramConnect(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="instagram")
    instagram_id = models.CharField(
        max_length=50, help_text="Instagram ID of User")
    access_token = models.TextField(help_text="Long Lived Accesse token")
    token_expiry = models.CharField(
        max_length=40, help_text="Last Date of Expiry")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class SpotifyConnect(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="spotify")
    refresh_token = models.TextField(
        help_text="Refresh Token to Get New Access Token")
    access_token = models.TextField(
        help_text="Use Access Token if generated before One hours")
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class PromptQuestions(models.Model):
    question = models.CharField(max_length=255, help_text="Sample Questions")

    def __str__(self):
        return self.question


class UserPromptQA(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_prompt")
    question = models.ForeignKey(
        PromptQuestions, on_delete=models.CASCADE, related_name="prompt_questions")
    answer = models.TextField(blank=True, null=True,
                              help_text="Answer to question")

    def __str__(self):
        return self.user.user_profile.full_name


class UserImagesComment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user_image = models.ForeignKey(UserImages,related_name='userimages_comment',on_delete=models.CASCADE)
    comment_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='userimages_comment_user')
    comment = models.TextField()
    # reply = models.ForeignKey('self',null=True,on_delete=models.CASCADE,related_name='userimages_replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    liked_user = models.ManyToManyField(User,related_name='liked_user_comment',blank=True,null=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return "Comment by {}".format(self.comment_user)