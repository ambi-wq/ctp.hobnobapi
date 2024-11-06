from rest_framework import serializers
from matching.models import UserContacts, UserScore, UserLocation, CloseFriendList,SuggesstedUser
from userprofile.models import ProfileDetails, UserImages, Interest, DisplayPicture, UsersContacts
from userprofile.serializers import ProfileDetailsSerializer, UserImageSerializer, UserInterestSerializer, \
    DisplayPictureSerializer
from django.contrib.gis.db.models.functions import Distance
from drf_extra_fields.geo_fields import PointField
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class UserScoreSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserScore
        fields = '__all__'


class DesirableScoreSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserScore
        fields = ['desirable_score']


class UserContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContacts
        exclude = ['following', 'hosted_events']


class UserFollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContacts
        fields = '__all__'
        # depth = 1


class LocationSerializer(serializers.ModelSerializer):
    last_location = PointField()

    class Meta:
        model = UserLocation
        fields = ['last_location', 'place']


class UserExploreSerializer(serializers.ModelSerializer):
    desirable_score = serializers.SerializerMethodField('get_desirable_score')
    images = serializers.SerializerMethodField('get_user_profile_img')
    location = serializers.SerializerMethodField('get_user_location')
    interest = serializers.StringRelatedField(many=True, read_only=True)
    follower = serializers.SerializerMethodField('get_all_follower_list')

    class Meta:
        model = ProfileDetails
        fields = ['uuid', 'full_name', 'gender', 'follower', 'interest',
                  'user_age', 'desirable_score', 'location', 'images']

    def get_desirable_score(self, profile):
        # Get Potential User Profile
        potential_user_id = profile.uuid

        # Get Deriable Score
        score = UserScore.objects.get(user=potential_user_id)
        potential_score = score.desirable_score

        # Get Requested User ID
        requested_user_id = self.context.get("user_id")

        # Get Requested User Profile
        request_user_profile = ProfileDetails.objects.get(
            uuid=requested_user_id)

        # Calculate Age Difference
        age_difference = abs(profile.user_age - request_user_profile.user_age)
        if age_difference == 0 or age_difference == 1:
            potential_score += 6.4
        else:
            potential_score += 6.4 / age_difference

        # union_interest = request_user_profile.interest.all().intersection(profile.interest.all())

        # Calculate Interest Matching
        # potential_score += 6.4 * union_interest.count()

        # Calculate Distance

        # Get Requested User Location
        request_user_location = UserLocation.objects.get(
            user=requested_user_id).last_location

        # Get Potential User Location DIstance
        for location in UserLocation.objects.filter(user=potential_user_id).annotate(
                distance=Distance('last_location', request_user_location)):

            # User Distance
            potential_user_distance = location.distance.km
            if potential_user_distance == 0 or potential_user_distance == 1:
                potential_score += 32
            else:
                potential_score += 32 / potential_user_distance

        # return {'desirable_score': }
        return potential_score

    def get_user_profile_img(self, profile):
        user_id = profile.uuid
        user_image = UserImages.objects.filter(user=user_id)
        user_img_serializer = UserImageSerializer(user_image, many=True)
        return user_img_serializer.data

    def get_user_location(self, profile):
        user_id = profile.uuid
        location = UserLocation.objects.get(user=user_id)
        location_serializer = LocationSerializer(location)
        return location_serializer.data

    def get_all_follower_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Follower User
        follower_list_count = UserContacts.objects.filter(follower=user_id).count()

        # Return Data
        return follower_list_count


class CloseFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloseFriendList
        exclude = ['user']


