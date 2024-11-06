from rest_framework.response import Response
from rest_framework import views, generics
from matching.models import UserContacts, UserScore, UserLocation, CloseFriendList
from matching.serializers import UserContactsSerializer, UserScoreSerializers, UserFollowerSerializer, UserExploreSerializer, CloseFriendSerializer
from matching.serializers import LocationSerializer, UserSerializer, InterestedUserProfile, FollowerSerializer, UserSearchSerializer, CloseFriendSearchSerializer
from userprofile.models import ProfileDetails, UserPreference, Interest, UsersContacts, UserContactList
from userprofile.serializers import ProfileDetailsSerializer
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from django.contrib.gis.measure import D

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from datetime import datetime
from rest_framework.exceptions import NotFound
from hobnob.standard_response import success_response, error_response

# Create your views here.


class AddFollowerView(views.APIView):
    """Add user to followers list of other user
    """

    def post(self, request):
        # Get User who is following to other user
        following_user = request.user

        # Get Follower User
        follower_user = request.data['follower']

        # Check If User Already Following
        is_exist = UserContacts.objects.filter(
            following=following_user, follower=follower_user).count()

        if is_exist == 0:
            # Create Instant of User following other user
            user_contact = UserContacts(following=following_user)

            # Serialize object of user contact
            serializer = UserContactsSerializer(
                user_contact, data=request.data)

            # Check data pass is valid
            if serializer.is_valid():
                # save data to object if data is valid
                serializer.save()

                # send response back to user
                if request.version == 'v1':
                    response = success_response(serializer.data)
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # if passed data is not valid then send an error with message
                if request.version == 'v1':
                    response = error_response(serializer.errors)
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            error_msg = {"message": "You are already following this user"}
            if request.version == 'v1':
                response = error_response(error_msg['message'])
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        """Method use to unfollow user or remove user from following list
        """
        # Get Requested User
        user = request.user

        try:
            # Get User from Id
            follower_user = User.objects.get(pk=id)

            # Try if connection exist or not
            follower_connection = UserContacts.objects.get(
                following=user, follower=follower_user)

            # Delete Connection
            follower_connection.delete()

            # Response with Succcess Message
            success_msg = {"message": "User unfollowed successfully"}

            if request.version == 'v1':
                response = success_response(success_msg['message'])
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(success_msg, status=status.HTTP_200_OK)

        except UserContacts.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Requested Contact Doesn't Exist")
            else:
                return Response({"message": "Requested Contact Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)

        except User.DoesNotExist as e:
            # If failed then return error message
            if request.version == 'v1':
                raise NotFound(detail="Requested User Doesn't Exist")
            else:
                return Response({"message": "Requested User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)


class FollowerList(generics.ListAPIView):
    model = User
    serializer_class = FollowerSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        # Get Requested User
        user = self.request.user

        # Get Follower List
        follower = UserContacts.objects.values_list(
            'following', flat=True).filter(follower=user)

        # Get Follower User Profile
        profile_list = self.model.objects.filter(pk__in=follower).prefetch_related(
            'user_profile', 'display_pic')

        # return List
        return profile_list

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        current_user = User.objects.filter(
            username=user).prefetch_related('user_following')

        queryset = self.get_queryset()

        queryset_dict = {}
        for qs_data in queryset:
            queryset_dict[qs_data.id] = qs_data

        page = self.paginate_queryset(queryset)

        user_following = []

        for us_follow in user.user_following.all():
            user_following.append(us_follow.follower)

        serializer = self.serializer_class(
            queryset, many=True, context={'queryset': queryset_dict, 'user_following': user_following})

        # Updated Sorted Data
        sorted_data = serializer.data

        return self.get_paginated_response(sorted_data[start_limit:end_limit])
class OtherFollowerList(views.APIView):

    def get(self, request, id):
        try:
            # Get Requested User
            user = User.objects.get(pk=id)
            # Current User
            current_user = request.user
            # Get Follower List
            follower = UserContacts.objects.values_list(
                'following', flat=True).filter(follower=user)
            # Get Follower User Profile
            profile_list = User.objects.filter(pk__in=follower).prefetch_related(
                'user_profile', 'display_pic')

            # Initiate Pagination
            paginator = LimitOffsetPagination()

            # Set Pagination Size
            paginator.page = 20

            # Paginated Query
            result_page = paginator.paginate_queryset(profile_list, request)

            queryset_dict = {}
            for qs_data in profile_list:
                queryset_dict[qs_data.id] = qs_data
                print("queryset_dict[qs_data.id]", queryset_dict[qs_data.id])

            user_following = []

            for us_follow in current_user.user_following.all():
                user_following.append(us_follow.follower)
            print("user_following", user_following)

            # Serializer Data
            serializer = FollowerSerializer(profile_list, many=True, context={
                                            'queryset': queryset_dict, 'user_following': user_following})

            return paginator.get_paginated_response(serializer.data)

        except User.DoesNotExist:
            raise NotFound(detail="User Doesn't Exists")


class FollowingList(generics.ListAPIView):
    model = User
    serializer_class = FollowerSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        # Get Requested User
        user = self.request.user

        # Get following List
        following = UserContacts.objects.values_list(
            'follower', flat=True).filter(following=user)

        # Get Follower User Profile
        profile_list = self.model.objects.filter(pk__in=following).prefetch_related(
            'user_profile', 'display_pic', 'user_follower')

        # return List
        return profile_list

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()

        current_user = User.objects.filter(
            username=user).prefetch_related('user_following')

        queryset_dict = {}
        for qs_data in queryset:
            queryset_dict[qs_data.id] = qs_data

        page = self.paginate_queryset(queryset)

        user_following = []
        for us_follow in user.user_following.all():
            user_following.append(us_follow.follower)

        serializer = self.serializer_class(
            queryset, many=True, context={'queryset': queryset_dict, 'user_following': user_following})

        # Updated Sorted Data
        sorted_data = serializer.data

        return self.get_paginated_response(sorted_data[start_limit:end_limit])


class OtherFollowingList(views.APIView):

    def get(self, request, id):
        try:
            # Get Requested User
            user = User.objects.get(pk=id)

            # Current User
            current_user = request.user

            # Get Follower List
            following = UserContacts.objects.values_list(
                'follower', flat=True).filter(following=user)

            # Get Follower User Profile
            profile_list = User.objects.filter(pk__in=following).prefetch_related(
                'user_profile', 'display_pic')

            # Initiate Pagination
            paginator = LimitOffsetPagination()

            # Set Pagination Size
            paginator.page = 20

            # Paginated Query
            result_page = paginator.paginate_queryset(profile_list, request)

            queryset_dict = {}
            for qs_data in profile_list:
                queryset_dict[qs_data.id] = qs_data

            user_following = []

            for us_follow in current_user.user_following.all():
                user_following.append(us_follow.follower)

            # Serializer Data
            serializer = FollowerSerializer(profile_list, many=True, context={
                                            'queryset': queryset_dict, 'user_following': user_following})

            return paginator.get_paginated_response(serializer.data)

        except User.DoesNotExist:
            raise NotFound(detail="User Doesn't Exists")


class UserSearchView(generics.ListAPIView):
    model = User
    serializer_class = UserSearchSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user_profile__interest__interest_name',
                     'user_profile__full_name', 'user_profile__username']

    def get_queryset(self):

        # Get Requested user
        user = self.request.user

        # Get Current User
        current_user = User.objects.get(username=user)

        # Get Filter User
        try:
            # Check User Interest
            filter_user = User.objects.all().exclude(username=user).order_by('-score__desirable_score', 'geo_location__last_location').prefetch_related('user_profile',
                                                                                                                                                        'user_profile_image', 'display_pic', 'user_profile__interest', 'preference', 'user_follower', 'score', 'geo_location').distinct()

        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="User Profile Not Found")

        except UserLocation.DoesNotExist as e:
            raise NotFound(detail="User Location Not Found")

        except UserPreference.DoesNotExist as e:
            raise NotFound(detail="User Preference Not Found")
        except:
            return []

        return filter_user

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        current_user = User.objects.filter(username=user).prefetch_related(
            'user_profile', 'preference',  'user_profile__interest', 'score', 'geo_location')[0]
        queryset = self.filter_queryset(self.get_queryset())

        queryset_dict = {}
        for qs_data in queryset:
            queryset_dict[qs_data.id] = qs_data

        page = self.paginate_queryset(queryset)

        serializer = UserSearchSerializer(
            queryset, many=True, context={'user_id': current_user, 'queryset': queryset_dict})

        # Updated Sorted Data
        sorted_data = serializer.data

        return self.get_paginated_response(sorted_data[start_limit:end_limit])




class CloseFriendSearchView(generics.ListAPIView):
    model = User
    serializer_class = CloseFriendSearchSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    # search_fields = ['close_friend__user_profile__full_name', 'close_friend__user_profile__username']
    search_fields = ['user_profile__full_name', 'user_profile__username']
                     
    def get_queryset(self):
        # Get Requested user
        user = self.request.user
        print("user", user)
        # Get Current User
        current_user = User.objects.get(username=user)
        # Get Filter User
        try:
            # filter_user = CloseFriendList.objects.filter(user = current_user)
            # print("filter_user", filter_user)
            # Get Follower List
            follower_list = UserContacts.objects.values_list(
                'following', flat=True).filter(follower=current_user)

            print("follower_list", follower_list)

            # Get Following List with filter those user return following
            following_list = UserContacts.objects.filter(
                Q(following=current_user, follower__in=follower_list))
            print("following_list", following_list)
            # Get Close Friend List
            close_friend_list = CloseFriendList.objects.values_list(
                'close_friend', flat=True).filter(user=current_user)
            print("close_friend_list", close_friend_list)
            # Exclude Follower User already in close friend list
            following_list = following_list.values_list(
                'follower', flat=True).exclude(Q(follower__in=close_friend_list))
            print("following_list", following_list)
            # Get Profile of Return Follower User
            filter_user = User.objects.filter(id__in=following_list)
            print("filter_user", filter_user)
        except:
            return []

        return filter_user

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        current_user = User.objects.filter(username=user)[0]
        print("current_user", current_user)
        queryset = self.filter_queryset(self.get_queryset())
        print("queryset", queryset, type(queryset))

        queryset_dict = {}
        for qs_data in queryset:
            print("qs_data", qs_data)
            queryset_dict[qs_data.id] = qs_data
        print("queryset_dict", queryset_dict)
        page = self.paginate_queryset(queryset)

        serializer = CloseFriendSearchSerializer(
            queryset, many=True, context={'user_id': current_user, 'queryset': queryset_dict})

        # Updated Sorted Data
        sorted_data = serializer.data

        return self.get_paginated_response(sorted_data[start_limit:end_limit])








class UserExploreView(generics.ListAPIView):
    model = User
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user_profile__interest__interest_name',
                     'user_profile__full_name']

    def get_queryset(self):

        # Get Requested user
        user = self.request.user

        # Get Current User
        current_user = User.objects.get(username=user)

        # Get Min & Max Age Year
        current_year = datetime.now().year
        min_age_year = current_year - current_user.preference.min_age
        max_age_year = current_year - current_user.preference.max_age

        # Get Filter User
        try:
            # Check User Interest
            user_interests = current_user.user_profile.interest.all()
            contactsLst = [contact.contact_number for contact in UsersContacts.objects.filter(user = current_user.id)]
            if len(user_interests) > 0:
                filter_user = User.objects.filter(geo_location__last_location__distance_lte=(current_user.geo_location.last_location, D(km=current_user.preference.radius)),
                                                  user_profile__dob__year__gte=max_age_year, user_profile__active=True, user_profile__dob__year__lte=min_age_year, user_profile__interest__in=current_user.user_profile.interest.all()).exclude(Q(user_follower__following=user) | Q(username=user)).order_by('-score__desirable_score', 'geo_location__last_location').prefetch_related('user_profile', 'display_pic', 'user_profile_image', 'user_profile__interest', 'preference', 'user_follower', 'score', 'geo_location').distinct()
            else:
                filter_user = User.objects.filter(geo_location__last_location__distance_lte=(current_user.geo_location.last_location, D(km=current_user.preference.radius)),
                                                  user_profile__dob__year__gte=max_age_year, user_profile__active=True, user_profile__dob__year__lte=min_age_year).exclude(Q(user_follower__following=user) | Q(username=user)).order_by('-score__desirable_score', 'geo_location__last_location').prefetch_related('user_profile', 'user_profile_image', 'display_pic', 'user_profile__interest', 'preference', 'user_follower', 'score', 'geo_location').distinct()
            filter_user = filter_user.exclude(user_profile__phone__in=contactsLst)
        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="User Profile Not Found")

        except UserLocation.DoesNotExist as e:
            raise NotFound(detail="User Location Not Found")

        except UserPreference.DoesNotExist as e:
            raise NotFound(detail="User Preference Not Found")
        except:
            return []
        # if current_user.preference.opposite_gender == 'Both':
            # try:
            #     filter_user = User.objects.filter(geo_location__last_location__distance_lte=(current_user.geo_location.last_location, D(km=current_user.preference.radius)),
            #                                       user_profile__dob__year__gte=max_age_year, user_profile__dob__year__lte=min_age_year,
            #                                       user_profile__interest__in=current_user.user_profile.interest.all()).exclude(username=user, user_following__following=current_user).order_by('-score__desirable_score', 'geo_location__last_location').prefetch_related('user_profile', 'user_profile_image', 'user_profile__interest', 'preference', 'user_follower', 'score', 'geo_location').distinct()
            # except ProfileDetails.DoesNotExist as e:
            #     raise NotFound(detail="User Profile Not Found")

            # except UserLocation.DoesNotExist as e:
            #     raise NotFound(detail="User Location Not Found")

            # except UserPreference.DoesNotExist as e:
            #     raise NotFound(detail="User Preference Not Found")
            # except:
            #     return []

        # else:
        #     try:
        #         filter_user = User.objects.filter(geo_location__last_location__distance_lte=(current_user.geo_location.last_location, D(km=current_user.preference.radius)),
        #                                           user_profile__dob__year__gte=max_age_year, user_profile__dob__year__lte=min_age_year,
        #                                           user_profile__gender=current_user.preference.opposite_gender,
        #                                           user_profile__interest__in=current_user.user_profile.interest.all()).exclude(username=user, user_following__following=current_user).order_by('-score__desirable_score').prefetch_related('user_profile', 'user_profile_image', 'user_profile__interest', 'preference', 'user_follower', 'score', 'geo_location').distinct()
        #     except ProfileDetails.DoesNotExist as e:
        #         raise NotFound(detail="User Profile Not Found")

        #     except UserLocation.DoesNotExist as e:
        #         raise NotFound(detail="User Location Not Found")

        #     except UserPreference.DoesNotExist as e:
        #         raise NotFound(detail="User Preference Not Found")
        #     except:
        #         return []

        # filtered_profile = ProfileDetails.objects.filter(uuid__in=filter_user)
        return filter_user

    def get_queryset2(self):

        # Get Requested user
        user = self.request.user

        # Get Current User
        current_user = User.objects.get(username=user)
        try:
            contactsLst = [contact.contact_number for contact in UsersContacts.objects.filter(user = current_user.id)]
            filter_user2 = User.objects.filter(user_profile__active=True, user_profile__phone__in=contactsLst).prefetch_related('user_profile', 'display_pic', 'user_profile_image', 'user_profile__interest', 'preference', 'user_follower', 'score', 'geo_location').distinct()
        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="User Profile Not Found")
        except:
            return []
        return filter_user2

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        current_user = User.objects.filter(username=user).prefetch_related(
            'user_profile', 'preference',  'user_profile__interest', 'score', 'geo_location', 'user_following')[0]
        queryset = self.filter_queryset(self.get_queryset())
        queryset2 = self.filter_queryset(self.get_queryset2())
        queryset_dict = {}
        for qs_data2 in queryset2:
            queryset_dict[qs_data2.id] = qs_data2

        for qs_data in queryset:
            queryset_dict[qs_data.id] = qs_data
        # contact_page = self.paginate_queryset(queryset2)
        page = self.paginate_queryset(queryset2 | queryset)

        contact_serializer = UserSerializer(
            queryset2, many=True, context={'user_id': current_user, 'queryset': queryset_dict})

        serializer = UserSerializer(
            queryset, many=True, context={'user_id': current_user, 'queryset': queryset_dict})

        # Sorting functions
        def desirable_score(profile): return profile['desirable_score']

        # Updated Sorted Data
        contacts_sorted_data = sorted(
            contact_serializer.data, key=desirable_score, reverse=True)

        
        sorted_data = sorted(
            serializer.data, key=desirable_score, reverse=True)

        total_explore_data = contacts_sorted_data + sorted_data

        return self.get_paginated_response(total_explore_data[start_limit:end_limit])
        # return Response(status=status.HTTP_200_OK, data={"message": "Success", "contacts": self.get_paginated_response(contacts_sorted_data[start_limit:end_limit])
                        # ,"explore":self.get_paginated_response(sorted_data[start_limit:end_limit])})

