from rest_framework import serializers
from .models import EventImages, Events, CuratedEvents, EventComments, CurateImages, ImagesUpload
from drf_extra_fields.geo_fields import PointField
from userprofile.models import UserImages, ProfileDetails
from userprofile.serializers import UserImageSerializer, ProfileDetailsSerializer, DisplayPictureSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class EventSerializer(serializers.ModelSerializer):
    event_location = PointField()

    class Meta:
        model = Events
        exclude = ['user']
        extra_kwargs = {'interested_users': {'required': False}}


class EventImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventImages
        fields = '__all__'


class ImagesUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImagesUpload
        fields = '__all__'


class EventListSerializer(serializers.ModelSerializer):
    event_img = serializers.SerializerMethodField('get_event_img')

    user_images = serializers.SerializerMethodField('get_event_creator_image')

    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img')
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag')
    is_creator = serializers.SerializerMethodField('get_creator_flag')

    # creator = serializers.SerializerMethodField('get_creator')

    class Meta:
        model = Events
        fields = ['event_id', 'event_name', 'event_address', 'description', 'is_user_interested', 'is_creator', 'event_price', 'event_type', 'location', 'event_date', 'event_time_from',
                  'event_time_to', 'event_interest', 'interested_users', 'interested_user_img', 'invited_users', 'event_img', 'event_location', 'user_images', 'creator']

        read_only_fields = fields

    def get_event_img(self, event):
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            event_imgs = qs[event.event_id].images
            event_img_serializers = EventImageSerializer(event_imgs, many=True)
            event_img = event_img_serializers.data
            return event_img

    def get_creator(self, event):
        qs = self.context.get("qs")
        creator_name = ""
        if qs[event.event_id] == event:
            creator_name = qs[event.event_id].user.user_profile.full_name
            return creator_name
        else:
            return creator_name

    def get_event_creator_image(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        user_img = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            try:
                user_img = qs[event.event_id].user.display_pic.images.url
                return user_img
            except ObjectDoesNotExist:
                return user_img

    def get_interested_flag(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id in qs[event.event_id].interested_users.all():
                return True
            else:
                return False

    def get_creator_flag(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id == qs[event.event_id].user:
                return True
            else:
                return False

    def get_interested_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        interested_user_list = qs[event.event_id].interested_users.all()[:3]

        if len(interested_user_list) > 0:
            # Create Instance of User
            for int_user in interested_user_list:
                try:
                    images_array.append(int_user.display_pic.images.url)
                except ObjectDoesNotExist:
                    continue
                    print("{} user dp doesn't exist".format(int_user))

            # Return Data
            return images_array
        else:
            # Return Data
            return images_array


class EventDetailsListSerializer(serializers.ModelSerializer):
    event_img = serializers.SerializerMethodField('get_event_img')
    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img')
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag')
    is_creator = serializers.SerializerMethodField('get_creator_flag')
    user_images = serializers.SerializerMethodField('get_event_creator_image')
    creator = serializers.SerializerMethodField('get_creator')

    class Meta:
        model = Events
        fields = ['event_id', 'event_name', 'event_address', 'creator', 'description', 'user_images', 'is_user_interested', 'is_creator', 'event_price', 'event_type', 'location', 'event_date', 'event_time_from',
                  'event_time_to', 'event_interest', 'interested_users', 'interested_user_img', 'invited_users', 'event_img', 'event_location']

    def get_event_img(self, event):

        event_img = []
        if EventImages.objects.filter(event=event).exists():
            event_imgs = EventImages.objects.filter(event=event)
            event_img_serializers = EventImageSerializer(event_imgs, many=True)
            event_img = event_img_serializers.data

        return event_img

    def get_creator(self, event):
        creator_name = ""
        try:
            creator_name = event.user.user_profile.full_name
            return creator_name
        except:
            return creator_name

    def get_interested_flag(self, event):
        # Get Requested User ID
        requested_user_id = self.context.get("user")
        if requested_user_id in event.interested_users.all():
            return True
        else:
            return False

    def get_event_creator_image(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        user_img = ""

        try:
            user_img = event.user.display_pic.images.url
            return user_img
        except ObjectDoesNotExist:
            return user_img

    def get_creator_flag(self, event):
        # Get Requested User ID
        requested_user_id = self.context.get("user")
        if requested_user_id == event.user:
            return True
        else:
            return False

    def get_interested_user_img(self, event):
        images_array = []
        # Get Interested User List
        interested_user_list = event.interested_users.all()[:3]

        if len(interested_user_list) > 0:
            # Create Instance of User
            for int_user in interested_user_list:
                try:
                    images_array.append(int_user.display_pic.images.url)
                except ObjectDoesNotExist:
                    continue
                    print("{} user dp doesn't exist".format(int_user))

            # Return Data
            return images_array
        else:
            # Return Data
            return images_array


class CuratedImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = CurateImages
        fields = '__all__'


class CuratedEventsSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField('get_images')

    class Meta:
        model = CuratedEvents
        fields = ['id', 'event_name', 'description',
                  'create_at', 'categoery', 'images']

    def get_images(self, event):
        qs = self.context.get("qs")
        event_img = []

        if qs[event.id] == event:
            event_imgs = qs[event.id].currated_images
            event_img_serializers = CuratedImagesSerializer(
                event_imgs, many=True)
            event_img = event_img_serializers.data
            return event_img
        # # Get Event id
        # event_id = event.id

        # # Make Query to get all images
        # events_img = CurateImages.objects.filter(curated_event=event_id)

        # # Serializer Data
        # events_serializer = CuratedImagesSerializer(events_img, many=True)

        # # Return Data
        # return events_serializer.data


class EventCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventComments
        exclude = ['comment_user']


class CommentListSerializer(serializers.ModelSerializer):

    profile_img = serializers.SerializerMethodField('get_profile_img')
    full_name = serializers.SerializerMethodField('get_username')
    is_creator = serializers.SerializerMethodField('get_creator')
    total_replies = serializers.SerializerMethodField('get_total_replies')

    class Meta:
        model = EventComments
        fields = ['comment_id', 'is_creator', 'profile_img', 'full_name', 'total_replies',
                  'event', 'comment_user', 'comment', 'reply', 'create_at', 'update_at']

        read_only_fields = fields

    def get_profile_img(self, comment):
        # Get User
        comment_id = comment.comment_id

        # Get Profile Image Instance
        try:
            qs = self.context.get("queryset")
            user_image = qs[comment_id].comment_user.display_pic
            user_img_serializer = DisplayPictureSerializer(user_image)
            return [user_img_serializer.data]
        except:
            return []

    def get_username(self, comment):
        # Get User
        comment_id = comment.comment_id
        qs = self.context.get("queryset")
        return qs[comment_id].comment_user.user_profile.full_name

    def get_creator(self, comment):
        # Get User
        user = comment.comment_user
        current_user = self.context.get("current_user")
        if user == current_user:
            return True
        else:
            return False

    def get_total_replies(self, comment):
        # Get User
        comment_id = comment.comment_id
        qs = self.context.get("queryset")
        total_replies = qs[comment_id].replies.count()

        return total_replies


class EventInvitationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Events
        fields = ['event_id', 'event_name', 'invited_users']


class PrivateEventSerializer(serializers.ModelSerializer):
    event_img = serializers.SerializerMethodField('get_event_img')
    user_images = serializers.SerializerMethodField('get_event_creator_image')
    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img')
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag')
    is_creator = serializers.SerializerMethodField('get_creator_flag')
    creator = serializers.SerializerMethodField('get_creator')

    class Meta:
        model = Events
        fields = ['event_id', 'event_name', 'event_address', 'description', 'user_images', 'creator', 'event_img', 'is_user_interested', 'is_creator', 'event_price', 'event_type', 'location', 'event_date', 'event_time_from',
                  'event_time_to', 'event_interest', 'interested_users', 'interested_user_img', 'invited_users', 'event_location']

        read_only_fields = fields

    def get_event_img(self, event):
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            event_imgs = qs[event.event_id].images
            event_img_serializers = EventImageSerializer(event_imgs, many=True)
            event_img = event_img_serializers.data
            return event_img

    def get_creator(self, event):
        qs = self.context.get("qs")
        creator_name = ""
        if qs[event.event_id] == event:
            creator_name = qs[event.event_id].user.user_profile.full_name
            return creator_name
        else:
            return creator_name

    def get_event_creator_image(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        user_img = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            try:
                user_img = qs[event.event_id].user.display_pic.images.url
                return user_img
            except ObjectDoesNotExist:
                return user_img

    def get_interested_flag(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id in qs[event.event_id].interested_users.all():
                return True
            else:
                return False

    def get_creator_flag(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id == qs[event.event_id].user:
                return True
            else:
                return False

    def get_interested_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        interested_user_list = qs[event.event_id].interested_users.all()[:3]

        if len(interested_user_list) > 0:
            # Create Instance of User
            for int_user in interested_user_list:
                try:
                    images_array.append(int_user.display_pic.images.url)
                except ObjectDoesNotExist:
                    continue
                    print("{} user dp doesn't exist".format(int_user))

            # Return Data
            return images_array
        else:
            # Return Data
            return images_array


class InterestedEventsSerializer(serializers.ModelSerializer):
    event_img = serializers.SerializerMethodField('get_event_img')
    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img')
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag')
    is_creator = serializers.SerializerMethodField('get_creator_flag')
    user_images = serializers.SerializerMethodField('get_event_creator_image')
    creator = serializers.SerializerMethodField('get_creator')

    class Meta:
        model = Events
        fields = ['event_id', 'event_name', 'event_address', 'description', 'creator', 'user_images', 'is_user_interested', 'is_creator', 'event_price', 'event_type', 'location', 'event_date', 'event_time_from',
                  'event_time_to', 'event_interest', 'interested_users', 'interested_user_img', 'invited_users', 'event_img', 'event_location']

        read_only_fields = fields

    def get_event_img(self, event):
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            event_imgs = qs[event.event_id].images
            event_img_serializers = EventImageSerializer(event_imgs, many=True)
            event_img = event_img_serializers.data
            return event_img

    def get_creator(self, event):
        qs = self.context.get("qs")
        creator_name = ""
        if qs[event.event_id] == event:
            creator_name = qs[event.event_id].user.user_profile.full_name
            return creator_name
        else:
            return creator_name

    def get_interested_flag(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id in qs[event.event_id].interested_users.all():
                return True
            else:
                return False

    def get_event_creator_image(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        user_img = ""

        if qs[event.event_id] == event and (event.event_type == 'Private' or event.event_type == 'Close Friends'):
            requested_user_id = self.context.get("user")
            try:
                user_img = qs[event.event_id].user.display_pic.images.url
                return user_img
            except ObjectDoesNotExist:
                return user_img

        return user_img

    def get_creator_flag(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id == qs[event.event_id].user:
                return True
            else:
                return False

    def get_interested_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        interested_user_list = qs[event.event_id].interested_users.all()[:3]

        if len(interested_user_list) > 0:
            # Create Instance of User
            for int_user in interested_user_list:
                try:
                    images_array.append(int_user.display_pic.images.url)
                except ObjectDoesNotExist:
                    continue
                    print("{} user dp doesn't exist".format(int_user))

            # Return Data
            return images_array
        else:
            # Return Data
            return images_array
