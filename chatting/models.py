from django.contrib.auth import get_user_model
from django.db import models
from userprofile.models import ProfileDetails

User = get_user_model()


# class Contact(models.Model):
#     # user = models.ForeignKey(
#     #     User, related_name='contacts', on_delete=models.CASCADE)
#     user = models.OneToOneField(User, related_name='contacts', on_delete=models.CASCADE)
#     friends = models.ManyToManyField('self', blank=True)

#     def __str__(self):
#         return self.user.username


class Message(models.Model):
    contact = models.ForeignKey(
        User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.content)


class Room(models.Model):
    participants = models.ManyToManyField(
        User, related_name='rooms')
    messages = models.ManyToManyField(Message)

    def __str__(self):
        return str(self.id)
