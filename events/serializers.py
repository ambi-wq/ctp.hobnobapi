from rest_framework import serializers
from .models import ReportEventsDetails, EventImages, Events, CuratedEvents, EventComments, CurateImages, ImagesUpload, \
    EventInterestedUsers
from drf_extra_fields.geo_fields import PointField
from userprofile.models import UserImages, ProfileDetails,Interest
from userprofile.serializers import UserImageSerializer, ProfileDetailsSerializer, DisplayPictureSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timezone

User = get_user_model()


class ReportEventsDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportEventsDetails
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    event_location = PointField()
    event_img = serializers.SerializerMethodField('get_event_img')
    event_cover_img = serializers.SerializerMethodField('get_event_cover_img')

    class Meta:
        model = Events
        # exclude = ['user']
        extra_kwargs = {'interested_users': {'required': False}}
        fields = ['event_id', 'event_location', 'event_name', 'event_type', 'description', 'event_city', 'location',
                  'event_address', 'event_date', 'event_time_from', 'event_time_to', 'event_price', 'create_at',
                  'update_at','event_end_date', 'event_interest', 'interested_users', 'invited_users', 'going_users',
                  'yet_to_decide_users','event_img','event_cover_img']

    def get_event_img(self, event):

        event_img = []
        if EventImages.objects.filter(event=event).exists():
            event_imgs = EventImages.objects.filter(event=event, image_type="event")  # .order_by("-id")
            event_img_serializers = EventImageSerializer(event_imgs, many=True)
            event_img = event_img_serializers.data

        return event_img

    def get_event_cover_img(self, event):
        event_cover_img = []
        if EventImages.objects.filter(event=event).exists():
            event_cover_img = EventImages.objects.filter(event=event, image_type="cover")
            # print("event_cover_image", event_cover_img)
            event_cover_img_serializers = EventImageSerializer(event_cover_img, many=True)
            event_cover_img = event_cover_img_serializers.data
        return event_cover_img


class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImages
        fields = '__all__'


class ImagesUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagesUpload
        fields = '__all__'


