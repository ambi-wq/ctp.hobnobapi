from events.models import Events, EventComments
from matching.models import UserScore, UserContacts
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import receiver
import math
from userprofile.models import ProfileDetails
from notifications.models import DeviceRegistry, Notification
from firebase_admin import messaging
from django.contrib.auth import get_user_model

import firebase_admin
from firebase_admin import credentials

User = get_user_model()


def calculate_probability(rating1, rating2):
    """Calculate Probability of User"""
    return 1.0 * 1.0 / (1 + 1.0 * math.pow(10, 1.0 * (rating1 - rating2) / 400))


def calculate_events_score(following, follower, type=1):

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


@receiver(m2m_changed, sender=Events.interested_users.through)
def event_interest_notification(sender, instance, action, **kwargs):
    """Function used to calculate Events Interesting Score based on type of people show interest.

    Args:
        sender: Sender is signal received attched to model
        instance: model instance with it is attached
    """
    if action == 'post_add':
        # Device Registry Array
        registration_tokens = []

        # Get Events Data
        event_data = instance

        # Get Event Name
        event_name = event_data.event_name

        # Get Event id
        event_id = event_data.event_id

        # Get Creator User
        event_host = event_data.user

        # Get Device token of Event Host
        event_host_device_token = DeviceRegistry.objects.filter(
            user=event_host)

        if event_host_device_token.count() > 0:
            registration_tokens = [
                devices.device_token for devices in event_host_device_token]

            interested_user_set = kwargs['pk_set']

            for interest_user in interested_user_set:
                full_name = ProfileDetails.objects.get(
                    uuid=interest_user).full_name
                user_name2 = ProfileDetails.objects.get(
                    uuid=interest_user).username

                user_instance = User.objects.get(pk=interest_user)

                #Previous value
                # message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> is interested in your Event</p>'''.format(
                #     user_name2, event_name)

                #New value
                message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> is interested in the event: {1}</p>'''.format(
                    full_name, event_name)

                # Save Notification data
                #Previous Query
                # notification = Notification.objects.create(notification_user=event_host, activity_type='event', activity_name=event_name,
                #                                            activity_id=event_data, activity_user=user_instance, activity_user_name=user_name2, message = message_body)

                # notification = Notification.objects.create(notification_user=event_host,
                #                                            activity_type='event_interested',
                #                                            activity_name=event_name,
                #                                            activity_id=event_data, activity_user=user_instance,
                #                                            activity_user_name=user_name2, message=message_body)
                #New Query
                notification = Notification.objects.create(notification_user=event_host, activity_type='event',activity_sub_type='event_interested',
                                                           activity_name=event_name,
                                                           activity_id=event_data, activity_user=user_instance,
                                                           activity_user_name=full_name, message=message_body)

                #                title = '{0} shows interest in your event'.format(event_name)
                title = "Hobnob"
                body = '{0} is interested in your Event'.format(
                    full_name)

                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data={'type': 'EventDetail', 'id': str(event_id)},
                    tokens=registration_tokens,
                )

                response = messaging.send_multicast(message)

                print('Event Interest Notification Sent')
        else:
            print('No Device Register')


@receiver(post_save, sender=EventComments)
def commnet_notification(sender, instance, created, **kwargs):
    # Initate Register Token
    register_token = []

    # Get Comment Owner User ID
    comment_user_id = instance.comment_user

    # Get Comment Owner Full Name
    comment_user_full_name = ProfileDetails.objects.get(
        uuid=comment_user_id).full_name

    # Get Comment Reply Object
    try:
        reply_comment_id = instance.reply.comment_id
    except:
        reply_comment_id = None

    # Get Event Name
    event_name = instance.event.event_name

    # Get Event ID
    event_id = instance.event.event_id

    # Get Event Host User ID
    event_host_user_id = instance.event.user

    # Get Device Registry List
    event_host_device_tokens = DeviceRegistry.objects.filter(
        user=event_host_user_id)

    # Get Event
    event_instace = Events.objects.get(event_id=instance.event.event_id)

    # Save Notification

    #Previous Value
    # message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> commented on <b>{1}</b> Event</p>'''.format(
    #     comment_user_full_name, event_name)

    #New Value
    message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> commented on your event: {1}</p>'''.format(
        comment_user_full_name, event_name)

    if comment_user_id != event_host_user_id:
        #Prev Query
        # notification = Notification.objects.create(notification_user=event_host_user_id, activity_type="comment", activity_name=event_name,
        #                                            activity_id=event_instace, activity_user=comment_user_id, activity_user_name=comment_user_full_name, message=message_body)

        #New Query
        notification = Notification.objects.create(notification_user=event_host_user_id,activity_type="event" ,activity_sub_type="event_comment",
                                                   activity_name=event_name,
                                                   activity_id=event_instace, activity_user=comment_user_id,
                                                   activity_user_name=comment_user_full_name, message=message_body)

        # Check Event Host has device tokens
        if event_host_device_tokens.count() > 0:
            # Add Token in Register Token
            register_token = [
                devices.device_token for devices in event_host_device_tokens]

    # Check if reply is null
    if reply_comment_id:
        # If reply is not null get get comment instance
        reply_comment = EventComments.objects.get(comment_id=reply_comment_id)

        # Get Comment Owner ID
        reply_comment_owner = reply_comment.comment_user

        # Get Device List of Comment Owner
        reply_comment_device_token = DeviceRegistry.objects.filter(
            user=reply_comment_owner)

        # Check if device token exist
        if reply_comment_device_token.count() > 0 and comment_user_id != reply_comment_owner:
            # Append in Register token Array
            for devices in reply_comment_device_token:
                register_token.append(devices.device_token)

    # Check if Register token is not null
    if len(register_token) > 0 and created:
        # If register token array not null

        # Create title and body for notication
        title = '{0} commented on {1} Event'.format(comment_user_full_name, event_name)
        body = '{0} commented on {1} Event'.format(
            comment_user_full_name, event_name)

        # Create Instance of Firebase multicast message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={'type': 'EventDetail', 'id': str(event_id)},
            tokens=register_token,
        )

        # Dispatch message
        response = messaging.send_multicast(message)

        print('Event Interest Notification Sent')
    else:
        print('No Device Register')


@receiver(post_save, sender=Events)
def events_creation_notification(sender, instance, created, **kwargs):

    # Register Token
    register_token = []

    # Get Event Creator User
    event_host = instance.user

    # Get Event Name
    event_name = instance.event_name

    # Get Event Id
    event_id = instance.event_id

    try:
        # Host Full Name
        host_name = event_host.user_profile.full_name
        user_name = event_host.user_profile.username
        # Get Follower List
        follower_list = UserContacts.objects.values_list(
            'following', flat=True).filter(follower=event_host)
        # print(event_host)
        # print("follower_list", follower_list)
        # print([fl for fl in follower_list],"=====follower")

        # Previous Query
        # # Get Following List with filter those user return following
        # following_list = UserContacts.objects.values_list('follower').filter(
        #     following=event_host, follower__in=follower_list)

        # New Query
        # Get Following List with filter those user return following
        following_list = UserContacts.objects.values_list('follower').filter(
            following=event_host, follower__in=follower_list).exclude(follower=event_host)

        # print([fl for fl in following_list],"=====following")

        # Get List of Register Token
        event_host_device_tokens = DeviceRegistry.objects.filter(
            user__in=following_list)

        print([d for d in event_host_device_tokens])
        register_token = [
            devices.device_token for devices in event_host_device_tokens]

        print("device regisered", event_host, event_id, host_name, event_name)

        message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> has created event <b>{1}</b></p>'''.format(
            host_name, event_name)

        # Uncomment if notifications to be appered for event Creation.

        #Previous Query
        # for followers in following_list:
        #     notification = Notification.objects.create(notification_user=User.objects.get(id=followers[0]), activity_type="event", activity_name=event_name,
        #                                             activity_id=Events.objects.get(event_id = event_id), activity_user=event_host, activity_user_name=host_name, message=message_body)

        # # New Query
        # for followers in following_list:
        #     # notification = Notification.objects.create(notification_user=User.objects.get(id=followers[0]), activity_type="event_created", activity_name=event_name,
        #     #                                         activity_id=Events.objects.get(event_id = event_id), activity_user=event_host, activity_user_name=host_name, message=message_body)
        #     notification = Notification.objects.create(notification_user=User.objects.get(id=followers[0]),
        #                                                activity_type = "event",
        #                                                activity_sub_type="event_created", activity_name=event_name,
        #                                                activity_id=Events.objects.get(event_id=event_id),
        #                                                activity_user=event_host, activity_user_name=host_name,
        #                                                message=message_body)

        # Check if Register token is not null and event is newly created
        if len(register_token) > 0 and created:
            # New Query
            for followers in following_list:
                # notification = Notification.objects.create(notification_user=User.objects.get(id=followers[0]), activity_type="event_created", activity_name=event_name,
                #                                         activity_id=Events.objects.get(event_id = event_id), activity_user=event_host, activity_user_name=host_name, message=message_body)
                notification = Notification.objects.create(notification_user=User.objects.get(id=followers[0]),
                                                           activity_type="event",
                                                           activity_sub_type="event_created", activity_name=event_name,
                                                           activity_id=Events.objects.get(event_id=event_id),
                                                           activity_user=event_host, activity_user_name=host_name,
                                                           message=message_body)

            # If register token array not null

            # Create title and body for notication
            title = '{}'.format(user_name)
            body = '{0} has created an event'.format(
                host_name, event_name)

            # Create Instance of Firebase multicast message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data={'type': 'EventDetail', 'id': str(event_id)},
                tokens=register_token,
            )

            # Dispatch message
            response = messaging.send_multicast(message)

            print('Event Creation Notification Sent')
        else:
            print('No Device Register')
    except:
        print('Something went wrong')


