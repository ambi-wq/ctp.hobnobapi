from .models import UserImages, ProfileDetails, InstagramConnect, UserImages, UserPreference, SpotifyConnect, \
    DisplayPicture, UserContactList, UsersContacts, UserImagesComment
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, pre_save, m2m_changed
from django.dispatch import receiver
from matching.models import UserScore, UserLocation
from notifications.models import DeviceRegistry, Notification
from django.contrib.gis.geos import Point
import ast
import phonenumbers
from firebase_admin import messaging
import firebase_admin
from firebase_admin import credentials


@receiver(pre_save, sender=ProfileDetails)
def calculate_desirable_score(sender, instance, **kwargs):
    """Function used to calculate Desirable Score based on Bio, Work as, Fun Fact, You Enjoy and Interested.
    Whenever their is changes in any of the variable value of users deseriable score will get changed

    Args:
        sender: Sender is signal received attched to model
        instance: model instance with it is attached
    """

    # Get User Profile Data
    profile_data = instance

    # Get Previous Profile Data
    last_data = ProfileDetails.objects.filter(uuid=profile_data.uuid)

    # Read Desirable Score
    score = UserScore.objects.filter(user=profile_data.uuid)

    if last_data.count() > 0:
        last_data = last_data[0]
        print("last_data", last_data, last_data.bio, type(last_data))
        score = score[0]
        print("score", score)
        # Check if Bio is filled or empty based on that add to score
        if len(last_data.bio) == 0 and len(profile_data.bio) > 0:
            score.desirable_score += 100.0
        elif len(last_data.bio) > 0 and len(profile_data.bio) == 0:
            score.desirable_score -= 100.0

        # Check if Work as is filled or empty
        if len(last_data.work_as) == 0 and len(profile_data.work_as) > 0:
            score.desirable_score += 50.0
        elif len(last_data.work_as) > 0 and len(profile_data.work_as) == 0:
            score.desirable_score -= 50.0

        # Check if Fun Fack is filled or empty
        if len(last_data.fun_fact) == 0 and len(profile_data.fun_fact) > 0:
            score.desirable_score += 50.0
        elif len(last_data.fun_fact) > 0 and len(profile_data.fun_fact) == 0:
            score.desirable_score -= 50.0

        # Check if Enjoy is filled or empty
        if len(last_data.enjoy) == 0 and len(profile_data.enjoy) > 0:
            score.desirable_score += 100.0
        elif len(last_data.enjoy) > 0 and len(profile_data.enjoy) == 0:
            score.desirable_score -= 100.0

        # Check if Interest has been add or not
        if last_data.interest.all().count() == 0 and profile_data.interest.all().count() == 5:
            score.desirable_score += 200

        score.save()
        print('User Profile Score Updated')


@receiver(post_save, sender=ProfileDetails)
def create_initiate_profile_score(sender, instance, created, **kwargs):
    """Initiate Score for Profile when first time Profile is created

    Args:
        sender: Sender is signal received attched to model
        instance: model instance with it is attached
        created: Instance is newly created or updated
    """

    # Check if signal is from newly created profile
    if created:
        # Read user id from profile
        user_id = instance.uuid

        # Initiate Profile Default Score
        user_score = UserScore.objects.create(user=user_id)
        print('User Score Initated')

        # Initiate User Preference
        preference = UserPreference.objects.create(
            user=user_id, opposite_gender="Both", min_age=18, max_age=60, radius=50)


@receiver(post_save, sender=InstagramConnect)
def calculate_instagram_desirable_score(sender, instance, created, **kwargs):
    """Function used to calculate Desirable Score based on Instagram Account Connected.
    Whenever their is changes in any of the variable value of users deseriable score will get changed

    Args:
        sender: Sender is signal received attched to model
        instance: model instance with it is attached
        created: Instance is newly created or updated
    """
    # Check is newly created instagram
    if created:
        # Read Desirable Score
        score = UserScore.objects.get(user=instance.user)

        # Add Scroe when connect with instagram
        score.desirable_score += 200.0

        score.save()
        print('User Profile Score Updated')


@receiver(post_save, sender=SpotifyConnect)
def calculate_spotify_desirable_score(sender, instance, created, **kwargs):
    """Function used to calculate Desirable Score based on Instagram Account Connected.
    Whenever their is changes in any of the variable value of users deseriable score will get changed

    Args:
        sender: Sender is signal received attched to model
        instance: model instance with it is attached
        created: Instance is newly created or updated
    """
    # Check is newly created instagram
    if created:
        # Read Desirable Score
        score = UserScore.objects.get(user=instance.user)

        # Add Scroe when connect with instagram
        score.desirable_score += 50

        score.save()
        print('User Profile Score Updated')


