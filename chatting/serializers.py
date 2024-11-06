from rest_framework import serializers
from django.contrib.auth import get_user_model
from userprofile.models import ProfileDetails, DisplayPicture
from chatting.models import Room, Message
from matching.models import UserContacts
from userprofile.serializers import ProfileDetailsSerializer

User = get_user_model()


class RoomSerializer(serializers.ModelSerializer):

    participants = serializers.SerializerMethodField('get_participants')
    
    class Meta:
        model = Room
        fields = ('id', 'participants', 'messages')

    def get_participants(self, room):
        participants = []

        for participant in room.participants.all():
            data = {
                "name": participant.user_profile.full_name,
                "user_id": participant.user_profile.id
            }
            participants.append(data)

        return participants


class ProfileDataSerializer(serializers.ModelSerializer):

    follower = serializers.SerializerMethodField('get_all_follower_list')
    following = serializers.SerializerMethodField('get_all_following_list')
    
    class Meta:
        model = ProfileDetails
        fields = ('id', 'follower', 'following')

    def get_all_follower_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Follower User
        follower_list = UserContacts.objects.filter(
            follower=user_id).values_list('follower__username').order_by('?')[:10]
        if len(follower_list) > 0:
            followerList = []
            for f in follower_list[0]:
                followerData = {}
                if ProfileDetails.objects.get(uuid = User.objects.get(username = f)) != None or ProfileDetails.objects.get(uuid = User.objects.get(username = f)) != "":
                    userInfo = ProfileDetails.objects.get(uuid = User.objects.get(username = f))
                if DisplayPicture.objects.get(user = User.objects.get(username = f)) != None or DisplayPicture.objects.get(user = User.objects.get(username = f)) != "":
                    disp = DisplayPicture.objects.get(user = User.objects.get(username = f))
                followerData['username'] = userInfo.username
                followerData['uid'] = f
                followerData['user_image'] = disp.images.url
                followerList.append(followerData)
            return followerList
        else:
            return []

    def get_all_following_list(self, profile):
        # Get User ID
        user_id = profile.uuid

        # Query to get All Follower User
        following_list = UserContacts.objects.filter(
            following=user_id).values_list('following__username').order_by('?')[:10]
        if len(following_list) > 0:
            followingList = []
            for f in following_list[0]:
                followingData = {}
                userInfo = ProfileDetails.objects.get(uuid = User.objects.get(username = f))
                disp = DisplayPicture.objects.get(user = User.objects.get(username = f))
                followingData['username'] = userInfo.username
                followingData['uid'] = f
                followingData['user_image'] = disp.images.url
                followingList.append(followingData)
            return followingList
        else:
            return []

class RoomListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