# class EventListSerializer(serializers.ModelSerializer):
class EventListSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(read_only=True)
    event_name = serializers.CharField(read_only=True)
    event_address = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    event_price = serializers.FloatField(read_only=True)
    event_type = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    event_date = serializers.DateField(read_only=True)
    event_time_from = serializers.TimeField(read_only=True)
    event_time_to = serializers.TimeField(read_only=True)
    event_interest = serializers.PrimaryKeyRelatedField(queryset=Interest.objects.all(), many=True)
    interested_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    invited_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    event_city = serializers.CharField(read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    event_end_date = serializers.DateField(read_only=True)
    going_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    yet_to_decide_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    event_img = serializers.SerializerMethodField('get_event_img',read_only=True)

    user_images = serializers.SerializerMethodField('get_event_creator_image',read_only=True)

    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img',read_only=True)
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag',read_only=True)
    is_creator = serializers.SerializerMethodField('get_creator_flag',read_only=True)

    # creator = serializers.SerializerMethodField('get_creator')
    creator_id = serializers.SerializerMethodField('get_event_creator_id',read_only=True)
    creator_username = serializers.SerializerMethodField('get_event_creator_username',read_only=True)

    going_user_img = serializers.SerializerMethodField('get_going_user_img',read_only=True)
    yet_to_decide_user_img = serializers.SerializerMethodField('get_yet_to_decide_user_img',read_only=True)
    type = serializers.SerializerMethodField('get_type',read_only=True)

    class Meta:
        model = Events
        # fields = ['event_id', 'event_name', 'event_address', 'description', 'is_user_interested', 'is_creator',
        #           'event_price', 'event_type', 'location', 'event_date', 'event_time_from',
        #           'event_time_to', 'event_interest', 'interested_users', 'interested_user_img', 'invited_users',
        #           'event_img', 'event_location', 'user_images', 'creator_id', 'create_at', 'event_city',
        #           'creator_username', 'event_end_date', 'going_users', 'yet_to_decide_users', 'going_user_img',
        #           'yet_to_decide_user_img', 'type']
        #
        # read_only_fields = fields

    def get_event_img(self, event):
        qs = self.context.get("qs")
        print("qs3", qs)
        event_img = []

        if qs[event.event_id] == event:
            event_imgs = qs[event.event_id].images
            print("event_imgs", event_imgs)
            event_img_serializers = EventImageSerializer(event_imgs, many=True)
            event_img = event_img_serializers.data
            return event_img

    def get_event_creator_username(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        print("qs", qs)
        user_username = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            try:
                user_username = qs[event.event_id].user.user_profile.username
                return user_username
            except ObjectDoesNotExist:
                return user_username

    def get_event_creator_id(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        user_id = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            print("requested_user_id", requested_user_id)
            try:
                user_id = qs[event.event_id].user.id
                return user_id
            except ObjectDoesNotExist:
                return user_id

    def get_creator(self, event):
        qs = self.context.get("qs")
        creator_name = ""
        print("queryset", qs[event.event_id])
        try:
            creator_name = qs[event.event_id].user.user_profile.full_name
            print("creator_name", creator_name, dir(creator_name), type(creator_name))
            return creator_name
        except:
            pass

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

    def get_going_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        going_user_list = qs[event.event_id].going_users.all()[:3]

        if len(going_user_list) > 0:
            # Create Instance of User
            for int_user in going_user_list:
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

    def get_yet_to_decide_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        yet_to_decide_user_list = qs[event.event_id].yet_to_decide_users.all()[:3]

        if len(yet_to_decide_user_list) > 0:
            # Create Instance of User
            for int_user in yet_to_decide_user_list:
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

    def get_type(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        type = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id in qs[event.event_id].interested_users.all():
                type = "interested"
            elif requested_user_id in qs[event.event_id].going_users.all():
                type = "going"
            elif requested_user_id in qs[event.event_id].yet_to_decide_users.all():
                type = "yet_to_decide"
        return type


# class EventDetailsListSerializer(serializers.ModelSerializer):
class EventDetailsListSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(read_only=True)
    event_name = serializers.CharField(read_only=True)
    event_address = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    event_price = serializers.FloatField(read_only=True)
    event_type = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    event_date = serializers.DateField(read_only=True)
    event_time_from = serializers.TimeField(read_only=True)
    event_time_to = serializers.TimeField(read_only=True)
    event_interest = serializers.PrimaryKeyRelatedField(queryset=Interest.objects.all(), many=True)
    interested_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=True)
    invited_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=True)
    event_city = serializers.CharField(read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    event_end_date = serializers.DateField(read_only=True)
    going_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=True)
    yet_to_decide_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=True)

    event_img = serializers.SerializerMethodField('get_event_img',read_only=True)

    event_cover_img = serializers.SerializerMethodField('get_event_cover_img',read_only=True)

    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img',read_only=True)
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag',read_only=True)
    is_creator = serializers.SerializerMethodField('get_creator_flag',read_only=True)
    user_images = serializers.SerializerMethodField('get_event_creator_image',read_only=True)
    creator_id = serializers.SerializerMethodField('get_creator_id',read_only=True)
    creator = serializers.SerializerMethodField('get_creator',read_only=True)
    creator_username = serializers.SerializerMethodField('get_event_creator_username',read_only=True)

    going_user_img = serializers.SerializerMethodField('get_going_user_img',read_only=True)
    yet_to_decide_user_img = serializers.SerializerMethodField('get_yet_to_decide_user_img',read_only=True)
    type = serializers.SerializerMethodField('get_type',read_only=True)

    class Meta:
        model = Events
        # fields = ['event_id', 'event_name', 'event_address', 'creator', 'description', 'user_images',
        #           'is_user_interested', 'is_creator', 'event_price', 'event_type', 'location', 'event_date',
        #           'event_time_from',
        #           'event_time_to', 'event_interest', 'interested_users', 'interested_user_img', 'invited_users',
        #           'event_img', 'event_cover_img', 'event_location', 'event_city', 'creator_username', 'creator_id',
        #           'create_at', 'event_end_date', 'going_users', 'yet_to_decide_users', 'going_user_img',
        #           'yet_to_decide_user_img', 'type']

    def get_event_img(self, event):

        event_img = []
        if EventImages.objects.filter(event=event).exists():
            event_imgs = EventImages.objects.filter(event=event, image_type="event")  # .order_by("-id")
            event_img_serializers = EventImageSerializer(event_imgs, many=True)
            event_img = event_img_serializers.data

        return event_img

    def get_event_cover_img(self, event):
        event_cover_img = []
        if EventImages.objects.filter(event=event).exists():
            event_cover_img = EventImages.objects.filter(event=event, image_type="cover")
            # print("event_cover_image", event_cover_img)
            event_cover_img_serializers = EventImageSerializer(event_cover_img, many=True)
            event_cover_img = event_cover_img_serializers.data
        return event_cover_img

    def get_creator(self, event):
        creator_name = ""
        try:
            creator_name = event.user.user_profile.full_name
            return creator_name
        except:
            return creator_name

    def get_creator_id(self, event):
        creator_id = ""
        try:
            creator_id = event.user.id
            return creator_id
        except:
            return creator_id

    def get_event_creator_username(self, event):
        creator_username = ""
        try:
            creator_username = event.user.user_profile.username
            return creator_username
        except:
            return creator_username

    # def get_event_creator_username(self, event):
    #     # Get Requested User ID
    #     qs = self.context.get("qs")
    #     print("qs", qs)
    #     user_username = ""

    #     if qs[event.event_id] == event:
    #         requested_user_id = self.context.get("user")
    #         try:
    #             user_username = qs[event.event_id].user.user_profile.username
    #             return user_username
    #         except ObjectDoesNotExist:
    #             return user_username

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

    def get_going_user_img(self, event):
        images_array = []
        # Get Interested User List
        going_user_list = event.going_users.all()[:3]

        if len(going_user_list) > 0:
            # Create Instance of User
            for int_user in going_user_list:
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

    def get_yet_to_decide_user_img(self, event):
        images_array = []
        # Get Interested User List
        yet_to_decide_user_list = event.yet_to_decide_users.all()[:3]

        if len(yet_to_decide_user_list) > 0:
            # Create Instance of User
            for int_user in yet_to_decide_user_list:
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

    def get_type(self, event):
        # Get Requested User ID
        type = ""
        requested_user_id = self.context.get("user")
        if requested_user_id in event.interested_users.all():
            type = "interested"
        elif requested_user_id in event.going_users.all():
            type = "going"
        elif requested_user_id in event.yet_to_decide_users.all():
            type = "yet_to_decide"
        return type


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


class EventInterestedUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventInterestedUsers
        fields = '__all__'


# class PrivateEventSerializer(serializers.ModelSerializer):
class PrivateEventSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(read_only=True)
    event_name = serializers.CharField(read_only=True)
    event_address = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    event_price = serializers.FloatField(read_only=True)
    event_type = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    event_date = serializers.DateField(read_only=True)
    event_time_from = serializers.TimeField(read_only=True)
    event_time_to = serializers.TimeField(read_only=True)
    event_interest = serializers.PrimaryKeyRelatedField(queryset=Interest.objects.all(), many=True)
    interested_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    invited_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    event_city = serializers.CharField(read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    event_end_date = serializers.DateField(read_only=True)
    going_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    yet_to_decide_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    event_img = serializers.SerializerMethodField('get_event_img',read_only=True)
    user_images = serializers.SerializerMethodField('get_event_creator_image',read_only=True)
    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img',read_only=True)
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag',read_only=True)
    is_creator = serializers.SerializerMethodField('get_creator_flag',read_only=True)
    # creator = serializers.SerializerMethodField('get_creator')
    creator_id = serializers.SerializerMethodField('get_event_creator_id',read_only=True)
    creator_username = serializers.SerializerMethodField('get_event_creator_username',read_only=True)

    going_user_img = serializers.SerializerMethodField('get_going_user_img',read_only=True)
    yet_to_decide_user_img = serializers.SerializerMethodField('get_yet_to_decide_user_img',read_only=True)
    type = serializers.SerializerMethodField('get_type',read_only=True)

    class Meta:
        model = Events
        # fields = ['event_id', 'event_name', 'event_address', 'description', 'user_images', 'event_img', 'event_price',
        #           'event_type', 'location', 'event_date', 'event_time_from',
        #           'event_time_to', 'event_interest', 'interested_users', 'invited_users', 'event_location',
        #           'is_user_interested', 'is_creator', 'creator_id', 'create_at', 'event_city', 'creator_username',
        #           'event_end_date', 'going_users', 'yet_to_decide_users', 'type', 'interested_user_img',
        #           'going_user_img', 'yet_to_decide_user_img']
        #
        # read_only_fields = fields

    def get_event_img(self, event):
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            event_imgs = qs[event.event_id].images  # .order_by("-id")
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

    def get_event_creator_username(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        # print("qs", qs)
        user_username = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            try:
                user_username = qs[event.event_id].user.user_profile.username
                return user_username
            except ObjectDoesNotExist:
                return user_username

    def get_event_creator_id(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        user_id = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            # print("requested_user_id", requested_user_id)
            try:
                user_id = qs[event.event_id].user.id
                return user_id
            except ObjectDoesNotExist:
                return user_id

    # def get_event_creator_username(self, event):
    #     # Get Requested User ID
    #     qs = self.context.get("qs")
    #     user_username = ""

    #     if qs[event.event_id] == event:
    #         requested_username = self.context.get("user")
    #         try:
    #             user_username = qs[event.event_id].user
    #             return user_username
    #         except ObjectDoesNotExist:
    #             return user_username

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

    def get_going_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        going_user_list = qs[event.event_id].going_users.all()[:3]

        if len(going_user_list) > 0:
            # Create Instance of User
            for int_user in going_user_list:
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

    def get_yet_to_decide_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        yet_to_decide_user_list = qs[event.event_id].yet_to_decide_users.all()[:3]

        if len(yet_to_decide_user_list) > 0:
            # Create Instance of User
            for int_user in yet_to_decide_user_list:
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

    def get_type(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        type = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id in qs[event.event_id].interested_users.all():
                type = "interested"
            elif requested_user_id in qs[event.event_id].going_users.all():
                type = "going"
            elif requested_user_id in qs[event.event_id].yet_to_decide_users.all():
                type = "yet_to_decide"
        return type


# class InterestedEventsSerializer(serializers.ModelSerializer):
class InterestedEventsSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(read_only=True)
    event_name = serializers.CharField(read_only=True)
    event_address = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    event_price = serializers.FloatField(read_only=True)
    event_type = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    event_date = serializers.DateField(read_only=True)
    event_time_from = serializers.TimeField(read_only=True)
    event_time_to = serializers.TimeField(read_only=True)
    event_interest = serializers.PrimaryKeyRelatedField(queryset=Interest.objects.all(), many=True)
    interested_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    invited_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    event_city = serializers.CharField(read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    update_at = serializers.DateTimeField(read_only=True)
    event_end_date = serializers.DateField(read_only=True)
    going_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    yet_to_decide_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    event_img = serializers.SerializerMethodField('get_event_img',read_only=True)
    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img',read_only=True)
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag',read_only=True)
    is_creator = serializers.SerializerMethodField('get_creator_flag',read_only=True)
    user_images = serializers.SerializerMethodField('get_event_creator_image',read_only=True)
    creator = serializers.SerializerMethodField('get_creator',read_only=True)
    creator_id = serializers.SerializerMethodField('get_event_creator_id',read_only=True)
    creator_username = serializers.SerializerMethodField('get_event_creator_username',read_only=True)

    going_user_img = serializers.SerializerMethodField('get_going_user_img',read_only=True)
    yet_to_decide_user_img = serializers.SerializerMethodField('get_yet_to_decide_user_img',read_only=True)
    type = serializers.SerializerMethodField('get_type',read_only=True)

    class Meta:
        model = Events
        # fields = ['event_id', 'event_name', 'event_address', 'description', 'creator', 'user_images',
        #           'is_user_interested', 'is_creator', 'event_price', 'event_type', 'location', 'event_date',
        #           'event_time_from',
        #           'event_time_to', 'event_interest', 'interested_users', 'interested_user_img', 'invited_users',
        #           'event_img', 'event_location', 'create_at', 'update_at', 'creator_username', 'creator_id',
        #           'event_city', 'event_end_date', 'going_users', 'yet_to_decide_users', 'going_user_img',
        #           'yet_to_decide_user_img', 'type']
        #
        # read_only_fields = fields

    def get_event_img(self, event):
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            event_imgs = qs[event.event_id].images  # .order_by("-id")
            event_img_serializers = EventImageSerializer(event_imgs, many=True)
            event_img = event_img_serializers.data
            return event_img

    def get_event_creator_username(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        print("qs", qs)
        user_username = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            try:
                user_username = qs[event.event_id].user.user_profile.username
                return user_username
            except ObjectDoesNotExist:
                return user_username

    def get_event_creator_id(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        user_id = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            print("requested_user_id", requested_user_id)
            try:
                user_id = qs[event.event_id].user.id
                return user_id
            except ObjectDoesNotExist:
                return user_id

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

        if qs[event.event_id] == event:
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

    def get_going_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        going_user_list = qs[event.event_id].going_users.all()[:3]

        if len(going_user_list) > 0:
            # Create Instance of User
            for int_user in going_user_list:
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

    def get_yet_to_decide_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        yet_to_decide_user_list = qs[event.event_id].yet_to_decide_users.all()[:3]

        if len(yet_to_decide_user_list) > 0:
            # Create Instance of User
            for int_user in yet_to_decide_user_list:
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

    def get_type(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        type = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id in qs[event.event_id].interested_users.all():
                type = "interested"
            elif requested_user_id in qs[event.event_id].going_users.all():
                type = "going"
            elif requested_user_id in qs[event.event_id].yet_to_decide_users.all():
                type = "yet_to_decide"
        return type


class HostedEventSerializer(serializers.ModelSerializer):
    event_img = serializers.SerializerMethodField('get_event_img')
    user_images = serializers.SerializerMethodField('get_event_creator_image')
    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img')
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag')
    is_creator = serializers.SerializerMethodField('get_creator_flag')
    creator = serializers.SerializerMethodField('get_creator')
    creator_id = serializers.SerializerMethodField('get_event_creator_id')
    creator_username = serializers.SerializerMethodField('get_event_creator_username')

    going_user_img = serializers.SerializerMethodField('get_going_user_img')
    yet_to_decide_user_img = serializers.SerializerMethodField('get_yet_to_decide_user_img')
    type = serializers.SerializerMethodField('get_type')

    class Meta:
        model = Events
        fields = ['event_id', 'event_name', 'event_address', 'description', 'user_images', 'creator', 'event_img',
                  'is_user_interested', 'is_creator', 'event_price', 'event_type', 'location', 'event_date',
                  'event_time_from',
                  'event_time_to', 'event_interest', 'interested_users', 'interested_user_img', 'invited_users',
                  'event_location', 'create_at', 'event_city', 'creator_id', 'creator_username', 'event_end_date',
                  'going_users', 'yet_to_decide_users', 'going_user_img', 'yet_to_decide_user_img', 'type']

        read_only_fields = fields

    def get_event_img(self, event):
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            event_imgs = qs[event.event_id].images  # .order_by("-id")
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

    def get_event_creator_username(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        print("qs", qs)
        user_username = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            try:
                user_username = qs[event.event_id].user.user_profile.username
                return user_username
            except ObjectDoesNotExist:
                return user_username

    def get_event_creator_id(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        user_id = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            print("requested_user_id", requested_user_id)
            try:
                user_id = qs[event.event_id].user.id
                return user_id
            except ObjectDoesNotExist:
                return user_id

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

    def get_going_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        going_user_list = qs[event.event_id].going_users.all()[:3]

        if len(going_user_list) > 0:
            # Create Instance of User
            for int_user in going_user_list:
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

    def get_yet_to_decide_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        yet_to_decide_user_list = qs[event.event_id].yet_to_decide_users.all()[:3]

        if len(yet_to_decide_user_list) > 0:
            # Create Instance of User
            for int_user in yet_to_decide_user_list:
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

    def get_type(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        type = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id in qs[event.event_id].interested_users.all():
                type = "interested"
            elif requested_user_id in qs[event.event_id].going_users.all():
                type = "going"
            elif requested_user_id in qs[event.event_id].yet_to_decide_users.all():
                type = "yet_to_decide"
        return type


# class GoingEventsSerializer(serializers.ModelSerializer):
class GoingEventsSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(read_only=True)
    event_name = serializers.CharField(read_only=True)
    event_address = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    event_price = serializers.FloatField(read_only=True)
    event_type = serializers.CharField(read_only=True)
    location = serializers.CharField(read_only=True)
    event_date = serializers.DateField(read_only=True)
    event_time_from = serializers.TimeField(read_only=True)
    event_time_to = serializers.TimeField(read_only=True)
    event_interest = serializers.PrimaryKeyRelatedField(queryset=Interest.objects.all(), many=True)
    interested_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    invited_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    event_city = serializers.CharField(read_only=True)
    create_at = serializers.DateTimeField(read_only=True)
    update_at = serializers.DateTimeField(read_only=True)
    event_end_date = serializers.DateField(read_only=True)
    going_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    yet_to_decide_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    event_img = serializers.SerializerMethodField('get_event_img', read_only=True)
    interested_user_img = serializers.SerializerMethodField(
        'get_interested_user_img', read_only=True)
    event_location = PointField()
    is_user_interested = serializers.SerializerMethodField(
        'get_interested_flag', read_only=True)
    is_creator = serializers.SerializerMethodField('get_creator_flag', read_only=True)
    user_images = serializers.SerializerMethodField('get_event_creator_image', read_only=True)
    creator = serializers.SerializerMethodField('get_creator', read_only=True)
    creator_id = serializers.SerializerMethodField('get_event_creator_id', read_only=True)
    creator_username = serializers.SerializerMethodField('get_event_creator_username', read_only=True)

    going_user_img = serializers.SerializerMethodField('get_going_user_img', read_only=True)
    yet_to_decide_user_img = serializers.SerializerMethodField('get_yet_to_decide_user_img', read_only=True)
    type = serializers.SerializerMethodField('get_type', read_only=True)

    class Meta:
        model = Events
        # fields = ['event_id', 'event_name', 'event_address', 'description', 'creator', 'user_images',
        #           'is_user_interested', 'is_creator', 'event_price', 'event_type', 'location', 'event_date',
        #           'event_time_from',
        #           'event_time_to', 'event_interest', 'interested_users', 'interested_user_img', 'invited_users',
        #           'event_img', 'event_location', 'create_at', 'update_at', 'creator_username', 'creator_id',
        #           'event_city', 'event_end_date', 'going_users', 'going_user_img', 'yet_to_decide_users',
        #           'yet_to_decide_user_img', 'type']
        # fields = ['event_id', 'event_name', 'event_address', 'description', 'creator', 'user_images',
        #           'is_user_interested', 'is_creator', 'event_price', 'event_type', 'location', 'event_date',
        #           'event_time_from',
        #           'event_time_to', 'event_interest', 'interested_users', 'interested_user_img',
        #           'event_img', 'event_location', 'create_at', 'update_at', 'creator_username', 'creator_id',
        #           'event_city', 'event_end_date', 'going_users', 'going_user_img', 'yet_to_decide_users',
        #           'yet_to_decide_user_img', 'type']
        #
        #
        # read_only_fields = fields

    def get_event_img(self, event):
        qs = self.context.get("qs")
        event_img = []

        if qs[event.event_id] == event:
            event_imgs = qs[event.event_id].images  # .order_by("-id")
            event_img_serializers = EventImageSerializer(event_imgs, many=True)
            event_img = event_img_serializers.data
            return event_img

    def get_event_creator_username(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        print("qs", qs)
        user_username = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            try:
                user_username = qs[event.event_id].user.user_profile.username
                return user_username
            except ObjectDoesNotExist:
                return user_username

    def get_event_creator_id(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        user_id = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            print("requested_user_id", requested_user_id)
            try:
                user_id = qs[event.event_id].user.id
                return user_id
            except ObjectDoesNotExist:
                return user_id

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

        if qs[event.event_id] == event:
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

    def get_going_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        going_user_list = qs[event.event_id].going_users.all()[:3]

        if len(going_user_list) > 0:
            # Create Instance of User
            for int_user in going_user_list:
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

    def get_yet_to_decide_user_img(self, event):
        images_array = []
        # Get Interested User List
        qs = self.context.get("qs")
        yet_to_decide_user_list = qs[event.event_id].yet_to_decide_users.all()[:3]

        if len(yet_to_decide_user_list) > 0:
            # Create Instance of User
            for int_user in yet_to_decide_user_list:
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

    def get_type(self, event):
        # Get Requested User ID
        qs = self.context.get("qs")
        type = ""

        if qs[event.event_id] == event:
            requested_user_id = self.context.get("user")
            if requested_user_id in qs[event.event_id].interested_users.all():
                type = "interested"
            elif requested_user_id in qs[event.event_id].going_users.all():
                type = "going"
            elif requested_user_id in qs[event.event_id].yet_to_decide_users.all():
                type = "yet_to_decide"
        return type