class UserLocationView(views.APIView):

    def get(self, request):
        # Get User
        user = request.user
        try:
            # Get User Location
            location = UserLocation.objects.get(user=user)

            # Serialise Data
            location_serializer = LocationSerializer(location)

            # Response
            if request.version == 'v1':
                response = success_response(location_serializer.data)
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(location_serializer.data, status=status.HTTP_200_OK)
        except UserLocation.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(
                    detail="User Location Object does not exist. Please Use Post method to create location object.")
            else:
                return Response({"message": "User Location Object does not exist. Please Use Post method to create location object."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        # Get User
        user = request.user

        # Get Count of User Locaton
        user_location_count = UserLocation.objects.filter(user=user).count()

        # Check if user location exist or not
        if user_location_count == 0:

            # Create Instance of User Location
            user_location = UserLocation(user=user)

            # Serialize User Data and Pass Data
            location_serializer = LocationSerializer(
                user_location, data=request.data)

            # Check If user input is valid
            if location_serializer.is_valid():
                # Store User Data
                location_serializer.save()

                # Send Response to User
                if request.version == 'v1':
                    response = success_response(location_serializer.data)
                    return Response(response, status=status.HTTP_201_CREATED)
                else:
                    return Response(location_serializer.data, status=status.HTTP_201_CREATED)
            else:
                if request.version == 'v1':
                    response = error_response(location_serializer.errors)
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(location_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If User Exist then Response Message with Message of Already Exist
            error_msg = {
                "message": "Location Object for User already Exist. Please Use Put Method to Update location"}
            if request.version == 'v1':
                response = error_response(error_msg['message'])
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data=error_msg, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Get User
        user = request.user

        try:
            # Create Instance of User Location
            user_location, created = UserLocation.objects.get_or_create(
                user=user)

            # Serialize User Data and Pass Data
            location_serializer = LocationSerializer(
                user_location, data=request.data)

            # Check If user input is valid
            if location_serializer.is_valid():
                # Store User Data
                location_serializer.save()

                # Send Response to User
                if request.version == 'v1':
                    response = success_response(location_serializer.data)
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    return Response(location_serializer.data, status=status.HTTP_200_OK)
            else:
                if request.version == 'v1':
                    response = error_response(location_serializer.errors)
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(location_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserLocation.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(
                    detail="User Location Object does not exist. Please Use Post method to create location object.")
            else:
                return Response({"message": "User Location Object does not exist. Please Use Post method to create location object."}, status=status.HTTP_404_NOT_FOUND)


class ReturnFollower(generics.ListAPIView):
    model = User
    serializer_class = InterestedUserProfile
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        # Get Current User
        current_user = self.request.user

        # Get Follower List
        follower_list = UserContacts.objects.values_list(
            'following', flat=True).filter(follower=current_user)

        print(follower_list)

        # Get Following List with filter those user return following
        following_list = UserContacts.objects.filter(
            Q(following=current_user, follower__in=follower_list))

        # Get Close Friend List
        close_friend_list = CloseFriendList.objects.values_list(
            'close_friend', flat=True).filter(user=current_user)

        # Exclude Follower User already in close friend list
        following_list = following_list.values_list(
            'follower', flat=True).exclude(Q(follower__in=close_friend_list))

        # Get Profile of Return Follower User
        profile_list = User.objects.filter(id__in=following_list).prefetch_related(
            'user_profile', 'display_pic', 'user_follower')

        return profile_list

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()

        queryset_dict = {}
        for qs_data in queryset:
            queryset_dict[qs_data.id] = qs_data

        page = self.paginate_queryset(queryset)

        serializer = self.serializer_class(
            queryset, many=True, context={'queryset': queryset_dict})

        # Updated Sorted Data
        sorted_data = serializer.data

        return self.get_paginated_response(sorted_data[start_limit:end_limit])


class CloseFriendsListView(generics.ListCreateAPIView, generics.DestroyAPIView):
    model = User
    serializer_class = InterestedUserProfile
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        # Get Current User
        current_user = self.request.user

        # Get Get Close Friend Flat List
        close_firends_list = CloseFriendList.objects.values_list(
            'close_friend', flat=True).filter(user=current_user)

        # Get Profiles List with filter Close Friends
        profile_list = User.objects.filter(
            id__in=close_firends_list).prefetch_related(
            'user_profile', 'user_profile_image', 'user_follower')

        # Return Profile List
        return profile_list

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.get_queryset()

        queryset_dict = {}
        for qs_data in queryset:
            queryset_dict[qs_data.id] = qs_data

        page = self.paginate_queryset(queryset)

        serializer = self.serializer_class(
            queryset, many=True, context={'queryset': queryset_dict})

        # Updated Sorted Data
        sorted_data = serializer.data

        return self.get_paginated_response(sorted_data[start_limit:end_limit])

    def create(self, request, *args, **kwargs):
        # Get Current User
        current_user = request.user

        try:
            # Close friend id
            close_friend_user_id = request.data['close_friend']

            # Closefriend User
            close_friend_user = User.objects.get(pk=close_friend_user_id)
            
        except:
            raise NotFound(detail="Please send close friend id")

        # Check already in close friend list
        is_close_friend = CloseFriendList.objects.filter(user=current_user, close_friend=close_friend_user).exists()

        if is_close_friend:
            if request.version == 'v1':
                response = error_response("Already in close friend list")
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail":"Already in close friend list"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Create Close Friend Instance
            close_friend = CloseFriendList(user=current_user)

            # Create Serializer and Pass data
            close_friend_serializer = CloseFriendSerializer(
                close_friend, data=request.data)

            # Check Validation
            if close_friend_serializer.is_valid():
                # Save Data if Data Validation is Correct
                close_friend_serializer.save()

                # Response User with 201 Code
                if request.version == 'v1':
                    response = success_response(close_friend_serializer.data)
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    return Response(close_friend_serializer.data, status=status.HTTP_201_CREATED)

            # If Validation Not accepted
            else:
                # Send Error Response
                if request.version == 'v1':
                    response = error_response(close_friend_serializer.errors)
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(close_friend_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, id, *args, **kwargs):
        # Get Current User
        current_user = request.user
        try:
            # Try get user by id
            close_frined = CloseFriendList.objects.get(
                user=current_user, close_friend=id)

            # User Delete
            close_frined.delete()

            # Response Positivily
            success_msg = {
                "message": "User removed from close frined list successfully"}
            if request.version == 'v1':
                response = success_response(success_msg['message'])
                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(success_msg, status=status.HTTP_200_OK)
        except CloseFriendList.DoesNotExist as e:
            # Send Does not exist response
            if request.version == 'v1':
                raise NotFound(detail="User not in close friend list")
            else:
                return Response({"message": "User not in close friend list"}, status=status.HTTP_404_NOT_FOUND)
