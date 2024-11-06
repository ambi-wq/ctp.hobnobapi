from django.contrib.auth import get_user_model
from .serializers import ProfileSerializer, InterestSerializer, UserInterestSerializer, UserImageSerializer, UserPreferenceSerializer, InstagramSerializer, PromptQuestionsSerializer, ReplaceQuestionSerializer, DowntoChillSerializer
from .serializers import OtherUserProfileSerializer, SpotifySerializer, ProfileDataSerializer, DisplayPictureSerializer, UserPromptQASerializer, UserCreatePromptQASerializer, ContactSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import ProfileDetails, Interest, UserImages, UserPreference, InstagramConnect, SpotifyConnect, DisplayPicture, UserPromptQA, PromptQuestions, UserContactList, UsersContacts
from matching.models import UserContacts, UserScore, UserLocation, CloseFriendList
from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from firebase_admin import auth
from firebase_admin import credentials
import firebase_admin
from rest_framework import generics
from rest_framework import views
from django.conf import settings
import requests
import time
import json
from django.core.exceptions import ValidationError
from matching.models import UserLocation
from events.models import Events
from matching.serializers import LocationSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.renderers import JSONRenderer
from hobnob.standard_response import success_response, error_response
from rest_framework.exceptions import NotFound, ValidationError, NotAcceptable, PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
import datetime
from django.db.models import Q
# Create your views here.

@api_view(['POST'],)
def create_profile(request):
    user = request.user

    profile_count = ProfileDetails.objects.filter(uuid=user).exists()
    print("profile_count", profile_count)

    if profile_count:
        profile = ProfileDetails.objects.get(uuid=user)
        profile_serializer = ProfileSerializer(profile)
        if request.version == 'v1':
            standard_response = success_response(profile_serializer.data)
            return Response(standard_response, status=status.HTTP_200_OK)
        else:
            return Response(profile_serializer.data, status=status.HTTP_200_OK)
    else:
        profile = ProfileDetails(uuid=user)
        profile_serializer = ProfileSerializer(profile, data=request.data)
        if profile_serializer.is_valid():
            profile_serializer.save()

            if request.version == 'v1':
                standard_response = success_response(profile_serializer.data)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(profile_serializer.data, status=status.HTTP_200_OK)
        else:
            if request.version == 'v1':
                standard_response = error_response(profile_serializer.errors)
                return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'],)
def create_spotify(request):
    user = request.user
    if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
        # profile_count = ProfileDetails.objects.filter(uuid=user).exists()
        is_account_connected = SpotifyConnect.objects.filter(
                user=user).exists()
        if not is_account_connected:
            try:
                refresh_token = request.data['refresh_token']
                access_token = request.data['access_token']
            except:
                return Response(data={"message": "Access Token or Refresh Token or Both are missing"}, status=status.HTTP_400_BAD_REQUEST)        
            # Pass Spotify Instance for Serialization
            spotify_connect = SpotifyConnect.objects.create(
                user=user, refresh_token=refresh_token, access_token=access_token)
            profile = ProfileDetails.objects.get(uuid=user)
            profile.spotify_connected = True
            profile.save()
            # Serializer Data
            spotify_serializer = SpotifySerializer(spotify_connect)
            if request.version == 'v1':
                standard_response = success_response(spotify_serializer.data)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(spotify_serializer.data, status=status.HTTP_200_OK)
        else:
            # Error Msg
            error_msg = {"message": "Spotify Account Already Connected"}
            if request.version == 'v1':
                standard_response = error_response(error_msg['message'])
                return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data=error_msg, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message: user account is deleted"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'],)
def get_profile_details(request):
    user = request.user
    print("user", user)
    if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
        try:
            profile = ProfileDetails.objects.get(uuid=user)
            profile_serializer = ProfileDataSerializer(profile)
            if request.version == 'v1':
                standard_response = success_response(profile_serializer.data)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(profile_serializer.data, status=status.HTTP_200_OK)
        except ProfileDetails.DoesNotExist:
            raise NotFound(detail="User Profile doesn't exist")
    else:
        return Response({"message: user account is deleted"}, status=status.HTTP_400_BAD_REQUEST)



class DowntoChillList(generics.ListAPIView):
    serializer_class = DowntoChillSerializer

    def get_queryset(self):
        """
        This view should return a list of all the available users
        """
        user = self.request.user
        print("user", user) 
        following_list = CloseFriendList.objects.values_list(
            'close_friend', flat=True).filter(user=user)
        print("following_list", following_list)
        return ProfileDetails.objects.filter(~Q(uuid=user), is_available=True).exclude(~Q(uuid__in=following_list))


