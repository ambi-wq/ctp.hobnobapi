from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProfileDetails, Interest, UserImages, UserPreference, InstagramConnect, SpotifyConnect, \
    DisplayPicture, UserPromptQA, PromptQuestions, UserContactList, UserImagesComment
from events.models import Events
import random
from matching.models import UserContacts, CloseFriendList
from django.core.exceptions import ObjectDoesNotExist


class UserPromptQASerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField('get_question')

    class Meta:
        model = UserPromptQA
        fields = ['id', 'question', 'answer']

    def get_question(self, user_profile_qa):
        return user_profile_qa.question.question


class UserCreatePromptQASerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPromptQA
        exclude = ['user', ]


# class InterestSerializer(serializers.ModelSerializer):
class InterestSerializer(serializers.Serializer):
    interest_id = serializers.IntegerField(read_only=True)
    interest_name = serializers.CharField(read_only=True)

    color = serializers.SerializerMethodField('generate_hex_color', read_only=True)
    images = serializers.ImageField(read_only=True)

    class Meta:
        model = Interest
        # fields = ['interest_id', 'interest_name', 'color', 'images']

    def generate_hex_color(self, interest):
        self.color_gen = lambda: random.randint(0, 255)
        self.hex_code = '#%02X%02X%02X' % (
            self.color_gen(), self.color_gen(), self.color_gen())
        return self.hex_code


class UserInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['interest_id', 'interest_name']


class DisplayPictureSerializer(serializers.ModelSerializer):
    image_thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = DisplayPicture
        fields = ['id', 'images', 'image_thumbnail']
        # exclude = ['user', ]


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField('get_user_id')

    class Meta:
        model = ProfileDetails
        exclude = ['uuid', ]

    def get_user_id(self, profile):
        return profile.uuid.id


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContactList
        exclude = ['user', ]


class ProfileDataSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    user_age = serializers.IntegerField(read_only=True)
    gender = serializers.CharField(read_only=True)
    work_as = serializers.CharField(read_only=True)
    dob = serializers.DateField(read_only=True)
    home_town = serializers.CharField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    bio = serializers.CharField(read_only=True)
    fun_fact = serializers.CharField(read_only=True)
    phone = serializers.CharField(read_only=True)
    enjoy = serializers.CharField(read_only=True)
    education = serializers.CharField(read_only=True)
    company = serializers.CharField(read_only=True)
    spotify_connected = serializers.BooleanField(read_only=True)
    recorvery_mail = serializers.CharField(read_only=True)
    city = serializers.CharField(read_only=True)
    active = serializers.BooleanField(read_only=True)

    interest = serializers.StringRelatedField(many=True, read_only=True)
    display_pic = serializers.SerializerMethodField('get_display_pic')
    user_image = serializers.SerializerMethodField('get_user_profile_img')
    follower = serializers.SerializerMethodField('get_all_follower_list')
    following = serializers.SerializerMethodField('get_all_following_list')
    close_friends = serializers.SerializerMethodField('get_all_closefriends_list')
    hosted_events = serializers.SerializerMethodField('get_hosted_event_list')
    user_id = serializers.SerializerMethodField('get_user_id')
    questions = serializers.SerializerMethodField('get_questions_list')

    # company = serializers.SerializerMethodField('company')
    # education = serializers.SerializerMethodField('education')

    class Meta:
        model = ProfileDetails

        # fields = ['id', 'user_id', 'username', 'full_name', 'user_age', 'display_pic', 'gender', 'work_as', 'dob',
        #           'home_town', 'close_friends', 'is_available',
        #           'bio', 'fun_fact', 'phone', 'enjoy', 'interest', 'user_image', 'follower', 'following',
        #           'hosted_events', 'questions', 'education', 'company', 'spotify_connected', 'recorvery_mail', 'city',
        #           'active']

    def get_questions_list(self, profile):
        # Get User
        user_id = profile.uuid.id

        # Query for PromptQA
        qa_list = UserPromptQA.objects.filter(user=user_id)

        # Serialize List
        qa_serializer = UserPromptQASerializer(qa_list, many=True)

        # Return Data
        return qa_serializer.data

    def get_user_id(self, profile):
        return profile.uuid.id

    def get_display_pic(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Get Display Picture Object
        try:
            display_pic = DisplayPicture.objects.get(user=user_id)

            return display_pic.images.url
        except ObjectDoesNotExist:
            return ""

    def get_user_profile_img(self, profile):
        user_id = profile.uuid
        # user_image = UserImages.objects.filter(user=user_id)
        user_image = UserImages.objects.filter(user=user_id).order_by('-create_at')
        if len(user_image) > 0:
            user_img = user_image
            user_img_serializer = UserImageSerializer(user_img, many=True)
            return user_img_serializer.data
        else:
            return []

    def get_all_follower_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Follower User
        follower_list_count = UserContacts.objects.filter(
            follower=user_id).count()
        # Return Data
        return follower_list_count

    def get_all_following_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Follower User
        following_list_count = UserContacts.objects.filter(
            following=user_id).count()
        # Return Data
        return following_list_count

    def get_all_closefriends_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Follower User
        close_friends_list_count = CloseFriendList.objects.filter(
            user=user_id).count()
        # Return Data
        return close_friends_list_count

    def get_hosted_event_list(self, profile):
        # Get User ID
        user_id = profile.uuid
        # print("user_id", user_id)
        # Query to get All Follower User
        hosted_event_list_count = Events.objects.filter(
            user=user_id).count()

        # Return Data
        return hosted_event_list_count


class UserInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileDetails
        fields = ['interest']


class UserImageSerializer(serializers.ModelSerializer):
    image_thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = UserImages
        fields = ['id', 'images', 'image_thumbnail', 'create_at', 'update_at', 'height', 'width']
        # exclude = ['user', ]


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        exclude = ['user', ]


class InstagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramConnect
        exclude = ['user', ]


# class DowntoChillSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = ProfileDetails
#         fields = ['id', 'username', 'full_name', 'uuid', 'user_image']


class ProfileDetailsSerializer(serializers.ModelSerializer):
    user_image = serializers.SerializerMethodField('get_user_profile_img')

    class Meta:
        model = ProfileDetails
        fields = ['id', 'username', 'full_name', 'uuid', 'user_image']

    def get_user_profile_img(self, profile):
        user_id = profile.uuid
        user_image = DisplayPicture.objects.filter(user=user_id)
        if len(user_image) > 0:
            user_img = user_image[0]
            user_img_serializer = DisplayPictureSerializer(user_img)

            return user_img_serializer.data
        else:
            return {}


class DowntoChillSerializer(serializers.ModelSerializer):
    user_image = serializers.SerializerMethodField('get_user_profile_img')
    user_uid = serializers.SerializerMethodField('get_user_uid')

    class Meta:
        model = ProfileDetails
        fields = ['id', 'username', 'full_name', 'uuid', 'user_image', 'user_uid']

    def get_user_uid(self, profile):
        user_id = profile.uuid
        print("user_id", user_id)
        if user_id:
            return str(user_id)
        else:
            return {}

    def get_user_profile_img(self, profile):
        user_id = profile.uuid
        user_image = DisplayPicture.objects.filter(user=user_id)
        if len(user_image) > 0:
            user_img = user_image[0]
            user_img_serializer = DisplayPictureSerializer(user_img)

            return user_img_serializer.data
        else:
            return {}


class OtherUserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    uuid = serializers.SerializerMethodField('get_uuid',read_only=True)
    user_age = serializers.IntegerField(read_only=True)
    gender = serializers.CharField(read_only=True)
    work_as = serializers.CharField(read_only=True)
    home_town = serializers.CharField(read_only=True)
    bio = serializers.CharField(read_only=True)
    fun_fact = serializers.CharField(read_only=True)
    enjoy = serializers.CharField(read_only=True)
    education = serializers.CharField(read_only=True)
    company = serializers.CharField(read_only=True)

    interest = serializers.StringRelatedField(many=True, read_only=True)
    display_pic = serializers.SerializerMethodField('get_display_pic')
    user_image = serializers.SerializerMethodField('get_user_profile_img')
    is_following = serializers.SerializerMethodField('get_is_follow_flag')
    follower = serializers.SerializerMethodField('get_all_follower_list')
    following = serializers.SerializerMethodField('get_all_following_list')
    questions = serializers.SerializerMethodField('get_questions_list')
    hosted_events = serializers.SerializerMethodField('get_hosted_event_list')
    user_uid = serializers.SerializerMethodField('get_user_uid')

    class Meta:
        model = ProfileDetails
        # fields = ['id', 'username', 'full_name', 'uuid', 'user_age', 'display_pic', 'gender', 'is_following',
        #           'home_town', 'user_uid',
        #           'work_as', 'bio', 'fun_fact', 'enjoy', 'interest', 'user_image', 'follower', 'following', 'questions',
        #           'hosted_events', 'education', 'company']

    def get_questions_list(self, profile):
        # Get User
        user_id = profile.uuid.id

        # Query for PromptQA
        qa_list = UserPromptQA.objects.filter(user=user_id)

        # Serialize List
        qa_serializer = UserPromptQASerializer(qa_list, many=True)

        # Return Data
        return qa_serializer.data

    def get_display_pic(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Get Display Picture Object
        try:
            display_pic = DisplayPicture.objects.get(user=user_id)

            return display_pic.images.url
        except ObjectDoesNotExist:
            return ""

    def get_user_profile_img(self, profile):
        user_id = profile.uuid
        user_image = UserImages.objects.filter(user=user_id).order_by('-create_at')
        if len(user_image) > 0:
            user_img = user_image
            user_img_serializer = UserImageSerializer(user_img, many=True,read_only=True)
            return user_img_serializer.data
        else:
            return []

    def get_is_follow_flag(self, profile):
        # Get Requested User ID
        requested_user_id = self.context.get("user_id")

        # Get User ID
        user_id = profile.uuid

        # Make Query to User Contact
        user_contact = UserContacts.objects.filter(
            following=requested_user_id, follower=user_id).count()

        if user_contact > 0:
            return True
        else:
            return False

    def get_all_follower_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Follower User
        follower_list_count = UserContacts.objects.filter(
            follower=user_id).count()

        # Return Data
        return follower_list_count

    def get_all_following_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Follower User
        following_list_count = UserContacts.objects.filter(
            following=user_id).count()

        # Return Data
        return following_list_count

    def get_hosted_event_list(self, profile):
        # Get User ID
        user_id = profile.uuid
        print("user_id", user_id)

        # Get Requested User ID
        requested_user_id = self.context.get("user_id")

        # new added
        # Check If User Following
        is_exist = self.get_is_follow_flag(profile)

        # Check If User is Close Friend
        is_close_friend = CloseFriendList.objects.values_list(
            'user', flat=True).filter(user=requested_user_id, close_friend=user_id).exists()

        # case 1 : following each other and close friend
        if is_exist and is_close_friend:
            hosted_event_list_count = Events.objects.filter(user=user_id).count()

        # case 2 : following each other and not close friend
        elif is_exist and is_close_friend is False:
            hosted_event_list_count = Events.objects.filter(user=user_id, event_type__in=["Public", "Private"]).count()

        # case 3 : not following each other and close friend
        elif is_exist is False and is_close_friend:
            hosted_event_list_count = Events.objects.filter(user=user_id,
                                                            event_type__in=["Public", "Close Friends"]).count()

        # case 4 : not following each other and not close friend
        # elif is_exist is False and is_close_friend is False:
        else:
            hosted_event_list_count = Events.objects.filter(user=user_id, event_type="Public").count()

        # hosted_event_list_count = Events.objects.filter(
        #     user=user_id).count()
        print("hosted_event_list_count", hosted_event_list_count)

        # Return Data
        return hosted_event_list_count

    def get_user_uid(self, profile):
        user_id = profile.uuid
        print("user_id", user_id)
        if user_id:
            return str(user_id)
        else:
            return {}

    def get_uuid(self,profile):
        return profile.uuid_id


class SpotifySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpotifyConnect
        fields = '__all__'


class PromptQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptQuestions
        fields = ['id', 'question']


class ReplaceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPromptQA
        fields = '__all__'


class UserImagesCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImagesComment
        exclude = ['comment_user']


class AllUserImageCommentsSerializer(serializers.ModelSerializer):
    profile_img = serializers.SerializerMethodField('get_profile_img')
    full_name = serializers.SerializerMethodField('get_fullname')
    username = serializers.SerializerMethodField('get_username')
    total_likes = serializers.SerializerMethodField('get_total_likes')

    class Meta:
        model = UserImagesComment
        fields = ['comment_id', 'username', 'full_name', 'profile_img', 'comment', 'comment_user', 'total_likes',
                  'created_at', 'updated_at']

    def get_profile_img(self, obj):
        try:
            user_image = obj.comment_user.display_pic
            user_img_serializer = DisplayPictureSerializer(user_image)
            return [user_img_serializer.data]
        except:
            return []

    def get_fullname(self, obj):
        return obj.comment_user.user_profile.full_name

    def get_username(self, obj):
        return obj.comment_user.user_profile.username

    def get_total_likes(self, obj):
        total_like = obj.liked_user.count()
        return total_like


class UserProfileImageDetailsSerializer(serializers.ModelSerializer):
    image_thumbnail = serializers.ImageField(read_only=True)
    liked_user_img = serializers.SerializerMethodField('get_liked_user_img')
    liked_username = serializers.SerializerMethodField('get_liked_username')

    class Meta:
        model = UserImages
        fields = ['id', 'images', 'image_thumbnail', 'create_at', 'update_at', 'liked_user', 'liked_user_img', 'height',
                  'width', 'liked_username']

    def get_liked_user_img(self, user_image):
        image_array = []
        # Get likes user list
        liked_user_list = user_image.liked_user.all()[:3]
        if len(liked_user_list) > 0:
            for like_user in liked_user_list:
                try:
                    image_array.append(like_user.display_pic.images.url)
                except ObjectDoesNotExist:
                    continue
                    print("{} user dp doesn;t exist".format(like_user))

            return image_array
        else:
            return image_array

    def get_liked_username(self, user_image):
        username_list = []
        # Get liked username list upto  2 user
        liked_username = user_image.liked_user.all()[:2]
        if len(liked_username) > 0:
            for like_user in liked_username:
                username_list.append(like_user.user_profile.username)

        return username_list
