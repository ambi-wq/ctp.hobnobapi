from userprofile.models import UserImages, ProfileDetails, InstagramConnect
from matching.models import UserContacts, UserScore
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
import math
from notifications.models import DeviceRegistry, Notification
from firebase_admin import messaging


def calculate_probability(rating1, rating2):
    """Calculate Probability of User"""
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


def calculate_desirable_score(following, follower, type=1):

    # Define Contact Value
    constant = 32.0

    # Calculate Probability of User following
    probability_follower = calculate_probability(following, follower)

    # Calculatw Probability of Follower User
    probability_following = calculate_probability(follower, following)

    # Evaluate Rating of Follower User based on Probability
    if type == 1:
        following = following + constant * (0 - probability_following)
        follower = follower + constant * (1 - probability_follower)
    else:
        following = following + constant * (1 - probability_following)
        follower = follower + constant * (0 - probability_follower)

    print('Following', following)
    print('Follower', follower)

    # return rating of follower user
    return following, follower


@receiver(post_save, sender=UserContacts)
def update_desirable_score(sender, instance, created, **kwargs):

    # Get following User Score
    following = UserScore.objects.get(user=instance.following)

    # Get follower User Score
    follower = UserScore.objects.get(user=instance.follower)

    # Calculate Desirable Score
    following_updated_score, follower_updated_score = calculate_desirable_score(
        following.desirable_score, follower.desirable_score)

    # Update Score of Follower user
    follower.desirable_score = follower_updated_score

    follower.save()

    print('Follower Score Updated')


@receiver(post_delete, sender=UserContacts)
def deduct_desirable_score(sender, instance, **kwargs):
    try:
        # Get following User Score
        following = UserScore.objects.get(user=instance.following)

        # Get follower User Score
        follower = UserScore.objects.get(user=instance.follower)


        # Calculate Desirable Score
        following_updated_score, follower_updated_score = calculate_desirable_score(
            following.desirable_score, follower.desirable_score, 0)

        # Update Score of Follower user
        follower.desirable_score = follower_updated_score

        follower.save()

        print('Follower Score Updated')
    except UserScore.DoesNotExist as e:
        print("UserScore does not exist")



@receiver(post_save, sender=UserContacts)
def send_notification_of_following(sender, instance, created, **kwargs):
    # Device Registry Array
    registration_tokens = []

    # Get follower User, i.e User who click on button of follow on other user profile
    follower = instance.follower

    # Get User Device List
    follower_device_list = DeviceRegistry.objects.filter(user=follower)

    # Get Register Token
    if follower_device_list.count() > 0:
        registration_tokens = [
            devices.device_token for devices in follower_device_list]

    # Get follower User, i.e User on whoes profile other click to follow
    following = instance.following

    # Get Profile of Follower
    following_profile = ProfileDetails.objects.get(uuid=following)

    body = '''<p style="font-family:'Helvetica'; color:#000"><b>{0}</b> started following you</p>'''.format(following_profile.full_name)

    # Save Notification
    #Prev  Query
    # notification = Notification.objects.create(
    #     notification_user=follower, activity_type='following', activity_user=following, activity_user_name=following_profile.username, message=body)

    #New Query
    notification = Notification.objects.create(
        notification_user=follower, activity_type='user',activity_sub_type='following', activity_user=following,
        activity_user_name=following_profile.full_name, message=body)

    # Build Message
    if follower_device_list.count() > 0:
        title = 'Hobnob'
        body = '{0} started following you'.format(following_profile.full_name)

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={'type': 'UserProfile', 'id': str(following.id)},
            tokens=registration_tokens,
        )
        # print('uuid', follower.id)

        # Send a message to the device corresponding to the provided
        # registration token.
        response = messaging.send_multicast(message)

        print('Notification Sent')