@receiver(m2m_changed,sender=Events.going_users.through)
def event_going_notification(sender,instance,action,**kwargs):
    if action == 'post_add':
        # Device Registry Array
        registration_tokens = []

        #Get Events Data
        event_data = instance

        event_name = event_data.event_name
        event_id = event_data.event_id
        event_host = event_data.user

        # Get device token of Event Host
        event_host_device_token = DeviceRegistry.objects.filter(user=event_host)

        if event_host_device_token.count() > 0:
            registration_tokens = [devices.device_token for devices in event_host_device_token]
            going_user_set = kwargs['pk_set']

            for going_user in going_user_set:
                full_name = ProfileDetails.objects.get(
                    uuid=going_user).full_name
                user_name = ProfileDetails.objects.get(uuid=going_user).username
                user_instance = User.objects.get(pk=going_user)

                message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> is going in the event: {1}</p>'''.format(
                    full_name, event_name)

                notification = Notification.objects.create(notification_user=event_host, activity_type='event',
                                                           activity_sub_type='event_going',
                                                           activity_name=event_name,
                                                           activity_id=event_data, activity_user=user_instance,
                                                           activity_user_name=full_name, message=message_body)

                #                title = '{0} shows interest in your event'.format(event_name)
                title = "Hobnob"
                body = '{0} is going in your Event'.format(
                    full_name)

                # comment below 2 line while deploying
                cred = credentials.Certificate("credentials/serviceAccountKey.json")
                firebase_admin.initialize_app(cred)

                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data={'type': 'EventDetail', 'id': str(event_id)},
                    tokens=registration_tokens,
                )

                response = messaging.send_multicast(message)

                print('Event Going Notification Sent')
        else:
            print('No Device Register')


@receiver(m2m_changed,sender=Events.yet_to_decide_users.through)
def event_yet_to_decide_notification(sender,instance,action,**kwargs):
    if action == 'post_add':
        # Device registry array
        registration_tokens = []

        # Get event data
        event_data = instance

        event_name = event_data.event_name
        event_id = event_data.event_id
        event_host = event_data.user

        # Get device token of event host
        event_host_device_token = DeviceRegistry.objects.filter(user=event_host)

        if event_host_device_token.count() > 0:
            registration_tokens = [devices.device_token for devices in event_host_device_token]
            yet_to_decide_user_set = kwargs['pk_set']

            for yet_to_decide_user in yet_to_decide_user_set:
                full_name = ProfileDetails.objects.get(
                    uuid=yet_to_decide_user).full_name
                user_name = ProfileDetails.objects.get(uuid=yet_to_decide_user).username
                user_instance = User.objects.get(pk=yet_to_decide_user)

                message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> is yet to decide in the event: {1}</p>'''.format(
                    full_name, event_name)

                notification = Notification.objects.create(notification_user=event_host, activity_type='event',
                                                           activity_sub_type='event_yettodecide',
                                                           activity_name=event_name,
                                                           activity_id=event_data, activity_user=user_instance,
                                                           activity_user_name=full_name, message=message_body)

                #                title = '{0} shows interest in your event'.format(event_name)
                title = "Hobnob"
                body = '{0} is yet to decide in your Event'.format(
                    full_name)

                # comment below 2 line while deploying
                # cred = credentials.Certificate("credentials/serviceAccountKey.json")
                # firebase_admin.initialize_app(cred)

                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data={'type': 'EventDetail', 'id': str(event_id)},
                    tokens=registration_tokens,
                )

                response = messaging.send_multicast(message)

                print('Event Yet To Decide Notification Sent')
        else:
            print('No Device Register')