class ProfileDetailsDataSerializer(serializers.ModelSerializer):
    user_image = serializers.SerializerMethodField('get_user_profile_img')
    following = serializers.SerializerMethodField('get_all_following_list')
    follower = serializers.SerializerMethodField('get_all_follower_list')

    class Meta:
        model = ProfileDetails
        fields = ['id', 'full_name', 'uuid', 'following', 'follower', 'user_image']

    def get_user_profile_img(self, profile):
        user_id = profile.uuid
        user_image = UserImages.objects.filter(user=user_id)
        if len(user_image) > 0:
            user_img = user_image[0]
            user_img_serializer = UserImageSerializer(user_img)

            return user_img_serializer.data
        else:
            return {}

    def get_all_following_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Following User
        following_list = UserContacts.objects.values('follower').filter(following=user_id)

        # Return Data
        return following_list

    def get_all_follower_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Follower User
        follower_list = UserContacts.objects.values('following').filter(follower=user_id)

        # Return Data
        return follower_list


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')
    # user_age = serializers.SerializerMethodField('get_user_age')
    # interest = serializers.SerializerMethodField('get_interest')
    follower = serializers.SerializerMethodField('get_all_follower_list')
    images = serializers.SerializerMethodField('get_user_profile_img')
    # desirable_score = serializers.SerializerMethodField('get_desirable_score')
    # work_as = serializers.SerializerMethodField('get_work_as')
    username = serializers.SerializerMethodField('get_user_name')
    followed_by = serializers.SerializerMethodField('get_followed_by')

    class Meta:
        model = User

        # fields = ['id', 'full_name', 'user_age', 'username', 'interest', 'work_as', 'follower', 'images',
        #           'desirable_score','followed_by']

        fields = ['id', 'full_name', 'username', 'follower', 'images', 'followed_by']

        read_only_fields = fields

    def get_user_name(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.username

    def get_full_name(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.full_name

    def get_user_age(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.user_age

    def get_work_as(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.work_as

    def get_interest(self, user):
        qs = self.context.get("queryset")
        for uid in qs:
            if user == uid:
                interest_list = [interest.interest_name for interest in uid.user_profile.interest.all()]
                return interest_list
        interest_list = [interest.interest_name for interest in qs[user.id].user_profile.interest.all()]
        return interest_list

    def get_all_follower_list(self, user):
        # Return Data
        qs = self.context.get("queryset")
        return qs[user.id].user_follower.count()

    def get_user_profile_img(self, user):
        qs = self.context.get("queryset")
        # user_image = qs[user.id].user_profile_image
        # user_img_serializer = UserImageSerializer(user_image, many=True)
        # return user_img_serializer.data
        try:
            user_image = qs[user.id].display_pic
            user_img_serializer = DisplayPictureSerializer(user_image)
            return [user_img_serializer.data]
        except ObjectDoesNotExist:
            return []

    def get_following_status(self, user):
        return False

    def get_desirable_score(self, user):
        # Get Potential User Profile
        qs = self.context.get("queryset")

        potential_user_id = qs[user.id]

        # Get Deriable Score
        potential_score = potential_user_id.score.desirable_score

        # Get Requested User ID
        request_user_profile = self.context.get("user_id")

        # Calculate Age Difference
        age_difference = abs(potential_user_id.user_profile.user_age - request_user_profile.user_profile.user_age)
        if age_difference == 0 or age_difference == 1:
            potential_score += 6.4
        else:
            potential_score += 6.4 / age_difference

        for interest in potential_user_id.user_profile.interest.all():
            if interest in request_user_profile.user_profile.interest.all():
                potential_score += 6.4

        #new change
        # Calculate Distance

        # Get Requested User Location
        request_user_location = UserLocation.objects.get(
                    user=request_user_profile).last_location

        # Get Potential User Location DIstance
        for location in UserLocation.objects.filter(user=potential_user_id).annotate(
                        distance=Distance('last_location', request_user_location)):

            # User Distance
            potential_user_distance = location.distance.km
            if potential_user_distance == 0 or potential_user_distance == 1:
                potential_score += 32
            else:
                potential_score += 32 / potential_user_distance

        # # Calculate Distance
        # potential_user_distance = potential_user_id.geo_location.last_location.distance(
        #     request_user_profile.geo_location.last_location) * 100
        #
        # if potential_user_distance == 0 or potential_user_distance == 1:
        #     potential_score += 32
        # else:
        #     potential_score += 32 / potential_user_distance

        return potential_score

    def get_followed_by(self, user):
        qs = self.context.get("queryset")
        current_user = self.context.get("user_id")
        username = ""

        current_user_follower = UserContacts.objects.filter(following=current_user.id).values_list("follower",flat=True)
        user_follower = UserContacts.objects.filter(follower=qs[user.id]).values_list('following',flat=True)


        # if user_follower and current_user_follower:
        if user_follower:
            follower_id = user_follower[0]
            # current_user_follower_id = current_user_follower[0]["follower"]
            # if follower_id == current_user_follower_id:
            #     profile = ProfileDetails.objects.get(uuid=follower_id)
            #     username = profile.username

            profile = ProfileDetails.objects.get(uuid=follower_id)
            username = profile.username
        return username


class UserSearchSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField('get_full_name')
    user_age = serializers.SerializerMethodField('get_user_age')
    interest = serializers.SerializerMethodField('get_interest')
    follower = serializers.SerializerMethodField('get_all_follower_list')
    images = serializers.SerializerMethodField('get_user_profile_img')
    work_as = serializers.SerializerMethodField('get_work_as')
    username = serializers.SerializerMethodField('get_user_name')

    class Meta:
        model = User
        fields = ['id', 'full_name', 'user_age', 'work_as', 'interest', 'follower', 'images', 'username']

        read_only_fields = fields

    def get_full_name(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.full_name

    def get_user_name(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.username

    def get_user_age(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.user_age

    def get_work_as(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.work_as

    def get_interest(self, user):
        qs = self.context.get("queryset")
        for uid in qs:
            if user == uid:
                interest_list = [interest.interest_name for interest in uid.user_profile.interest.all()]
                return interest_list
        interest_list = [interest.interest_name for interest in qs[user.id].user_profile.interest.all()]
        return interest_list

    def get_all_follower_list(self, user):
        # Return Data
        qs = self.context.get("queryset")
        return qs[user.id].user_follower.count()

    def get_user_profile_img(self, user):
        qs = self.context.get("queryset")
        # user_image = qs[user.id].user_profile_image
        # user_img_serializer = UserImageSerializer(user_image, many=True)
        # return user_img_serializer.data
        try:
            user_image = qs[user.id].display_pic
            user_img_serializer = DisplayPictureSerializer(user_image)
            return [user_img_serializer.data]
        except ObjectDoesNotExist:
            return []


# class CloseFriendSearchSerializer(serializers.ModelSerializer):
class CloseFriendSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField('get_full_name',read_only=True)
    # user_age = serializers.SerializerMethodField('get_user_age')
    # interest = serializers.SerializerMethodField('get_interest')
    # follower = serializers.SerializerMethodField('get_all_follower_list')
    images = serializers.SerializerMethodField('get_user_profile_img',read_only=True)
    # work_as = serializers.SerializerMethodField('get_work_as')
    username = serializers.SerializerMethodField('get_user_name',read_only=True)

    class Meta:
        model = User
        # fields = ['id', 'full_name', 'images', 'username']  # 'user_age','work_as','interest','follower','images']
        #
        # read_only_fields = fields

    def get_full_name(self, user):
        qs = self.context.get("queryset")
        print("qs", qs, qs[user.id])
        # print("qs", qs)
        # print("qs[user.id].user_profile.full_name", qs[user.id], type(qs), qs)#.user_profile.full_name)
        # user =
        user_profile = ProfileDetails.objects.get(uuid=User.objects.get(username=qs[user.id]))
        # for key, val in qs.items():
        # print("user full name", user.user_profile.full_name)
        # return qs[user.id].user_profile.full_name
        return user_profile.full_name

    def get_user_name(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.username

    def get_user_age(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.user_age

    def get_work_as(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.work_as

    def get_interest(self, user):
        qs = self.context.get("queryset")
        for uid in qs:
            if user == uid:
                interest_list = [interest.interest_name for interest in uid.user_profile.interest.all()]
                return interest_list
        interest_list = [interest.interest_name for interest in qs[user.id].user_profile.interest.all()]
        return interest_list

    def get_all_follower_list(self, user):
        # Return Data
        qs = self.context.get("queryset")
        return qs[user.id].user_follower.count()

    def get_user_profile_img(self, user):
        qs = self.context.get("queryset")
        # current_user = User.objects.get(username = qs[user.id])
        # print("current_usere", current_user)
        # user_image = current_user.user_profile_image
        # print("user_image", user_image)
        # user_img_serializer = UserImageSerializer(user_image, many=True)
        # return user_img_serializer.data
        try:
            # user_image = current_user.user_profile_image
            # user_image = qs[user.id].display_pic
            # user_img_serializer = DisplayPictureSerializer(user_image)
            # return [user_img_serializer.data]
            current_user = User.objects.get(username=qs[user.id])
            user_image = current_user.display_pic
            user_img_serializer = DisplayPictureSerializer(user_image)
            print("user_img_serializer", user_img_serializer)
            return [user_img_serializer.data]
        except ObjectDoesNotExist:
            return []


# class InterestedUserProfile(serializers.ModelSerializer):
class InterestedUserProfile(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField('get_full_name',read_only=True)
    user_age = serializers.SerializerMethodField('get_user_age',read_only=True)
    follower = serializers.SerializerMethodField('get_all_follower_list',read_only=True)
    images = serializers.SerializerMethodField('get_user_profile_img',read_only=True)
    username = serializers.SerializerMethodField('get_user_name',read_only=True)
    is_close_friend = serializers.SerializerMethodField('get_close_friend_flag',read_only=True)

    class Meta:
        model = User
        # fields = ['id', 'full_name', 'user_age', 'follower', 'images', 'username','is_close_friend']

    def get_full_name(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.full_name

    def get_user_name(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.username

    def get_user_age(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.user_age

    def get_all_follower_list(self, user):
        # Return Data
        qs = self.context.get("queryset")
        return qs[user.id].user_follower.count()

    def get_user_profile_img(self, user):
        qs = self.context.get("queryset")
        try:
            user_image = qs[user.id].display_pic
            user_img_serializer = DisplayPictureSerializer(user_image)
            return [user_img_serializer.data]
        except ObjectDoesNotExist:
            return []

    def get_close_friend_flag(self,user):
        close_friend = self.context.get("close_friend")
        if close_friend:
            if user.id in close_friend:
                return True
        return False


# class FollowerSerializer(serializers.ModelSerializer):
class FollowerSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField('get_full_name',read_only=True)
    user_age = serializers.SerializerMethodField('get_user_age',read_only=True)
    images = serializers.SerializerMethodField('get_user_profile_img',read_only=True)
    is_following = serializers.SerializerMethodField('get_following_flag',read_only=True)
    username = serializers.SerializerMethodField('get_user_name',read_only=True)

    class Meta:
        model = User
        # fields = ['id', 'full_name', 'user_age', 'is_following', 'images', 'username']

    def get_full_name(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.full_name

    def get_user_name(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.username

    def get_user_age(self, user):
        qs = self.context.get("queryset")
        return qs[user.id].user_profile.user_age

    def get_following_flag(self, user):
        user_following = self.context.get("user_following")
        if user in user_following:
            return True
        return False

    def get_user_profile_img(self, user):
        qs = self.context.get("queryset")
        try:
            user_image = qs[user.id].display_pic
            return user_image.images.url
        except ObjectDoesNotExist:
            return ""


# class InviteFriendsSerializer(serializers.ModelSerializer):
class InviteFriendsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    contact_name = serializers.CharField(read_only=True)
    contact_number = serializers.CharField(read_only=True)

    class Meta:
        model = UsersContacts
        fields = ['id', 'contact_name', 'contact_number']


class SuggesstedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggesstedUser
        fields = '__all__'