@api_view(['DELETE'],)
def delete_profile(request):
    user = request.user
    print("user", user)
    if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
        try:
            if len(Events.objects.filter(user = user, event_date__gte=datetime.date.today())) == 0:
                profile = ProfileDetails.objects.get(uuid=user)
                profile.active = False
                profile.username = ""
                profile.save()
                success_msg = {"message": "Profile Deleted Successfully"}
                standard_response = success_response(success_msg)

                if request.version == 'v1':
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response({"message: Got Some issue while deleting account"}, status=status.HTTP_400_BAD_REQUEST)                
        except ProfileDetails.DoesNotExist:
            raise NotFound(detail="User Profile doesn't exist")
    else:
        return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'],)
def update_profile(request):
    # Get User
    user = request.user
    if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
        try:
            # Load User Profile
            profile = ProfileDetails.objects.get(uuid=user)

            # Load Serializer and Pass Updated Data
            profile_serializer = ProfileSerializer(
                profile, data=request.data, partial=True)

            # Check validation of data
            if profile_serializer.is_valid():
                # if data is valid then Save Data
                profile_serializer.save()

                # Response
                if request.version == 'v1':
                    standard_response = success_response(profile_serializer.data)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(profile_serializer.data, status=status.HTTP_200_OK)
            else:
                # If data is invalid, send invalid response
                if request.version == 'v1':
                    standard_response = error_response(profile_serializer.errors)
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="User Profile doesn't exist")
    else:
        return Response({"message: user account is deleted"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'],)
def get_top_artists(request):
    # try:
    # user = request.user
    # token = request.data['token']
    # print("token", token)
    # url = "https://api.spotify.com/v1/me/top/artists"
    # headers = {'Authorization' : 'Bearer ' + token }
    # r = requests.get(url, headers=headers)
    # print(r.text, type(r.text))
    # standard_response = success_response(json.loads(r.text)
    # print("standard_response", standard_response)
    return Response(standard_response, status=status.HTTP_200_OK)
    # except as e:
    #     raise NotFound(detail=e)


@api_view(['PUT'],)
def add_user_interest(request):
    if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
        try:
            user = request.user
            profile_detail = ProfileDetails.objects.get(uuid=user)

            # Check User Interest
            interest_set = set(request.data['interest'])
            interest_list = list(interest_set)

            if len(interest_list) == 5:
                user_interest_serializer = UserInterestSerializer(
                    profile_detail, data=request.data)
                if user_interest_serializer.is_valid():
                    user_interest_serializer.save()

                    # Response
                    if request.version == 'v1':
                        standard_response = success_response(
                            user_interest_serializer.data)
                        return Response(standard_response, status=status.HTTP_200_OK)
                    else:
                        return Response(user_interest_serializer.data, status=status.HTTP_200_OK)
                else:
                    if request.version == 'v1':
                        standard_response = error_response(
                            user_interest_serializer.errors)
                        return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(user_interest_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            elif len(interest_list) < 5:
                error_msg = {"message": "You should add minimum 5 unique interest"}
                if request.version == 'v1':
                    standard_response = error_response(error_msg['message'])
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

            elif len(interest_list) > 5:
                error_msg = {"message": "You can only add 5 unique interest"}
                if request.version == 'v1':
                    standard_response = error_response(error_msg['message'])
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="User Profile doesn't exist")
    else:
        return Response({"message: user account is deleted"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileUsername(views.APIView):

    def get(self, request, username):
        # Make query to check if username exists or not
        is_username_exist = ProfileDetails.objects.filter(
            username=username).exists()

        # If Exist
        if is_username_exist:
            standard_response = success_response({"available": False})
            return Response(standard_response, status=status.HTTP_200_OK)
        else:
            standard_response = success_response({"available": True})
            return Response(standard_response, status=status.HTTP_200_OK)

class InterestCollection(views.APIView):

    # Setting cache time out for 1 Days
    @method_decorator(cache_page(60*60*24))
    def get(self, request):
        interests = Interest.objects.all()
        interests_serializer = InterestSerializer(interests, many=True)
        if request.version == 'v1':
            standard_response = success_response(
                interests_serializer.data, is_array=True)
            return Response(standard_response, status=status.HTTP_200_OK)
        else:
            return Response(interests_serializer.data, status=status.HTTP_200_OK)

class UserProfileImages(views.APIView):

    # Setting cache time out for 1 Horus
    # @method_decorator(cache_page(60*60))
    def get(self, request):
        user = request.user
        user_image = UserImages.objects.filter(user=user)
        user_img_serializer = UserImageSerializer(user_image, many=True)
        if request.version == 'v1':
            standard_response = success_response(
                user_img_serializer.data, is_array=True)
            return Response(standard_response, status=status.HTTP_200_OK)
        else:
            return Response(user_img_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        print("uploading image")
        user = request.user
        user_image = UserImages(user=user)
        user_img_serializer = UserImageSerializer(
            user_image, data=request.data)
        if user_img_serializer.is_valid():
            user_img_serializer.save()
            if request.version == 'v1':
                standard_response = success_response(user_img_serializer.data)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(user_img_serializer.data, status=status.HTTP_200_OK)
        else:
            if request.version == 'v1':
                standard_response = error_response(user_img_serializer.errors)
                return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(user_img_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            user_image = UserImages.objects.get(pk=id)
            user_image.delete()
            success_msg = {"message": "Image Deleted Successfully"}
            if request.version == 'v1':
                standard_response = success_response(success_msg)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(success_msg, status=status.HTTP_200_OK)
        except UserImages.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Image doesn't exist")
            else:
                return Response({"message": "Image doesn't exist"}, status=status.HTTP_404_NOT_FOUND)


class UserPreferenceView(views.APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = request.user
        try:
            user_pref = UserPreference.objects.values(
                'id', 'user', 'opposite_gender', 'min_age', 'max_age', 'radius').get(user=user)

            user_location = UserLocation.objects.values(
                'last_location', 'place').get(user=user)

            location_serializer = LocationSerializer(user_location)

            user_pref.update(location_serializer.data)

            if request.version == 'v1':
                standard_response = success_response(user_pref)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(user_pref, status=status.HTTP_200_OK)
        except UserPreference.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="User Preference doesn't exist")
            else:
                return Response({"message": "User Preference doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            user = request.user
            pref_exist = UserPreference.objects.filter(user=user).count()
            if pref_exist == 0:
                user_pref = UserPreference(user=user)
                user_pref_serializer = UserPreferenceSerializer(
                    user_pref, data=request.data)
                if user_pref_serializer.is_valid():
                    user_pref_serializer.save()

                    if request.version == 'v1':
                        standard_response = success_response(
                            user_pref_serializer.data)
                        return Response(standard_response, status=status.HTTP_201_CREATED)
                    else:
                        return Response(user_pref_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    if request.version == 'v1':
                        standard_response = error_response(
                            user_pref_serializer.errors)
                        return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(user_pref_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                if request.version == 'v1':
                    raise NotAcceptable(
                        detail="User Preference already exist. Please use update method for update.")
                else:
                    return Response({"message": "User Preference already exist. Please use update method for update."}, status=status.HTTP_406_NOT_ACCEPTABLE)

        except ValidationError:
            msg = {"message": "Maximum age should be greater than minimum age"}
            if request.version == 'v1':
                standard_response = error_response(msg['message'])
                return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user
        try:
            user_pref = UserPreference.objects.get(user=user)
            user_pref_serializer = UserPreferenceSerializer(
                user_pref, data=request.data, partial=True)
            if user_pref_serializer.is_valid():
                user_pref_serializer.save()
                if request.version == 'v1':
                    standard_response = success_response(
                        user_pref_serializer.data)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(user_pref_serializer.data, status=status.HTTP_200_OK)
            else:
                if request.version == 'v1':
                    standard_response = error_response(
                        user_pref_serializer.errors)
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(user_pref_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserPreference.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="User Preference doesn't exist.")
            else:
                return Response({"message": "User Preference doesn't exist."}, status=status.HTTP_404_NOT_FOUND)


class InstagramView(views.APIView):

    # Setting cache time out for 1 Days
    @method_decorator(cache_page(60*60*24))
    def get(self, request):
        user = request.user
        instagram_user = InstagramConnect.objects.filter(user=user)
        if instagram_user.count() > 0:
            user_data = instagram_user[0]
            # Check User Token is expired or not
            today = int(time.time())
            if today >= int(user_data.token_expiry):
                url = "{root_url}/refresh_access_token?grant_type=ig_refresh_token&access_token={access_token}".format(
                    root_url=settings.INSTAGRAM_ROOT_URL, access_token=user_data.access_token)

                response = requests.request("GET", url)
                response = response.json()

                long_live_token = response['access_token']
                expires_in = response['expires_in']
                timestamp = time.time()
                expires_date = int(timestamp) + expires_in

                user_data.access_token = long_live_token
                user_data.token_expiry = expires_date
                user_data.save()

            url = "{root_url}/{insta_id}/media?fields=id,username,media_url&access_token={access_token}".format(
                root_url=settings.INSTAGRAM_ROOT_URL, insta_id=user_data.instagram_id, access_token=user_data.access_token)

            response = requests.request("GET", url)
            response = response.json()
            if request.version == 'v1':
                standard_response = success_response(response)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(response, status=status.HTTP_200_OK)
        else:
            if request.version == 'v1':
                raise NotFound(detail="User has not connected Instagram")
            else:
                return Response({"message": "User has not connected Instagram"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):

        user = request.user
        insta_count = InstagramConnect.objects.filter(user=user).count()

        if 'code' in request.data:

            # Get Short Live Access Token
            short_token_url = "https://api.instagram.com/oauth/access_token"

            payload = {'client_id': '576239349748743',
                       'client_secret': 'da33e01ca729c6f2cdde17faa968a56b',
                       'grant_type': 'authorization_code',
                       'redirect_uri': 'https://httpstat.us/200',
                       'code': request.data['code']
                       }
            response = requests.request("POST", short_token_url, data=payload)

            if response.status_code == 400:
                response = response.json()
                if request.version == 'v1':
                    standard_response = error_response(response)
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                response = response.json()
                instagram_id = response['user_id']
                short_live_token = response['access_token']

                # Get Long Live Token
                url = "{root_url}/access_token?client_secret={app_secret}&access_token={short_token}&grant_type=ig_exchange_token".format(
                    root_url=settings.INSTAGRAM_ROOT_URL, app_secret=settings.INSTA_APP_SECRET, short_token=short_live_token)

                response = requests.get(url)
                response = response.json()

                long_live_token = response['access_token']
                expires_in = response['expires_in']
                timestamp = time.time()
                expires_date = int(timestamp) + expires_in

                # Store Access Data
                if insta_count == 0:
                    instagram_user = InstagramConnect(
                        user=user, instagram_id=instagram_id, access_token=long_live_token, token_expiry=expires_date)
                    instagram_user.save()

                    # Success Msg
                    success_msg = {"message": "Instagram User Added"}
                    if request.version == 'v1':
                        standard_response = success_response(success_msg)
                        return Response(standard_response, status=status.HTTP_200_OK)
                    else:
                        return Response(success_msg, status=status.HTTP_201_CREATED)
                else:

                    # Update Msg
                    update_msg = {"message": "Instagram User Updated"}

                    instagram_user = InstagramConnect.objects.get(user=user)
                    instagram_user.instagram_id = instagram_id
                    instagram_user.access_token = long_live_token
                    instagram_user.token_expiry = expires_date
                    instagram_user.save()
                    if request.version == 'v1':
                        standard_response = success_response(update_msg)
                        return Response(standard_response, status=status.HTTP_200_OK)
                    else:
                        return Response(update_msg, status=status.HTTP_200_OK)
        else:
            # Bad Msg
            bad_msg = {"message": "You must pass code from instagram"}

            if request.version == 'v1':
                standard_response = error_response(bad_msg['message'])
                return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(bad_msg, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Get User
        user = request.user
        try:
            # Try to find User
            instagram_user = InstagramConnect.objects.get(user=user)

            # Delete User Instace
            instagram_user.delete()

            # Success Msg
            success_msg = {"message": "Instagram disconnected successfully"}

            if request.version == 'v1':
                response = success_msg(success_msg['message'])
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(success_msg, status=status.HTTP_200_OK)
        except InstagramConnect.DoesNotExist as e:
            raise ValidationError(detail="User has not connected Instagram")


class UserProfileView(views.APIView):

    def get(self, request, id):

        profile_count = ProfileDetails.objects.filter(uuid=id).count()

        try:
            profile = ProfileDetails.objects.get(uuid=id)
            profile_serializer = OtherUserProfileSerializer(
                profile, context={'user_id': request.user})
            if request.version == 'v1':
                standard_response = success_response(profile_serializer.data)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(profile_serializer.data, status=status.HTTP_200_OK)
        except ProfileDetails.DoesNotExist:
            raise NotFound(detail="User Profile doesn't exist")


class SpotifyView(views.APIView):

    def get(self, request):
        # Get User
        current_user = request.user

        try:
            # Check Token exist
            spotify_connect = SpotifyConnect.objects.get(user=current_user)
            print("spotify Connected", spotify_connect)

            # Connect timestamp
            last_connect = spotify_connect.update_at.timestamp()
            print("last_connect", last_connect)

            # Check Token Expiry
            # if (int(time.time()) - int(last_connect)) < 3600:
            #     # Get Access Token
            #     access_token = spotify_connect.access_token
            #     print("access_token", access_token)
            #     # access_token = "BQDOTwleqOMQ8x7JgEEckwiG7oQDl9JZflBAvDh7nUFZFlvbJTTeCXqZJd9dRP7R3aQ2CEArtxenW91ZFn9OLN340vZzViFHkh7Ca69umuU4OS9SFcfg3pO1NfhqN_wA7KkC_fCPLnM5SSEhGoT_mI9I139jxRODyVJcHA3Td-o6vYM6-FzvzskEs3B_Cfw"
  
            #     # Call Artist API
            #     artist_response, arttist_status_code = self.get_spotify_artist(
            #         access_token)
            #     print("artist_response", artist_response)
            #     print("arttist_status_code", arttist_status_code)

            #     # Get Response Data
            #     data = artist_response

            #     # Check Status Code
            #     if arttist_status_code == 200:
            #         # Send Response Back
            #         return Response(data, status=arttist_status_code)

            #     else:
            #         return Response(data, status=arttist_status_code)

            # # Token Expiry
            # else:
                # Get Refresh Token
            refresh_token = spotify_connect.refresh_token
            print("refresh_token", refresh_token)
            # refresh_token = "AQCuig0J5oitFB2F15Wu9VEEi5OrysGyGSG5LD__sis3sRlpxaeOnRmkL0zoqM1I9A5YQbvuYDOAhs1cjlxPWgHU7b43vLn00X3RocDD11aO_CRTzI1gYBRCIK6ksKzFkK0"

            authroisation_url = settings.SPOTIFY_ROOT_URL + '/api/token'

            print("authroisation_url", authroisation_url)

            # Call API for Access Token
            response, status_code = self.spotify_helper(
                authroisation_url, 'refresh_token', refresh_token)
            print("response, status_code", response, status_code)
            if status_code == 200:
                print("status code 200")
                # Get Access Token
                access_token = response['access_token']
                print("access_token", access_token)

                # Update Access Token in MOdel
                spotify_connect.access_token = access_token
                print("spotify connected with new access token")

                # Save Access Token
                spotify_connect.save()


                # Call Artist API
                artist_response, arttist_status_code = self.get_spotify_artist(
                    access_token)
                print("arttist_status_code", arttist_status_code)

                # Call Album API
                # album_response, album_status_code = self.get_spotify_album(
                #     access_token)

                # Get Response Data
                data = artist_response
                print("data", data, type(data), dir(data))

                # Check Status Code
                if arttist_status_code == 200:
                    # Send Response Back
                    return Response(data, status=arttist_status_code)

                else:
                    return Response(data, status=arttist_status_code)

            else:
                return Response(response, status=status_code)

            # Token Not Not Expire
        except SpotifyConnect.DoesNotExist:
            return Response(data={"message": "Spotify Account not Connected"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        # Get User
        current_user = request.user

        # Check Token Already Exist
        is_account_connected = SpotifyConnect.objects.filter(
            user=current_user).exists()

        # Try Get Code
        try:
            # Get Spotify Authorization Code
            code = request.data['code']
        except:
            return Response(data={"message": "Send Authorise Code"}, status=status.HTTP_400_BAD_REQUEST)

        if not is_account_connected:
            # Make request to Spotify Server to get Refresh & Access Token
            authroisation_url = settings.SPOTIFY_ROOT_URL + '/api/token'
            response, status_code = self.spotify_helper(
                authroisation_url, 'authorization_code', code)
            print("response, status_code", response, status_code)
 
            # Check Status Code is 200
            if status_code == 200:
                # Store Refresh & Access Token in User Model
                refresh_token = response['refresh_token']
                access_token = response['access_token']

                # Pass Spotify Instance for Serialization
                spotify_connect = SpotifyConnect.objects.create(
                    user=current_user, refresh_token=refresh_token, access_token=access_token)

                # Serializer Data
                spotify_serializer = SpotifySerializer(spotify_connect)

                # Return Data
                if request.version == 'v1':
                    standard_response = success_response(
                        spotify_serializer.data)
                    return Response(standard_response, status=status.HTTP_201_CREATED)
                else:
                    return Response(spotify_serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Status Code Other than 200, return Erro
                return Response(data=response, status=status_code)
        else:
            # Error Msg
            error_msg = {"message": "Spotify Account Already Connected"}
            if request.version == 'v1':
                standard_response = error_response(error_msg['message'])
                return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data=error_msg, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # Get User
        user = request.user
        try:
            # Try to find User
            spotify_user = SpotifyConnect.objects.get(user=user)

            # Delete User Instace
            spotify_user.delete()

            # Success Msg
            success_msg = {"message": "Spotify disconnected successfully"}

            if request.version == 'v1':
                response = success_response(success_msg['message'])
                return Response(data=response, status=status.HTTP_200_OK)
            else:
                return Response(success_msg, status=status.HTTP_200_OK)
        except SpotifyConnect.DoesNotExist as e:
            raise NotFound(detail="User has not connected Spotify")

    def spotify_helper(self, url, grant_type, token_or_code):
        # Payload
        print("url", url)
        print("grand_type", grant_type)
        print("token", token_or_code)
        # payload = 'grant_type={0}&code={1}&redirect_uri={2}&client_id={3}&client_secret={4}'.format(
        #     grant_type, token_or_code, 'http://httpstat.us/200', settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)

        if grant_type == 'authorization_code':
            print("entered if")
            payload = 'grant_type={0}&code={1}&redirect_uri={2}&client_id={3}&client_secret={4}'.format(
                grant_type, token_or_code, 'https://api.hobnobco.com/', settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
        else:
            payload = 'grant_type={0}&refresh_token={1}&redirect_uri={2}&client_id={3}&client_secret={4}'.format(
                grant_type, token_or_code, 'https://api.hobnobco.com/', settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
        print("payload", payload)
        # Make Requests
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json(), response.status_code

    def get_spotify_artist(self, access_token):
        # Spotify URL
        artist_url = "https://api.spotify.com/v1/me/top/artists"
        print("artist_url", artist_url)
        #artist_url = "https://api.spotify.com/v1/artists"

        # Token
        token = 'Bearer ' + access_token
        print("token", token)

        # Header
        headers = {'Authorization': token}

        # Make Get Request to get Artist User Like
        response = requests.request("GET", artist_url, headers=headers)
        print("response",response, type(response), dir(response))

        return response.json(), response.status_code

    def get_spotify_album(self, access_token):
        # Spotify URL
        album_url = "https://api.spotify.com/v1/me/albums"

        # Token
        token = 'Bearer ' + access_token

        # Header
        headers = {'Authorization': token}

        # Make Get Request to get Artist User Like
        response = requests.request("GET", album_url, headers=headers)

        return response.json(), response.status_code


class DisplayPictureView(views.APIView):

    # Setting cache time out for 1 Horus
    def get(self, request):
        user = request.user
        user_image = DisplayPicture.objects.filter(user=user)
        user_img_serializer = DisplayPictureSerializer(user_image, many=True)
        standard_response = success_response(
            user_img_serializer.data, is_array=True)
        return Response(standard_response, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        # Check display picture exist
        is_exist = DisplayPicture.objects.filter(user=user).exists()

        if is_exist:
            # Get Display Picture Object
            display_pic = DisplayPicture.objects.get(user=user)

            # Delete Object
            display_pic.delete()

        user_image = DisplayPicture(user=user)
        user_img_serializer = DisplayPictureSerializer(
            user_image, data=request.data)
        if user_img_serializer.is_valid():
            user_img_serializer.save()
            standard_response = success_response(user_img_serializer.data)
            return Response(standard_response, status=status.HTTP_201_CREATED)
        else:
            standard_response = error_response(user_img_serializer.errors)
            return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            user_image = DisplayPicture.objects.get(pk=id)
            user_image.delete()
            success_msg = {"message": "Display Picture Deleted Successfully"}
            standard_response = success_response(success_msg)
            return Response(standard_response, status=status.HTTP_200_OK)
        except UserImages.DoesNotExist as e:
            raise NotFound(detail="Display Picture doesn't exist")


class UserPromptView(views.APIView):
    # model = UserPromptQA
    # serializer_class = UserPromptQASerializer
    # pagination_class = LimitOffsetPagination
    # renderer_classes = [JSONRenderer]

    def get(self, request):
        # Get User
        current_user = request.user

        # Query QA
        qa_list = UserPromptQA.objects.filter(user=current_user)

        # Serialize Data
        qa_list_serializer = UserPromptQASerializer(qa_list, many=True)

        # Pagination instance
        paginator = LimitOffsetPagination()

        # pagination size
        paginator.size = 20

        # paginate data
        paginated_response = paginator.paginate_queryset(qa_list, request)

        # return data
        return paginator.get_paginated_response(qa_list_serializer.data)

    def post(self, request):
        # Get User
        current_user = request.user
        # CHeck if Question already answ
        is_answer = UserPromptQA.objects.filter(
            question=request.data['question'], user=current_user).exists()

        if not is_answer:
            # Make Query using ID
            prompt_qa = UserPromptQA(user=current_user)

            # Call serializer and pass data
            qa_serializer = UserCreatePromptQASerializer(
                prompt_qa, data=request.data)

            # Check validation
            if qa_serializer.is_valid():
                # Save Data
                qa_serializer.save()

                # Response
                standard_response = success_response(qa_serializer.data)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                standard_response = error_response(qa_serializer.errors)
                return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
        else:
            standard_response = error_response("User already answer")
            return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Get User
        current_user = request.user
        print("request data", request.data)

        try:
            # Make Query using ID
            prompt_qa = UserPromptQA.objects.get(id=request.data['id'])

            # Check QA of same User
            if prompt_qa.user == current_user:
                # Call serializer and pass data
                print("prompt_qa", prompt_qa)
                qa_serializer = UserPromptQASerializer(
                    prompt_qa, data=request.data, partial=True)

                # Check validation
                if qa_serializer.is_valid():
                    # Save Data
                    qa_serializer.save()

                    # Response
                    standard_response = success_response(qa_serializer.data)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    standard_response = error_response(qa_serializer.errors)
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)

            else:
                raise ValidationError(
                    detail="User have no access to this question")

        except UserPromptQA.DoesNotExist:
            raise NotFound(detail="Question not found")
    
    def delete(self, request, id):
        print("id", id)
        prompt_qa = UserPromptQA.objects.get(id=id)
        try:
            prompt_qa.delete()
            success_msg = {"message": "Answer Deleted Successfully"}
            standard_response = success_response(success_msg)
            return Response(standard_response, status=status.HTTP_200_OK)
        except prompt_qa.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Provided Id doesn't exist")
            else:
                return Response({"message": "Provided Id doesn't exist"}, status=status.HTTP_404_NOT_FOUND)


class UserQuestionsListView(views.APIView):
    
    def get(self, request):
        current_user = request.user
        if UserPromptQA.objects.filter(user=current_user).exists():
            having_questions_list = UserPromptQA.objects.filter(user=current_user).values('question')
            print("having questions list", having_questions_list, type(having_questions_list))
            questions_list = PromptQuestions.objects.all().exclude(id__in=having_questions_list)
            print("questions_list", questions_list)
        else:
            questions_list = PromptQuestions.objects.all()
        questoins_list_serializer = PromptQuestionsSerializer(questions_list, many=True)
        paginator = LimitOffsetPagination()
        paginator.size = 20
        paginated_response = paginator.paginate_queryset(questions_list, request)
        return paginator.get_paginated_response(questoins_list_serializer.data)


# class UserQuestionReplaceView(views.APIView):
#     serializer_class = ReplaceQuestionSerializer
#     permission_classes = (IsAuthenticated,)
#     filter_fields = ('question__id','user__id')

#     def get_queryset(self):
#         queryset = UserPromptQA.objects.filter(
#             user__user=self.request.user
#         )

#         return queryset

class UserQuestionReplaceView(views.APIView):
    def put(self, request):
        # Get User
        current_user = request.user

        try:
            # Make Query using ID
            prompt_qa = UserPromptQA.objects.get(id=request.data['id'])

            # Check QA of same User
            if prompt_qa.user == current_user:
                # Call serializer and pass data
                qa_serializer = ReplaceQuestionSerializer(
                    prompt_qa, data=request.data, partial=True)

                # Check validation
                if qa_serializer.is_valid():
                    # Save Data
                    qa_serializer.save()
                    # Response
                    standard_response = success_response(qa_serializer.data)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    standard_response = error_response(qa_serializer.errors)
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)

            else:
                raise ValidationError(
                    detail="User have no access to this question")

        except UserPromptQA.DoesNotExist:
            raise NotFound(detail="Question not found")

# @api_view(['POST'],)
# def add_contacts(request):
#     user = request.user

#     profile_count = ProfileDetails.objects.filter(uuid=user).exists()
#     print("profile_count", profile_count)

#     if profile_count:
#         print("entered into if")
#         profile = ProfileDetails.objects.get(uuid=user)
#         contact_serializer = ContactSerializer(profile)
#         standard_response = success_response(contact_serializer.data)
#         return Response(standard_response, status=status.HTTP_200_OK)


class ContactsView(views.APIView):

    def post(self, request):
        user = request.user
        contacts = UserContactList(user=user)
        current_user = User.objects.get(username = user)
        try:
            start_time = time.time()
            print("start_time = time.time()", start_time)
            contactListRecord = UserContactList.objects.filter(user = current_user)
            if len(contactListRecord)>0:
                get_record = UserContactList.objects.get(user = current_user)
                contacts_records = UsersContacts.objects.filter(user = current_user.id)
                contacts_records._raw_delete(contacts_records.db)
                get_record.delete()
                create_contacts_list = UserContactList.objects.create(user = current_user, contacts_list = request.data['contacts_list'])
                contact_serializer = ContactSerializer(create_contacts_list)
                end = time.time()
                print("endtime", end)
                print("total time",end - start_time)
                # standard_response = success_response(contact_serializer.data)
                success_msg = {"message": "Contacts Updated Successfully"}
                standard_response = success_response(success_msg)
                return Response(standard_response, status=status.HTTP_200_OK)            
            else:
                create_contacts_list = UserContactList.objects.create(user = current_user, contacts_list = request.data['contacts_list'])
                contact_serializer = ContactSerializer(create_contacts_list)
                # standard_response = success_response(contact_serializer.data)
                success_msg = {"message": "Contacts Imported Successfully"}
                standard_response = success_response(success_msg)
                return Response(standard_response, status=status.HTTP_200_OK)
        except Exception as e:            
            raise ValidationError(detail="error : {}; type : {}".format(str(e), type(e)))



# class ContactsView(views.APIView):

#     def post(self, request):
#         user = request.user
#         contacts = UserContactList(user=user)
#         print("data", request.data)
#         current_user = User.objects.get(username = user)
#         # try:
#         contactListRecord = UserContactList.objects.filter(user = current_user)
#         if len(contactListRecord)>0:
#             get_record = UserContactList.objects.get(user = current_user)
#             contacts_records = UsersContacts.objects.filter(user = current_user.id)
#             print("contacts", contacts_records)
#             for contact in contacts_records:
#                 contact.delete()
#             get_record.delete()
#             print("request.data", request.data)
#             contact_serializer = ContactSerializer(contacts, data=request.data)
#             print("contact_serializer", contact_serializer)
#             if contact_serializer.is_valid():
#                 print("before saving")
#                 contact_serializer.save()
#                 print("after saving")
#                 standard_response = success_response(contact_serializer.data)
#                 return Response(standard_response, status=status.HTTP_201_CREATED)
#             else:
#                 standard_response = error_response(contact_serializer.errors)
#                 return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)            
#         else:
#             contact_serializer = ContactSerializer(contacts, data=request.data)
#             if contact_serializer.is_valid():
#                 print("saving data", contact_serializer)
#                 contact_serializer.save()
#                 print("data saved")
#                 standard_response = success_response(contact_serializer.data)
#                 return Response(standard_response, status=status.HTTP_201_CREATED)
#             else:
#                 standard_response = error_response(contact_serializer.errors)
#                 return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
#         # except get_record.DoesNotExist:
#         #     raise NotFound(detail="exception occur")
    # def put(self, request):
    #     current_user = request.user
    #     try:
    #         contactListRecord = UserContactList.objects.get(user = User.objects.get(username = current_user))
    #         print("contactListRecord", contactListRecord)
    #         contact_serializer = ContactSerializer(
    #                 contactListRecord, data=request.data, partial=True)
    #         if contact_serializer.is_valid():
    #             contact_serializer.save()
    #             standard_response = success_response(contact_serializer.data)
    #             return Response(standard_response, status=status.HTTP_200_OK)
    #         else:
    #             standard_response = error_response(contact_serializer.errors)
    #             return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
            # prompt_qa = UserPromptQA.objects.get(id=request.data['id'])
            # # contact_serializer = ContactSerializer(contacts, data=request.data)            
            # if prompt_qa.user == current_user:
            #     qa_serializer = ReplaceQuestionSerializer(
            #         prompt_qa, data=request.data, partial=True)
            #     if qa_serializer.is_valid():
            #         qa_serializer.save()
            #         standard_response = success_response(qa_serializer.data)
            #         return Response(standard_response, status=status.HTTP_200_OK)
            #     else:
            #         standard_response = error_response(qa_serializer.errors)
            #         return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)

            # else:
            #     raise ValidationError(
            #         detail="User have no access to this question")

        # except UserPromptQA.DoesNotExist:
        #     raise NotFound(detail="Question not found")

    # def delete(self, request, id):
    #     try:
    #         user_image = DisplayPicture.objects.get(pk=id)
    #         user_image.delete()
    #         success_msg = {"message": "Display Picture Deleted Successfully"}
    #         standard_response = success_response(success_msg)
    #         return Response(standard_response, status=status.HTTP_200_OK)
    #     except UserImages.DoesNotExist as e:
    #         raise NotFound(detail="Display Picture doesn't exist")