@receiver(post_save, sender=DisplayPicture)
def calculate_display_img_desirable_score(sender, instance, created, **kwargs):
    """Function used to calculate Desirable Score based on Number of Image Uploaded.
    Whenever their is changes in any of the variable value of users deseriable score will get changed

    Args:
        sender: Sender is signal received attched to model
        instance: model instance with it is attached
        created: Instance is newly created or updated
    """
    # Check is newly created instagram
    if created:
        # Read Desirable Score
        score = UserScore.objects.get(user=instance.user)

        # Add Scroe when connect with instagram
        score.desirable_score += 50

        score.save()
        print('User Profile Score Updated')


@receiver(post_delete, sender=UserImages)
def deduct_desirable_score(sender, instance, **kwargs):
    try:
        # Read Desirable Score
        score = UserScore.objects.get(user=instance.user)

        # Add Scroe when connect with instagram
        score.desirable_score -= 300 / 6

        score.save()
        print('User Profile Score Updated')
    except UserScore.DoesNotExist as e:
        print("UserScore Does not exist")


@receiver(post_delete, sender=ProfileDetails)
def delete_desirable_score_and_location(sender, instance, **kwargs):
    try:
        # Read Desirable Score
        score = UserScore.objects.get(user=instance.uuid)

        score.delete()

        location = UserLocation.objects.get(user=instance.uuid)

        location.delete()

        print('User Score & Location Deleted')
    except UserScore.DoesNotExist as e:
        print("UserScore does not exist")
    except UserLocation.DoesNotExist as e:
        print("UserLocation does not exist")


@receiver(post_save, sender=ProfileDetails)
def create_location_default(sender, instance, created, **kwargs):
    """Function used to create Location Object When user Profile has been generated.

    Args:
        sender: Sender is signal received attched to model
        instance: model instance with it is attached
        created: Instance is newly created or updated
    """
    # Check is newly created instagram
    if created:
        # Create Default Coordinate of Vashi
        default_coordinated = Point(19.071178, 72.987064)

        # Create Instance of Location Object
        location = UserLocation(
            user=instance.uuid, last_location=default_coordinated, place="Vashi, Navi Mumbai")

        location.save()
        print('User Profile Location Updated')


@receiver(post_save, sender=UserContactList)
def create_user_contacts(sender, instance, created, **kwargs):
    try:
        if created:
            # contactsLst = ast.literal_eval(json.loads(instance.contacts_list, ensure_ascii=False).encode('utf8'))
            contactsLst = instance.contacts_list
            for itr, contacts in enumerate(contactsLst):
                for record in contactsLst[itr]['phone']:
                    if str(record).startswith("+"):
                        UsersContacts.objects.create(user=int(instance.user.id), contact_name=contactsLst[itr]['name'],
                                                     contact_number=phonenumbers.parse(record).national_number)
                    else:
                        UsersContacts.objects.create(user=int(instance.user.id), contact_name=contactsLst[itr]['name'],
                                                     contact_number=record.replace(" ", ""))
    except Exception as e:
        raise ValidationError(detail="error : {}; type : {}".format(str(e), type(e)))


@receiver(m2m_changed, sender=UserImages.liked_user.through)
def user_image_liked_notification(sender, instance, action, **kwargs):
    if action == 'post_add':
        registration_tokens = []
        # Get image data
        image_data = instance
        image_id = image_data.id
        image_owner = image_data.user

        # Get Device token of Image Uploaded
        image_owner_device_token = DeviceRegistry.objects.filter(user=image_owner)

        if image_owner_device_token.count() > 0:
            registration_tokens = [devices.device_token for devices in image_owner_device_token]

            liked_user_set = kwargs['pk_set']

            for liked_user in liked_user_set:
                print(f"{liked_user=} | {image_owner.id=}")
                full_name = ProfileDetails.objects.get(
                    uuid=liked_user).full_name
                user_name = ProfileDetails.objects.get(uuid=liked_user).username
                user_instance = User.objects.get(pk=liked_user)

                if liked_user != image_owner.id:

                    message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> liked your photo</p>'''.format(
                        full_name)

                    # Save Notification data
                    notification = Notification.objects.create(notification_user=image_owner, activity_type='user',
                                                               activity_sub_type='userimage_liked',
                                                               activity_user=user_instance, activity_user_name=full_name,
                                                               message=message_body, user_image_id=image_data)

                    title = "Hobnob"
                    body = '{0} liked your photo'.format(
                        full_name)

                    # comment below 2 line while deploying
                    # cred = credentials.Certificate("credentials/serviceAccountKey.json")
                    # firebase_admin.initialize_app(cred)

                    message = messaging.MulticastMessage(
                        notification=messaging.Notification(
                            title=title,
                            body=body,
                        ),
                        data={'type': 'UserImage', 'id': str(image_id)},
                        tokens=registration_tokens,
                    )

                    response = messaging.send_multicast(message)

                    print('Liked Photo Notification Sent')
        else:
            print('No Device Register')


@receiver(post_save, sender=UserImagesComment)
def imagecomment_notification(sender, instance, created, **kwargs):
    # Initiate register token
    register_token = []

    # Get comment owner user id
    comment_user_id = instance.comment_user

    # Get comment owner full name
    comment_user_full_name = ProfileDetails.objects.get(uuid=comment_user_id).full_name

    image_id = instance.user_image.id

    # Get Image uploaded user id
    image_uploaded_user_id = instance.user_image.user

    # Get Device registry list
    image_uploaded_device_tokens = DeviceRegistry.objects.filter(user=image_uploaded_user_id)

    image_instance = UserImages.objects.get(id=instance.user_image.id)

    message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> commented on your photo</p>'''.format(
        comment_user_full_name)

    if comment_user_id != image_uploaded_user_id:

        notification = Notification.objects.create(notification_user=image_uploaded_user_id, activity_type="user",
                                                   activity_sub_type="userimage_comment",
                                                   activity_user=comment_user_id,
                                                   activity_user_name=comment_user_full_name, message=message_body,
                                                   user_image_id=image_instance)

        # Check Event Host has device tokens
        if image_uploaded_device_tokens.count() > 0:
            # Add Token in Register Token
            register_token = [
                devices.device_token for devices in image_uploaded_device_tokens]

    # comment below 2 line while deploying
    # cred = credentials.Certificate("credentials/serviceAccountKey.json")
    # firebase_admin.initialize_app(cred)


    # Check if Register token is not null
    if len(register_token) > 0 and created:
        # If register token array not null

        # Create title and body for notication
        title = '{0} commented on your photo'.format(comment_user_full_name)
        body = '{0} commented on your photo'.format(comment_user_full_name)

        # Create Instance of Firebase multicast message
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={'type': 'UserImageComment', 'id': str(image_id)},
            tokens=register_token,
        )

        # Dispatch message
        response = messaging.send_multicast(message)

        print('Image Comment Notification Sent')
    else:
        print('No Device Register')


@receiver(m2m_changed,sender=UserImagesComment.liked_user.through)
def user_image_comment_liked_notification(sender,instance,action,**kwargs):
    if action == 'post_add':
        registration_tokens = []
        # Get comment like data
        comment_data = instance
        comment_id = comment_data.comment_id
        comment = comment_data.comment
        image_id = instance.user_image

        # Get image uploaded user
        image_uploaded_user = instance.user_image.user

        # Get device token of Image uploaded
        image_uploaded_device_token = DeviceRegistry.objects.filter(user=image_uploaded_user)

        if image_uploaded_device_token.count() > 0:
            registration_tokens = [devices.device_token for devices in image_uploaded_device_token]

            liked_user_set = kwargs['pk_set']

            for liked_user in liked_user_set:
                full_name = ProfileDetails.objects.get(
                    uuid=liked_user).full_name
                user_name = ProfileDetails.objects.get(uuid=liked_user).username
                user_instance = User.objects.get(pk=liked_user)

                message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> liked your comment : </p><b>{1}</b>'''.format(
                    full_name,comment)

                # Save Notification data
                notification = Notification.objects.create(notification_user=image_uploaded_user, activity_type='user',
                                                           activity_sub_type='userimage_comment_liked',
                                                           activity_user=user_instance, activity_user_name=full_name,
                                                           message=message_body, user_image_id=image_id)

                title = "Hobnob"
                body = '{0} liked your comment : {1}'.format(
                    user_name,comment)

                # comment below 2 line while deploying
                # cred = credentials.Certificate("credentials/serviceAccountKey.json")
                # firebase_admin.initialize_app(cred)

                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data={'type': 'UserImageComment', 'id': str(comment_id)},
                    tokens=registration_tokens,
                )

                response = messaging.send_multicast(message)

                print('Comment Liked Notification Sent')
        else:
            print('No Device Register')


