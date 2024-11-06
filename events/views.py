from django.shortcuts import render

from .serializers import EventImageSerializer, EventSerializer, EventListSerializer, EventInvitationSerializer, \
    PrivateEventSerializer, HostedEventSerializer, EventInterestedUsersSerializer
from .serializers import ReportEventsDetailsSerializer, CuratedEventsSerializer, EventCommentSerializer, \
    CommentListSerializer, EventDetailsListSerializer, InterestedEventsSerializer, ImagesUploadSerializer

from .serializers import EventImageSerializer, EventSerializer, EventListSerializer, EventInvitationSerializer, \
    PrivateEventSerializer, HostedEventSerializer, EventInterestedUsersSerializer
from .serializers import CuratedEventsSerializer, EventCommentSerializer, CommentListSerializer, \
    EventDetailsListSerializer, InterestedEventsSerializer, ImagesUploadSerializer, GoingEventsSerializer

from rest_framework import views
from .models import Events, EventImages, CuratedEvents, EventComments, CurateImages, ImagesUpload, EventInterestedUsers
from userprofile.models import ProfileDetails, UserPreference
from matching.models import UserLocation, CloseFriendList, UserContacts
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import datetime
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from django.db.models import Q
from django.contrib.gis.measure import D
from django.contrib.auth.models import User
from userprofile.serializers import ProfileDetailsSerializer
from matching.serializers import ProfileDetailsDataSerializer, InterestedUserProfile
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.renderers import JSONRenderer
from hobnob.standard_response import success_response, error_response
from django.contrib.gis.db.models.functions import Distance
from urllib.parse import urlparse
from django.core.mail import send_mail
from notifications.models import Notification


# Create your views here.

class UserEventSearchView(generics.ListAPIView):
    def get(self, request):
        query = request.GET.get("query", None)
        profile_data = ProfileDetails.objects.all()
        events_data = Events.objects.all()
        if query:
            profile_data = profile_data.filter(Q(username__icontains=query) |
                                               Q(full_name__icontains=query)).distinct()
            events_data = events_data.filter(Q(event_name__icontains=query)).distinct()
        return Response({"profile_data": ProfileDetailsSerializer(instance=profile_data, many=True).data,
                         "events_data": EventDetailsListSerializer(instance=events_data, many=True).data})


class EventSearchView(generics.ListAPIView):
    model = Events
    serializer_class = EventDetailsListSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['event_name']

    def get_queryset(self):
        try:
            category = str(self.request.GET.get("category", None))
            if not category:
                category = "1,2,3,4,5,6,7,8,9"
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            filterList = category.split(',')
            query = Q()
            for category in filterList:
                query = query | Q(event_date__gt=yesterday, event_type='Public', event_interest=int(category))

            # filter_events = self.model.objects.filter(query).distinct().raw("select * from events_events where event_date >'{yesterday}'".format(yesterday=yesterday))
            filter_events = self.model.objects.filter(query).distinct()

        except BaseException as err:
            print("errr", err)
            return []
        return filter_events

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit
        queryset = self.filter_queryset(self.get_queryset())
        queryset_dict = {}
        for qs_data in queryset:
            queryset_dict[qs_data.event_id] = qs_data
        page = self.paginate_queryset(queryset)
        serializer = EventDetailsListSerializer(
            queryset, many=True, context={'queryset': queryset_dict})
        sorted_data = serializer.data
        return self.get_paginated_response(sorted_data[start_limit:end_limit])


@api_view(['POST'])
def report_events(request):
    if request.method == "POST":
        serializer = ReportEventsDetailsSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.POST['user_id']
            event_id = request.POST['event_id']
            report_reason = request.POST['report_reason']
            # query -- to fetch eventdetails from events using event_id
            try:
                eventdata = Events.objects.get(event_id=event_id)
                userdata = ProfileDetails.objects.get(uuid=user_id)
                event_name = eventdata.event_name
                import datetime
                current_time = datetime.datetime.now()
                report_date = current_time
                reported_user_name = userdata.full_name
                # print(reported_user_name)
                event_date = eventdata.event_date
                event_time = eventdata.event_time_from
                event_address = eventdata.event_address
                event_host_name = eventdata.user.user_profile.full_name
            except Events.DoesNotExist:

                return Response(
                    {"message": "Event does not exists",
                     "status": False}, status=status.HTTP_404_NOT_FOUND)
            except ProfileDetails.DoesNotExist:
                return Response(
                    {"message": "User does not exists",
                     "status": False}, status=status.HTTP_404_NOT_FOUND)

            massage_body = (
                    "Dear Admin," + "\n" + event_name + " event is reported by an application user\nPlease check following\nevent details:\nName:" + event_name + "\nEvent Hosted by: " + event_host_name + "\nEvent Date:" + str(
                event_date) + " " + str(
                event_time) + "\nEvent Address: " + event_address + "\n\nReport reason:" + report_reason + "\nReported by:  " + reported_user_name + "\nReported on : " + str(
                report_date) + "\n\nRegards,\nHobnob Development Team.")

            send_mail(
                "Event Reported by User",
                massage_body,
                'ajay@quolam.com',
                ['pramod@quolam.com'],
            )

            serializer.save()
            return Response(
                {"message": "Event reported successfully",
                 "status": True}, )

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventView(views.APIView):
    def get(self, request, id):
        # Get User
        current_user = request.user
        # if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(uuid=current_user).active == True:
        try:
            event = Events.objects.get(event_id=id)
            event_serializer = EventDetailsListSerializer(
                event, context={'user': current_user})
            print("event", event_serializer.data)
            if request.version == 'v1':
                standard_response = success_response(event_serializer.data)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(event_serializer.data, status=status.HTTP_200_OK)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)
        # else:
        #     return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        user = request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            # Get Dates
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)

            # Get Events Type
            event_type = request.data['event_type']

            if len(str(request.data.get('event_price'))) == 0:
                del request.data['event_price']

            if len(str(request.data.get('event_time_from'))) == 0:
                del request.data['event_time_from']

            if len(str(request.data.get('event_time_to'))) == 0:
                del request.data['event_time_to']

            if len(str(request.data.get('event_city'))) == 0:
                del request.data['event_city']

            if len(str(request.data.get('event_end_date'))) == 0:
                del request.data['event_end_date']

            # Check User Has Already Created Public Events which is yet to be
            # if event_type == 'Private' or event_type == 'Close Friends':
            #     is_public_events = False
            # else:
            #     is_public_events = Events.objects.filter(
            #         user=user, event_type='Public', event_date__gt=yesterday).exists()

            # if is_public_events:
            #     error_msg = {
            #         "message": "User cannot create more than one public events at a time"}
            #     if request.version == 'v1':
            #         standard_response = error_response(error_msg['message'])
            #         return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
            #     else:
            #         return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
            # else:
            # If not then allow to create new events
            event = Events(user=user)
            event_serializer = EventSerializer(event, data=request.data)

            if event_serializer.is_valid():
                event_serializer.save()

                # event_id = Events.objects.get(
                #     event_id=event_serializer.data['event_id'])

                # Get Image URL Array
                events_img_arr = request.data.get('event_img', [])

                if len(events_img_arr) > 0:
                    # Make for loop
                    for evt_img in events_img_arr:
                        print("evt_img", evt_img)
                        if evt_img != "":
                            img_record = ImagesUpload.objects.get(id=evt_img)
                            print("img_record", img_record, img_record.event_img)
                            # Create Object of Event Image
                            # img_path = urlparse(img_record.event_img).path[7:]
                            img_path = img_record.event_img
                            event_img = EventImages.objects.create(
                                event=event, event_img=img_path, image_type=img_record.image_type)

                if request.version == 'v1':
                    standard_response = success_response(event_serializer.data)
                    return Response(standard_response, status=status.HTTP_201_CREATED)
                else:
                    return Response(event_serializer.data, status=status.HTTP_201_CREATED)
            else:
                if request.version == 'v1':
                    standard_response = error_response(event_serializer.errors)
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        try:
            user = request.user
            if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(
                    uuid=user).active == True:
                event = Events.objects.get(event_id=id)
                event_data = request.data

                # Get Dates
                today = datetime.date.today()
                yesterday = today - datetime.timedelta(days=1)

                if len(str(request.data.get('event_price'))) == 0:
                    del request.data['event_price']

                if len(str(request.data.get('event_time_from'))) == 0 or str(
                        request.data.get('event_time_from')) == "null":
                    del request.data['event_time_from']

                if len(str(request.data.get('event_time_to'))) == 0 or str(request.data.get('event_time_to')) == "null":
                    del request.data['event_time_to']

                if len(str(request.data.get('event_city'))) == 0 or str(request.data.get('event_city')) == "null":
                    del request.data['event_city']

                if len(str(request.data.get('event_end_date'))) == 0:
                    del request.data['event_end_date']

                # if "event_type" in event_data:
                #     if event.event_type == "Private" and event_data['event_type'] == 'Public':
                #         is_public_events = Events.objects.filter(
                #             user=user, event_type='Public', event_date__gt=yesterday).exists()

                #         if is_public_events:
                #             error_msg = {
                #                 "message": "User cannot create more than one public events at a time"}
                #             if request.version == 'v1':
                #                 standard_response = error_response(
                #                     error_msg['message'])
                #                 return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                #             else:
                #                 return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

                if event.user == user:
                    event_serializer = EventSerializer(
                        event, data=request.data, partial=True)
                    if event_serializer.is_valid():
                        event_serializer.save()

                        # Get Image URL Array
                        events_img_arr = request.data.get('event_img', [])

                        if len(events_img_arr) > 0:
                            # Make for loop
                            for evt_img in events_img_arr:

                                if evt_img != "":
                                    # Create Object of Event Image
                                    img_path = urlparse(evt_img).path[7:]

                                    # Check if img already exist
                                    is_img_exist = EventImages.objects.filter(
                                        event=event, event_img=img_path).exists()

                                    if not is_img_exist:
                                        event_img = EventImages.objects.create(
                                            event=event, event_img=img_path)

                        if request.version == 'v1':
                            standard_response = success_response(
                                event_serializer.data)
                            return Response(standard_response, status=status.HTTP_200_OK)
                        else:
                            return Response(event_serializer.data, status=status.HTTP_200_OK)
                    else:
                        if request.version == 'v1':
                            standard_response = error_response(
                                event_serializer.errors)
                            return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    error_msg = {
                        "message": "User doesn't have permission to Update"}
                    if request.version == 'v1':
                        standard_response = error_response(error_msg['message'])
                        return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            user = request.user
            if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(
                    uuid=user).active == True:
                event = Events.objects.get(event_id=id)

                if event.user == user:
                    event.delete()

                    success_msg = {"message": "Event deleted successfully"}
                    if request.version == 'v1':
                        standard_response = success_response(
                            success_msg['message'])
                        return Response(standard_response, status=status.HTTP_200_OK)
                    else:
                        return Response(success_msg, status=status.HTTP_200_OK)
                else:
                    error_msg = {
                        "message": "User doesn't have permission to delete"}
                    if request.version == 'v1':
                        standard_response = error_response(error_msg['message'])
                        return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)


class PrivateEventsView(generics.ListAPIView):
    model = Events
    serializer_class = PrivateEventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name', 'event_price']
    search_fields = ['event_name',
                     'event_interest__interest_name', 'event_price', 'user__user_profile__full_name',
                     'user__user_profile__username']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            interested_events = user.interested_user.all()
            print(f"{user=} | {interested_events=}")

            try:
                # Get User Preference
                user_preference = UserPreference.objects.filter(user=user)

                if user_preference.count() > 0:
                    # radius
                    user_distance_preference = user_preference[0].radius
                else:
                    user_distance_preference = 50.0
            except UserPreference.DoesNotExist as e:
                raise NotFound(detail="User Preference doesn't exist")

            # Get Dates
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)

            # Get Follower List
            follower_list = UserContacts.objects.values_list(
                'following', flat=True).filter(follower=user)
            # print("follower_list",follower_list)

            # Get Following List with filter those user return following
            following_list = UserContacts.objects.values_list('follower').filter(
                Q(following=user, follower__in=follower_list))

            close_friend_list = CloseFriendList.objects.values_list(
                'user', flat=True).filter(close_friend=user)

            # events_lists = self.model.objects.filter(Q(user=user, event_date__gt=yesterday, event_type='Private') | Q(user=user, event_date__gt=yesterday,event_type='Close Friends') | Q(event_type='Private', event_date__gt=yesterday, user__in=following_list) | Q(user__in=close_friend_list,event_date__gt=yesterday, event_type='Close Friends')| Q(event_type='Private',event_id__in=interested_events,event_date__gt=yesterday)).order_by(
            #     "event_date").prefetch_related('event_interest', 'interested_users', 'interested_users__display_pic', 'invited_users', 'user', 'user__user_profile', 'user__display_pic', 'images').distinct()

            # CHeck User has selected some interest or not
            # interested_users__display_pic

            # previous query
            # events_lists = self.model.objects.filter(
            #     Q(user=user, event_date__gt=yesterday, event_type='Private') | Q(user=user, event_date__gt=yesterday,
            #                                                                      event_type='Close Friends') | Q(
            #         event_type='Private', event_date__gt=yesterday, user__in=following_list) | Q(
            #         user__in=close_friend_list, event_date__gt=yesterday, event_type='Close Friends')).order_by(
            #     "event_date").exclude(event_id__in=interested_events).prefetch_related('event_interest',
            #                                                                            'interested_users',
            #                                                                            'interested_users__display_pic',
            #                                                                            'invited_users', 'user',
            #                                                                            'user__user_profile',
            #                                                                            'user__display_pic',
            #                                                                            'images').distinct()

            # Excludes events with interested events
            # events_lists = self.model.objects.filter(
            #     Q(user=user, event_date__gt=yesterday, event_type='Private') | Q(user=user, event_date__gt=yesterday,
            #                                                                      event_type='Close Friends') | Q(
            #         event_type='Private', event_date__gt=yesterday, user__in=following_list) | Q(
            #         user__in=close_friend_list, event_date__gt=yesterday, event_type='Close Friends')).order_by(
            #    "event_id", "event_date").exclude(event_id__in=interested_events).prefetch_related('event_interest',
            #                                                                            'interested_users',
            #                                                                            'interested_users__display_pic',
            #                                                                            'invited_users', 'user',
            #                                                                            'user__user_profile',
            #                                                                            'user__display_pic',
            #                                                                            'images').distinct("event_id").values_list("event_id",flat=True)
            # Does not Excludes events with interested events
            events_lists = self.model.objects.filter(
                Q(user=user, event_date__gt=yesterday, event_type='Private') | Q(user=user, event_date__gt=yesterday,
                                                                                 event_type='Close Friends') | Q(
                    event_type='Private', event_date__gt=yesterday, user__in=following_list) | Q(
                    user__in=close_friend_list, event_date__gt=yesterday, event_type='Close Friends')).order_by(
                "event_id", "event_date").prefetch_related('event_interest',
                                                           'interested_users',
                                                           'interested_users__display_pic',
                                                           'invited_users',
                                                           'user',
                                                           'user__user_profile',
                                                           'user__display_pic',
                                                           'images').distinct(
                "event_id").values_list("event_id", flat=True)

            events_lists = self.model.objects.filter(event_id__in=events_lists).order_by("event_date")

            return events_lists
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        queryset_dict = {}
        for event in queryset:
            queryset_dict[event.event_id] = event

        serializer = PrivateEventSerializer(
            queryset, many=True, context={'user': user, 'qs': queryset_dict})

        # Sorting functions
        def is_creator(event): return event['is_creator']

        # Updated Sorted Data
        sorted_data = sorted(serializer.data, key=is_creator, reverse=True)

        return self.get_paginated_response(sorted_data[start_limit:end_limit])


class PublicEventsView(generics.ListAPIView):
    model = Events
    serializer_class = EventListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name', 'event_price']
    search_fields = ['event_name',
                     'event_interest__interest_name', 'event_price', 'user__user_profile__full_name',
                     'user__user_profile__username']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        interested_events = user.interested_user.all()

        try:
            # Get User Preference
            user_preference = UserPreference.objects.filter(user=user)

            if user_preference.count() > 0:
                # radius
                user_distance_preference = user_preference[0].radius
            else:
                user_distance_preference = 50.0
        except UserPreference.DoesNotExist as e:
            raise NotFound(detail="User Preference doesn't exist")

        try:
            # Get User Current Location
            user_location = UserLocation.objects.get(user=user)
        except UserLocation.DoesNotExist as e:
            raise NotFound(detail="User Location doesn't exist")
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)

        # events_lists = self.model.objects.filter(Q(user=user, event_date__gt=yesterday, event_type='Public') | Q(event_type='Public', event_date__gt=yesterday, event_location__distance_lte=(
        #     user_location.last_location, D(km=user_distance_preference))))

        # Filter Events based on interest, location and date

        # CHeck User has selected some interest or not

        # events_lists = self.model.objects.filter(Q(user=user, event_date__gt=yesterday, event_type='Public') | Q(event_type='Public', event_date__gt=yesterday, event_location__distance_lte=(
        #     user_location.last_location, D(km=user_distance_preference)))).annotate(distance=Distance("event_location", user_location.last_location)).exclude(interested_users__in=[user]).order_by("distance", "event_date").exclude(event_id__in=interested_events).prefetch_related('event_interest', 'interested_users', 'interested_users__display_pic', 'invited_users', 'user', 'images').distinct()

        # Excludes events of interested events
        # events_lists = self.model.objects.filter(
        #     Q(user=user, event_date__gt=yesterday, event_type='Public') | Q(event_type='Public',
        #                                                                     event_date__gt=yesterday,
        #                                                                     event_location__distance_lte=(
        #                                                                         user_location.last_location,
        #                                                                         D(km=user_distance_preference)))).annotate(
        #     distance=Distance("event_location", user_location.last_location)).exclude(
        #     interested_users__in=[user]).order_by("event_id", "event_date", "distance").exclude(
        #     event_id__in=interested_events).prefetch_related('event_interest', 'interested_users',
        #                                                      'interested_users__display_pic', 'invited_users', 'user',
        #                                                      'images').distinct("event_id").values_list('event_id',
        #                                                                                                 flat=True)

        # Does not Excludes events of interested events
        events_lists = self.model.objects.filter(
            Q(user=user, event_date__gt=yesterday, event_type='Public') | Q(event_type='Public',
                                                                            event_date__gt=yesterday,
                                                                            event_location__distance_lte=(
                                                                                user_location.last_location,
                                                                                D(km=user_distance_preference)))).annotate(
            distance=Distance("event_location", user_location.last_location)).order_by("event_id", "event_date",
                                                                                       "distance").prefetch_related(
            'event_interest', 'interested_users',
            'interested_users__display_pic', 'invited_users', 'user',
            'images').distinct("event_id").values_list('event_id',
                                                       flat=True)

        events_lists = self.model.objects.filter(event_id__in=events_lists).annotate(
            distance=Distance("event_location", user_location.last_location)).order_by("event_date", "distance")

        # if len(interest_list) == 0:
        #     events_lists = self.model.objects.filter(Q(user=user, event_date__gt=yesterday, event_type='Public') | Q(event_type='Public', event_date__gt=yesterday, event_location__distance_lte=(
        #         user_location.last_location, D(km=user_distance_preference)))).annotate(distance=Distance("event_location", user_location.last_location)).exclude(interested_users__in=[user]).order_by("distance", "event_date").exclude(event_id__in=interested_events).prefetch_related('event_interest', 'interested_users', 'interested_users__display_pic', 'invited_users', 'user', 'images').distinct()
        # else:
        #     events_lists = self.model.objects.filter(Q(user=user, event_date__gt=yesterday, event_type='Public') | Q(event_interest__in=interest_list, event_type='Public', event_date__gt=yesterday, event_location__distance_lte=(
        #         user_location.last_location, D(km=user_distance_preference)))).annotate(distance=Distance("event_location", user_location.last_location)).exclude(interested_users__in=[user]).order_by("distance", "event_date").exclude(event_id__in=interested_events).prefetch_related('event_interest', 'interested_users', 'interested_users__display_pic', 'invited_users', 'user', 'images').distinct()

        # Q(user__in=close_friend_list, event_date__gt=yesterday, event_type='Private')
        return events_lists

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        queryset_dict = {}
        for event in queryset:
            queryset_dict[event.event_id] = event

        serializer = self.serializer_class(
            queryset, many=True, context={'user': user, 'qs': queryset_dict})

        # Sorting functions
        def is_creator(event): return event['is_creator']

        # Updated Sorted Data
        sorted_data = sorted(serializer.data, key=is_creator, reverse=True)

        return self.get_paginated_response(sorted_data[start_limit:end_limit])


# class ImageUploadView(generics.CreateAPIView):
#     queryset = ImagesUpload.objects.all()
#     serializer_class = ImagesUploadSerializer

class EventInterestedUsersView(views.APIView):
    model = EventInterestedUsers
    serializer_class = EventInterestedUsersSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get(self, request, id):
        user = self.request.user
        print("id", id)
        print("user", user)
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            print("profile details")
            interested_events = self.model.objects.filter(event=(Events.objects.get(event_id=id)))
            print("interested_events", interested_events)
            serializer = self.serializer_class(
                interested_events, many=True)
            print("serializer", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class InterestedEventsView(generics.ListAPIView):
    model = Events
    serializer_class = InterestedEventsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name', 'event_price']
    search_fields = ['event_name', 'location',
                     'event_interest__interest_name', 'event_price', 'user__user_profile__full_name',
                     'user__user_profile__username']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            # Get Dates
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)

            # Filter Events based on interest, location and date

            # CHeck User has selected some interest or not
            events_lists = self.model.objects.filter(interested_users__in=[user], event_date__gt=yesterday).order_by(
                "event_date", "event_time_from").prefetch_related(
                'event_interest', 'interested_users', 'interested_users__display_pic', 'invited_users', 'user',
                'user__user_profile', 'user__display_pic', 'images').distinct()

            return events_lists
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            start_limit = int(self.request.query_params.get('offset', 0))
            limit = int(self.request.query_params.get('limit', 20))
            end_limit = start_limit + limit

            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)

            queryset_dict = {}
            for event in queryset:
                queryset_dict[event.event_id] = event

            serializer = InterestedEventsSerializer(
                queryset, many=True, context={'user': user, 'qs': queryset_dict})

            return self.get_paginated_response(serializer.data[start_limit:end_limit])
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class AllPublicEventsView(generics.ListAPIView):
    model = Events
    serializer_class = EventListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name', 'event_price']
    search_fields = ['event_name', 'location',
                     'event_interest__interest_name', 'event_price', 'description', 'user__user_profile__full_name',
                     'user__user_profile__username']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            try:
                # Get User Profile
                profile = ProfileDetails.objects.get(uuid=user)
            except ProfileDetails.DoesNotExist as e:
                raise NotFound(detail="User Profile doesn't exist")

            # Get all interest list of user
            interest_list = profile.interest.all()

            # if len(interest_list) == 0:
            #     raise NotFound(detail="User doesn't selected interest")

            try:
                # Get User Preference
                user_distance_preference = UserPreference.objects.get(
                    user=user).radius
            except UserPreference.DoesNotExist as e:
                raise NotFound(detail="User Preference doesn't exist")

            try:
                # Get User Current Location
                user_location = UserLocation.objects.get(user=user)

            except UserLocation.DoesNotExist as e:
                raise NotFound(detail="User Location doesn't exist")

            # Get Dates
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)

            # Get Close Friend List
            close_friend_list = CloseFriendList.objects.values_list(
                'user', flat=True).filter(close_friend=user)

            # Filter Events based on interest, location and date

            # CHeck User has selected some interest or not
            if len(interest_list) == 0:
                events_lists = self.model.objects.filter(
                    Q(user=user, event_date__gt=yesterday) | Q(event_type='Public', event_date__gt=yesterday,
                                                               event_location__distance_lte=(
                                                                   user_location.last_location,
                                                                   D(km=user_distance_preference)))).annotate(
                    distance=Distance("event_location", user_location.last_location)).order_by("distance",
                                                                                               "event_date").prefetch_related(
                    'event_interest', 'interested_users', 'interested_users__display_pic', 'invited_users', 'user',
                    'images').distinct()
            else:
                events_lists = self.model.objects.filter(
                    Q(user=user, event_date__gt=yesterday) | Q(event_interest__in=interest_list, event_type='Public',
                                                               event_date__gt=yesterday, event_location__distance_lte=(
                            user_location.last_location, D(km=user_distance_preference))) | Q(
                        user__in=close_friend_list, event_date__gt=yesterday, event_type='Private')).prefetch_related(
                    'event_interest', 'interested_users', 'interested_users__display_pic', 'invited_users', 'user',
                    'images').distinct()

            # Q(user__in=close_friend_list, event_date__gt=yesterday, event_type='Private')

            return events_lists
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            start_limit = int(self.request.query_params.get('offset', 0))
            limit = int(self.request.query_params.get('limit', 20))
            end_limit = start_limit + limit

            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)

            queryset_dict = {}
            for event in queryset:
                queryset_dict[event.event_id] = event

            serializer = self.serializer_class(
                queryset, many=True, context={'user': user, 'qs': queryset_dict})

            # Sorting functions
            def is_creator(event):
                return event['is_creator']

            # Updated Sorted Data
            sorted_data = sorted(serializer.data, key=is_creator, reverse=True)

            return self.get_paginated_response(sorted_data[start_limit:end_limit])
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class UserEventsListView(generics.ListAPIView):
    model = Events
    serializer_class = EventDetailsListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name']
    search_fields = ['event_name', 'location',
                     'event_interest__interest_name', 'description']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            self.events = self.model.objects.filter(user=user).distinct()
            return self.events
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class EventImageView(views.APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, id):
        try:
            event_img = EventImages.objects.filter(event_id=id)
            event_img_serializer = EventImageSerializer(event_img, many=True)

            if request.version == 'v1':
                standard_response = success_response(event_img_serializer.data)
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(event_img_serializer.data, status=status.HTTP_200_OK)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            user = request.user
            if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(
                    uuid=user).active == True:
                event = Events.objects.get(event_id=request.data['event'])

                if event.user == user:
                    event_img = EventImages(event=event)
                    event_img_serializer = EventImageSerializer(
                        event_img, data=request.data)

                    if event_img_serializer.is_valid():
                        event_img_serializer.save()

                        if request.version == 'v1':
                            standard_response = success_response(
                                event_img_serializer.data)
                            return Response(standard_response, status=status.HTTP_201_CREATED)
                        else:
                            return Response(event_img_serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        if request.version == 'v1':
                            standard_response = error_response(
                                event_img_serializer.errors)
                            return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response(event_img_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    error_msg = {
                        "message": "User doesn't have permission to add image for this event."}
                    if request.version == 'v1':
                        standard_response = error_response(error_msg['message'])
                        return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            event_img = EventImages.objects.filter(pk=id)
            event_img.delete()

            # Success Msg
            success_msg = {"message": "Image Deleted Successfully"}

            if request.version == 'v1':
                standard_response = success_response(success_msg['message'])
                return Response(standard_response, status=status.HTTP_200_OK)
            else:
                return Response(success_msg, status=status.HTTP_200_OK)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)


# Previous Used
# class ImageUploadView(generics.CreateAPIView):
#     queryset = ImagesUpload.objects.all()
#     serializer_class = ImagesUploadSerializer
#     print("image upload view")

class ImageUploadView(views.APIView):
    def post(self, request):
        img_upload = ImagesUpload.objects.create(event_img=request.data['event_img'])

        if "image_type" in request.data:
            img_upload = ImagesUpload.objects.create(event_img=request.data['event_img'],
                                                     image_type=request.data['image_type'])

        img_upload.save()
        img_serializer = ImagesUploadSerializer(img_upload)
        return Response(img_serializer.data, status=status.HTTP_201_CREATED)


class AddEventUserInterested(views.APIView):

    def post(self, request, event_id):
        try:
            user = request.user
            if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(
                    uuid=user).active == True:
                event = Events.objects.get(event_id=event_id)
                event.interested_users.add(user)

                if user in event.going_users.all():
                    event.going_users.remove(user)
                if user in event.yet_to_decide_users.all():
                    event.yet_to_decide_users.remove(user)

                event.save()

                # Success Message
                success_msg = {"message": "User Added to Event"}
                if request.version == 'v1':
                    standard_response = success_response(success_msg)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(success_msg, status=status.HTTP_200_OK)
            else:
                return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, event_id):
        try:
            user = request.user
            if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(
                    uuid=user).active == True:
                event = Events.objects.get(event_id=event_id)
                event.interested_users.remove(user)
                event.save()

                # Remove from notification screen also
                notification = Notification.objects.filter(notification_user=event.user, activity_type='event',
                                                           activity_sub_type='event_interested',
                                                           activity_id=event,
                                                           activity_user=user).delete()

                success_msg = {"message": "User Deleted from Event"}
                if request.version == 'v1':
                    standard_response = success_response(success_msg['message'])
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(success_msg, status=status.HTTP_200_OK)
            else:
                return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)


class UpcomingEventsListView(generics.ListAPIView):
    model = Events
    serializer_class = EventListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name']
    search_fields = ['event_name', 'location',
                     'event_interest__interest_name', 'description']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            # Getting Today's date
            today = datetime.date.today()
            # Getting yesterday date for filtering events
            yesterday = today - datetime.timedelta(days=1)

            # Get Close Friend List
            close_friend_list = CloseFriendList.objects.values_list(
                'user', flat=True).filter(close_friend=user)

            # Find Events user has created and events user has interested. Exclude all events which has date yesterday
            self.events = self.model.objects.filter(Q(event_date__gt=yesterday), Q(
                interested_users__in=[user]) | Q(invited_users__in=[user]) | Q(user__in=close_friend_list,
                                                                               event_date__gt=yesterday,
                                                                               event_type='Private')).prefetch_related(
                'event_interest', 'interested_users', 'invited_users', 'user', 'interested_users__display_pic',
                'interested_users__user_profile_image', 'images').distinct()

            return self.events
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            start_limit = int(self.request.query_params.get('offset', 0))
            limit = int(self.request.query_params.get('limit', 20))
            end_limit = start_limit + limit

            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)

            queryset_dict = {}
            for event in queryset:
                queryset_dict[event.event_id] = event

            serializer = self.serializer_class(
                queryset, many=True, context={'user': user, 'qs': queryset_dict})

            return self.get_paginated_response(serializer.data[start_limit:end_limit])
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class PastEventsListView(generics.ListAPIView):
    model = Events
    serializer_class = EventListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name']
    search_fields = ['event_name', 'location',
                     'event_interest__interest_name', 'description']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            # Getting Today's date
            today = datetime.date.today()
            # Getting yesterday date for filtering events
            yesterday = today - datetime.timedelta(days=1)

            # Find Events user has created and events user has interested. Exclude all events which has date yesterday
            self.events = self.model.objects.filter(Q(event_date__lt=today), Q(
                user=user) | Q(interested_users__in=[user])).distinct().prefetch_related('event_interest',
                                                                                         'interested_users',
                                                                                         'invited_users', 'user',
                                                                                         'interested_users__user_profile',
                                                                                         'interested_users__display_pic',
                                                                                         'images').distinct()

            return self.events
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            start_limit = int(self.request.query_params.get('offset', 0))
            limit = int(self.request.query_params.get('limit', 20))
            end_limit = start_limit + limit

            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)

            queryset_dict = {}
            for event in queryset:
                queryset_dict[event.event_id] = event

            serializer = self.serializer_class(
                queryset, many=True, context={'user': user, 'qs': queryset_dict})

            return self.get_paginated_response(serializer.data[start_limit:end_limit])
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class GetInterestedUserList(views.APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, id):
        try:
            event = Events.objects.get(event_id=id)

            # Get all interested user list
            interested_users = event.interested_users.all()

            # Create Pagination Instance
            pagination = LimitOffsetPagination()

            # Set Pagination Size
            pagination.page_size = 20

            # Get all profile details of interested user
            profile_list = User.objects.filter(id__in=interested_users).prefetch_related(
                'user_profile', 'user_profile_image', 'user_follower').distinct()

            # Pass Pagination query
            paginated_data = pagination.paginate_queryset(
                profile_list, request)

            # Convert to dictionary
            queryset_dict = {}
            for qs_data in profile_list:
                queryset_dict[qs_data.id] = qs_data

            # Serialize profile data
            profile_details_serializer = InterestedUserProfile(
                profile_list, many=True, context={'queryset': queryset_dict})

            return pagination.get_paginated_response(profile_details_serializer.data)

        except Events.DoesNotExist as e:
            raise NotFound(detail="Event doesn't exist")
        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="User Profile Not Found")


class CuratedEventsListView(generics.ListCreateAPIView):
    model = CuratedEvents
    serializer_class = CuratedEventsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name',
                        'description', 'categoery__interest_name']
    search_fields = ['event_name']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        # Make Curated Event Query with prefetch_related data
        currated_events = CuratedEvents.objects.all(
        ).prefetch_related('categoery', 'currated_images')

        return currated_events

    def list(self, request, *args, **kwargs):
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        queryset_dict = {}
        for event in queryset:
            queryset_dict[event.id] = event

        serializer = CuratedEventsSerializer(
            queryset, many=True, context={'qs': queryset_dict})

        return self.get_paginated_response(serializer.data[start_limit:end_limit])


class CuratedEventsView(generics.RetrieveAPIView):
    queryset = CuratedEvents.objects.all()
    serializer_class = CuratedEventsSerializer


class SingleCommentView(views.APIView):

    def get(self, request, id):
        # Get User
        current_user = request.user
        if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
                uuid=current_user).active == True:
            try:
                # Get Comments based on ID
                comments = EventComments.objects.get(comment_id=id)

                # Serializer Data
                comment_serializer = EventCommentSerializer(comments)

                # Response User with serializer
                if request.version == 'v1':
                    standard_response = success_response(comment_serializer.data)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(comment_serializer.data, status=status.HTTP_200_OK)
            except EventComments.DoesNotExist as e:
                raise NotFound(detail="Event Comments doesn't exist")
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    # def post(self, request):
    #     # Get User
    #     current_user = request.user
    #     if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
    #             uuid=current_user).active == True:
    #         # Get Event ID
    #         event_id = request.data['event']
    #
    #         # Check Events Type
    #         event_type = Events.objects.get(event_id=event_id).event_type
    #
    #         # CHeck Event Type
    #         if event_type == 'Private':
    #             error_msg = {
    #                 "message": "Cannot make comment on Private Event"}
    #             if request.version == 'v1':
    #                 standard_response = error_response(error_msg['message'])
    #                 return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
    #             else:
    #                 return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
    #
    #         # Create Comment Instance
    #         comment = EventComments(comment_user=current_user)
    #
    #         # Pass Comment Instance to Serializer
    #         comment_serializer = EventCommentSerializer(comment, data=request.data)
    #
    #         # Check Validation of Comment Instace
    #         if comment_serializer.is_valid():
    #             # Save Resonse
    #             comment_serializer.save()
    #
    #             # Return Valid Data Response
    #             if request.version == 'v1':
    #                 standard_response = success_response(comment_serializer.data)
    #                 return Response(standard_response, status=status.HTTP_201_CREATED)
    #             else:
    #                 return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
    #
    #         else:
    #             # Return Error Response
    #             if request.version == 'v1':
    #                 standard_response = error_response(comment_serializer.errors)
    #                 return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
    #             else:
    #                 return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     else:
    #         return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        # Get User
        current_user = request.user
        if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
                uuid=current_user).active == True:
            # Get Event ID
            event_id = request.data['event']

            # Check Events Type
            event = Events.objects.get(event_id=event_id)
            event_type = event.event_type
            event_owner = event.user

            # CHeck Event Type
            if event_type == 'Private':
                is_follower = UserContacts.objects.filter(
                    following=current_user, follower=event_owner).count()

                is_following = UserContacts.objects.filter(
                    following=event_owner, follower=current_user).count()

                print(f"{is_following=} | {is_follower=}")
                if is_following == 0 and is_follower == 0:
                    error_msg = {
                        "message": "Cannot make comment on Private Event"}
                    if request.version == 'v1':
                        standard_response = error_response(error_msg['message'])
                        return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)
            elif event_type == 'Close Friends':
                is_close_friend = CloseFriendList.objects.filter(Q(user=current_user) | Q(user=event_owner),
                                                                 Q(close_friend=event_owner) | Q(
                                                                     close_friend=current_user)).count()
                if is_close_friend == 0:
                    error_msg = {
                        "message": "Cannot make comment on Close Friend"}
                    if request.version == 'v1':
                        standard_response = error_response(error_msg['message'])
                        return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

            # Create Comment Instance
            comment = EventComments(comment_user=current_user)

            # Pass Comment Instance to Serializer
            comment_serializer = EventCommentSerializer(comment, data=request.data)

            # Check Validation of Comment Instace
            if comment_serializer.is_valid():
                # Save Resonse
                comment_serializer.save()

                # Return Valid Data Response
                if request.version == 'v1':
                    standard_response = success_response(comment_serializer.data)
                    return Response(standard_response, status=status.HTTP_201_CREATED)
                else:
                    return Response(comment_serializer.data, status=status.HTTP_201_CREATED)

            else:
                # Return Error Response
                if request.version == 'v1':
                    standard_response = error_response(comment_serializer.errors)
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        # Get User
        current_user = request.user
        if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
                uuid=current_user).active == True:
            try:
                # Get Comments based on ID
                comments = EventComments.objects.get(comment_id=id)

                # Check COmment User and Current USer
                if current_user == comments.comment_user:
                    # Serializer Data
                    comment_serializer = EventCommentSerializer(
                        comments, data=request.data, partial=True)

                    # Check Validation of Comment Instace
                    if comment_serializer.is_valid():
                        # Save Resonse
                        comment_serializer.save()

                        # Return Valid Data Response
                        if request.version == 'v1':
                            standard_response = success_response(
                                comment_serializer.data)
                            return Response(standard_response, status=status.HTTP_200_OK)
                        else:
                            return Response(comment_serializer.data, status=status.HTTP_200_OK)

                    else:
                        # Return Error Response
                        if request.version == 'v1':
                            standard_response = error_response(
                                comment_serializer.errors)
                            return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    error_msg = {
                        "message": "You don't have permission to edit this comment"}
                    if request.version == 'v1':
                        standard_response = error_response(error_msg['message'])
                        return Response(standard_response, status=status.HTTP_401_UNAUTHORIZED)
                    else:
                        return Response(error_msg, status=status.HTTP_401_UNAUTHORIZED)

            except EventComments.DoesNotExist as e:
                raise NotFound(detail="Event Comments doesn't exist")
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        # Get User
        current_user = request.user
        if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
                uuid=current_user).active == True:
            try:
                # Get Comments based on ID
                comments = EventComments.objects.get(comment_id=id)
                event_owner = comments.event.user
                event_id = comments.event.event_id
                print(f"{event_owner=}")
                # Verify Comment User & Delete User
                if current_user == comments.comment_user:
                    # Delete Comment
                    comments.delete()

                    # Remove notification of event comment
                    notification = Notification.objects.filter(notification_user=event_owner,
                                                               activity_type="event", activity_sub_type="event_comment",
                                                               activity_id=event_id, activity_user=current_user
                                                               ).delete()

                    # Response User with serializer
                    standard_response = success_response(
                        "Comment Deleted Succesfully")
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    standard_response = error_response(
                        "You don't have permission to delete this comment")
                    return Response(standard_response, status=status.HTTP_401_UNAUTHORIZED)
            except EventComments.DoesNotExist as e:
                raise NotFound(detail="Event Comments doesn't exist")
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class CommentsList(views.APIView):

    def get(self, request, id):
        try:
            # Get Current User
            current_user = request.user
            if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
                    uuid=current_user).active == True:
                # Get Comments list with filter
                comments_list = EventComments.objects.filter(reply=None, event=id).order_by(
                    'create_at').prefetch_related(
                    'comment_user__user_profile', 'comment_user__display_pic', 'replies')

                # Initiate Pagination
                paginator = LimitOffsetPagination()

                # Set Pagination Page Size
                paginator.page_size = 50

                # Pass Query to Pagination
                result_page = paginator.paginate_queryset(comments_list, request)

                # QUerySet
                queryset_dict = {}
                for comment in comments_list:
                    queryset_dict[comment.comment_id] = comment

                # Serializer
                comment_serializer = CommentListSerializer(
                    comments_list, many=True, context={'queryset': queryset_dict, 'current_user': current_user})

                # Response
                return paginator.get_paginated_response(comment_serializer.data)
            else:
                return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except EventComments.DoesNotExist as e:
            raise NotFound(detail="Events Doesn't Exist")


class CommentReplyList(views.APIView):

    def get(self, request, id):
        try:
            # Get Current User
            current_user = request.user
            if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
                    uuid=current_user).active == True:

                # Get Comments list with filter
                comments_list = EventComments.objects.filter(reply=id).order_by('create_at').prefetch_related(
                    'comment_user__user_profile', 'comment_user__display_pic', 'replies')

                # Initiate Pagination
                paginator = LimitOffsetPagination()

                # Set Pagination Page Size
                paginator.page_size = 50

                # Pass Query to Pagination
                result_page = paginator.paginate_queryset(comments_list, request)

                # QUerySet
                queryset_dict = {}
                for comment in comments_list:
                    queryset_dict[comment.comment_id] = comment

                # Serializer
                comment_serializer = CommentListSerializer(
                    comments_list, many=True, context={'queryset': queryset_dict, 'current_user': current_user})

                # Response
                return paginator.get_paginated_response(comment_serializer.data)
            else:
                return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except EventComments.DoesNotExist as e:
            raise NotFound(detail="Events Doesn't Exist")


class EventInvitationView(views.APIView):

    def get(self, request, id):
        # Get User
        current_user = request.user
        try:
            if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
                    uuid=current_user).active == True:
                # Filter Events based on events id
                events = Events.objects.get(event_id=id)

                # Check if user is Event Creator
                if current_user == events.user:
                    # Get all invited User List
                    invited_users = events.invited_users.all()

                    # Pass User List to ProfileDetails Instance
                    invited_user_profiles = User.objects.filter(id__in=invited_users).prefetch_related(
                        'user_profile', 'user_profile_image', 'user_follower').distinct()

                    # Create LimitOffset Pagination Instance
                    pagination = LimitOffsetPagination()

                    # Set Pagination Size
                    pagination.page_size = 50

                    # Pass all profile list to pagination function
                    paginated_data = pagination.paginate_queryset(
                        invited_user_profiles, request)

                    # Convert to dictionary
                    queryset_dict = {}
                    for qs_data in invited_user_profiles:
                        queryset_dict[qs_data.id] = qs_data

                    # Pass data from pagination to data serializer function
                    profile_serializer = InterestedUserProfile(
                        paginated_data, many=True, context={'queryset': queryset_dict})

                    # Response back with Pagination
                    return pagination.get_paginated_response(profile_serializer.data)

                # If user is not creator
                else:
                    # Response back with Unauthorization Error
                    standard_response = error_response(
                        "You don't have permission to see invitation list")
                    return Response(standard_response, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)
            # If events Not exist
        except Events.DoesNotExist as e:
            # Response back with Data not found
            raise NotFound(detail="Event doesn't exist")

    def post(self, request, id):
        # Get User
        current_user = request.user
        if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
                uuid=current_user).active == True:
            # Get Invation user
            invited_user = request.data['invited_users']

            try:
                # Filter Events based on events id
                events = Events.objects.get(event_id=id)

                print(current_user, events.user)

                # Check if user is Event Creator
                if current_user == events.user:

                    # Remove User from Interested User
                    events.interested_users.remove(invited_user)

                    # Add User to Invited User
                    events.invited_users.add(invited_user)

                    # Response user
                    standard_response = success_response(
                        "You succesfully updated invitation list")
                    return Response(standard_response, status=status.HTTP_200_OK)

                # If user is not creator
                else:
                    # Response back with Unauthorization Error
                    standard_response = error_response(
                        "You don't have permission to add in invitation list")
                    return Response(standard_response, status=status.HTTP_401_UNAUTHORIZED)

            # If events Not exist
            except Events.DoesNotExist as e:
                # Response back with Data not found
                raise NotFound(detail="Event doesn't exist")
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        # Get User
        current_user = request.user
        if ProfileDetails.objects.filter(uuid=current_user).exists() and ProfileDetails.objects.get(
                uuid=current_user).active == True:

            # Get Invation user
            try:
                invited_user = request.data['invited_users']
            except:
                standard_response = error_response("Add invited user id in body")
                return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Filter Events based on events id
                events = Events.objects.get(event_id=id)

                # Check if user is Event Creator
                if current_user == events.user:

                    # Check user is in invitation list
                    if invited_user in events.invited_users.all():

                        # Remove User from Invited User
                        events.invited_users.remove(invited_user)

                        # Add User to Interested User
                        events.interested_users.add(invited_user)

                        # Response user
                        standard_response = success_response(
                            "You succesfully remove from invitation list")
                        return Response(standard_response, status=status.HTTP_200_OK)
                    else:
                        # Send Invalid User Response
                        raise NotFound(detail="User not exist in invitation list")

                # If user is not creator
                else:
                    # Response back with Unauthorization Error
                    standard_response = error_response(
                        "You don't have permission to add in invitation list")
                    return Response(standard_response, status=status.HTTP_400_BAD_REQUEST)

            # If events Not exist
            except Events.DoesNotExist as e:
                # Response back with Data not found
                raise NotFound(detail="Event doesn't exist")
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class HostedEventsView(generics.ListAPIView):
    model = Events
    serializer_class = PrivateEventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name', 'event_price']
    search_fields = ['event_name',
                     'event_interest__interest_name', 'event_price', 'user__user_profile__full_name',
                     'user__user_profile__username']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            interested_events = user.interested_user.all()

            # Get Dates
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)

            # CHeck User has selected some interest or not
            # interested_users__display_pic
            todays_events_lists = self.model.objects.filter(user=user, event_date=today).order_by(
                "-event_date").prefetch_related('event_interest', 'interested_users', 'interested_users__display_pic',
                                                'invited_users', 'user', 'user__user_profile', 'user__display_pic',
                                                'images').distinct()

            past_events_lists = self.model.objects.filter(user=user, event_date__lt=today).order_by(
                "-event_date").prefetch_related('event_interest', 'interested_users', 'interested_users__display_pic',
                                                'invited_users', 'user', 'user__user_profile', 'user__display_pic',
                                                'images').distinct()

            upcoming_events_lists = self.model.objects.filter(user=user, event_date__gt=today).order_by(
                "-event_date").prefetch_related('event_interest', 'interested_users', 'interested_users__display_pic',
                                                'invited_users', 'user', 'user__user_profile', 'user__display_pic',
                                                'images').distinct()

            events_lists = todays_events_lists | past_events_lists | upcoming_events_lists
            # new line added
            events_lists = events_lists.order_by("-create_at")
            return events_lists
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        queryset_dict = {}
        for event in queryset:
            queryset_dict[event.event_id] = event

        serializer = HostedEventSerializer(
            queryset, many=True, context={'user': user, 'qs': queryset_dict})

        # Sorting functions
        def is_creator(event): return event['is_creator']

        # Updated Sorted Data
        sorted_data = sorted(serializer.data, key=is_creator, reverse=True)

        return self.get_paginated_response(sorted_data[start_limit:end_limit])


class OthersHostedEventsView(generics.ListAPIView):
    model = Events
    serializer_class = PrivateEventSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name', 'event_price']
    search_fields = ['event_name',
                     'event_interest__interest_name', 'event_price', 'user__user_profile__full_name',
                     'user__user_profile__username']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        uid = self.kwargs.get(self.lookup_url_kwarg)
        print("uid", uid)
        user = User.objects.get(pk=uid)

        # new added
        following_user = self.request.user
        follower_user = user

        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            interested_events = user.interested_user.all()

            # new added
            # Check If User Following
            is_exist = UserContacts.objects.filter(
                following=following_user, follower=follower_user).exists()

            # Check If User is Close Friend
            is_close_friend = CloseFriendList.objects.values_list(
                'user', flat=True).filter(user=following_user, close_friend=follower_user).exists()

            # case 1 : following each other and close friend
            if is_exist and is_close_friend:
                events_lists = self.model.objects.filter(user=user).order_by(
                    "-event_date").prefetch_related('event_interest', 'interested_users',
                                                    'interested_users__display_pic',
                                                    'invited_users', 'user', 'user__user_profile',
                                                    'user__display_pic',
                                                    'images').distinct()


            # case 2 : following each other and not close friend
            elif is_exist and is_close_friend is False:
                events_lists = self.model.objects.filter(user=user, event_type__in=['Public', 'Private']).order_by(
                    "-event_date").prefetch_related('event_interest', 'interested_users',
                                                    'interested_users__display_pic',
                                                    'invited_users', 'user', 'user__user_profile',
                                                    'user__display_pic',
                                                    'images').distinct()

            # case 3 : not following each other and close friend
            elif is_exist is False and is_close_friend:
                events_lists = self.model.objects.filter(user=user,
                                                         event_type__in=['Public', 'Close Friends']).order_by(
                    "-event_date").prefetch_related('event_interest', 'interested_users',
                                                    'interested_users__display_pic',
                                                    'invited_users', 'user', 'user__user_profile',
                                                    'user__display_pic',
                                                    'images').distinct()

            # case 4 : not following each other and not close friend
            # elif is_exist is False and is_close_friend is False:
            else:
                events_lists = self.model.objects.filter(user=user, event_type="Public").order_by(
                    "-event_date").prefetch_related('event_interest', 'interested_users',
                                                    'interested_users__display_pic',
                                                    'invited_users', 'user', 'user__user_profile',
                                                    'user__display_pic',
                                                    'images').distinct()

            return events_lists
        else:
            return Response({"message: User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user

        start_limit = int(self.request.query_params.get('offset', 0))
        limit = int(self.request.query_params.get('limit', 20))
        end_limit = start_limit + limit

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        queryset_dict = {}
        for event in queryset:
            queryset_dict[event.event_id] = event

        serializer = HostedEventSerializer(
            queryset, many=True, context={'user': user, 'qs': queryset_dict})

        # Sorting functions
        def is_creator(event): return event['is_creator']

        # Updated Sorted Data
        sorted_data = sorted(serializer.data, key=is_creator, reverse=True)

        return self.get_paginated_response(sorted_data[start_limit:end_limit])


class AddEventUserGoing(views.APIView):

    def get(self, request, event_id):
        try:
            user = request.user
            if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(
                    uuid=user).active == True:
                event = Events.objects.get(event_id=event_id)
                event.going_users.add(user)

                if user in event.interested_users.all():
                    event.interested_users.remove(user)
                if user in event.yet_to_decide_users.all():
                    event.yet_to_decide_users.remove(user)

                event.save()

                # Success Message
                success_msg = {"message": "User Added to Going Event"}
                if request.version == 'v1':
                    standard_response = success_response(success_msg)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(success_msg, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, event_id):
        try:
            user = request.user
            if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(
                    uuid=user).active == True:
                event = Events.objects.get(event_id=event_id)
                event.going_users.remove(user)
                event.save()

                # Remove from notification screen also
                notification = Notification.objects.filter(notification_user=event.user, activity_type='event',
                                                           activity_sub_type='event_going',
                                                           activity_id=event,
                                                           activity_user=user).delete()
                # Success Message
                success_msg = {"message": "User Deleted from Going Event"}
                if request.version == 'v1':
                    standard_response = success_response(success_msg)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(success_msg, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)


class AddEventUserYetToDecide(views.APIView):

    def post(self, request, event_id):
        user = request.user
        try:
            if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(
                    uuid=user).active == True:
                event = Events.objects.get(event_id=event_id)
                event.yet_to_decide_users.add(user)

                if user in event.going_users.all():
                    event.going_users.remove(user)
                if user in event.interested_users.all():
                    event.interested_users.remove(user)

                event.save()

                # Success Message
                success_msg = {"message": "User Added to YetToDecide Event"}
                if request.version == 'v1':
                    standard_response = success_response(success_msg)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(success_msg, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, event_id):
        user = request.user
        try:
            if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(
                    uuid=user).active == True:
                event = Events.objects.get(event_id=event_id)
                event.yet_to_decide_users.remove(user)
                event.save()

                # Remove from notification screen also
                notification = Notification.objects.filter(notification_user=event.user, activity_type='event',
                                                           activity_sub_type='event_yettodecide',
                                                           activity_id=event,
                                                           activity_user=user).delete()
                # Success Message
                success_msg = {"message": "User Deleted from YetToDecide Event"}
                if request.version == 'v1':
                    standard_response = success_response(success_msg)
                    return Response(standard_response, status=status.HTTP_200_OK)
                else:
                    return Response(success_msg, status=status.HTTP_200_OK)
            else:
                return Response({"message": "User has no account"}, status=status.HTTP_400_BAD_REQUEST)
        except Events.DoesNotExist as e:
            if request.version == 'v1':
                raise NotFound(detail="Event doesn't exist")
            else:
                return Response({"message": "Event doesn't exist"}, status=status.HTTP_404_NOT_FOUND)


class GoingEventsView(generics.ListAPIView):
    model = Events
    serializer_class = GoingEventsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name', 'event_price']
    search_fields = ['event_name', 'location',
                     'event_interest__interest_name', 'event_price', 'user__user_profile__full_name',
                     'user__user_profile__username']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            # Get Dates
            today = datetime.datetime.today()
            yesterday = today - datetime.timedelta(days=1)

            events_lists = self.model.objects.filter(going_users__in=[user], event_date__gt=yesterday).order_by(
                'event_date', 'event_time_from').prefetch_related('event_interest', 'going_users',
                                                                  'going_users__display_pic', 'invited_users', 'user',
                                                                  'user__user_profile', 'user__display_pic',
                                                                  'images').distinct()

            return events_lists
        else:
            return Response({"message:User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            start_limit = int(self.request.query_params.get('offset', 0))
            limit = int(self.request.query_params.get('limit', 20))
            end_limit = start_limit + limit

            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)

            queryset_dict = {}
            for event in queryset:
                queryset_dict[event.event_id] = event

            serializer = GoingEventsSerializer(queryset, many=True, context={'user': user, 'qs': queryset_dict})

            return self.get_paginated_response(serializer.data[start_limit:end_limit])

        else:
            return Response({"message:User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class YetToDecideEventsView(generics.ListAPIView):
    model = Events
    serializer_class = GoingEventsSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['event_name', 'location',
                        'event_interest__interest_name', 'event_price']
    search_fields = ['event_name', 'location',
                     'event_interest__interest_name', 'event_price', 'user__user_profile__full_name',
                     'user__user_profile__username']
    pagination_class = LimitOffsetPagination
    renderer_classes = [JSONRenderer]

    def get_queryset(self):
        user = self.request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            # Get Dates
            today = datetime.datetime.today()
            yesterday = today - datetime.timedelta(days=1)

            events_lists = self.model.objects.filter(yet_to_decide_users__in=[user], event_date__gt=yesterday).order_by(
                'event_date', 'event_time_from').prefetch_related('event_interest', 'yet_to_decide_users',
                                                                  'yet_to_decide_users__display_pic', 'invited_users',
                                                                  'user', 'user__user_profile', 'user__display_pic',
                                                                  'images').distinct()

            return events_lists
        else:
            return Response({"message:User has no account"}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        if ProfileDetails.objects.filter(uuid=user).exists() and ProfileDetails.objects.get(uuid=user).active == True:
            start_limit = int(self.request.query_params.get('offset', 0))
            limit = int(self.request.query_params.get('limit', 20))
            end_limit = start_limit + limit

            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)

            queryset_dict = {}
            for event in queryset:
                queryset_dict[event.event_id] = event

            serializer = GoingEventsSerializer(queryset, many=True, context={'user': user, 'qs': queryset_dict})

            return self.get_paginated_response(serializer.data[start_limit:end_limit])

        else:
            return Response({"message:User has no account"}, status=status.HTTP_400_BAD_REQUEST)


class GetGoingUserList(views.APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, id):
        try:
            event = Events.objects.get(event_id=id)

            # Get all going user list
            going_users = event.going_users.all()

            # create Pagination instance
            pagination = LimitOffsetPagination()

            # set pagination size
            pagination.page_size = 20

            profile_list = User.objects.filter(id__in=going_users).prefetch_related('user_profile',
                                                                                    'user_profile_image',
                                                                                    'user_follower').distinct()

            # Pass pagination query
            paginated_data = pagination.paginate_queryset(
                profile_list, request)

            queryset_dict = {}
            for qs_data in profile_list:
                queryset_dict[qs_data.id] = qs_data

            # Serialize profile data
            profile_details_serializer = InterestedUserProfile(
                profile_list, many=True, context={'queryset': queryset_dict})

            return pagination.get_paginated_response(profile_details_serializer.data)

        except Events.DoesNotExist as e:
            raise NotFound(detail="Event doesn't exist")
        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="User Profile Not Found")


class GetYetToDecideUserList(views.APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, id):
        try:
            event = Events.objects.get(event_id=id)

            # Get all yet_to_decide_users list
            yet_to_decide_users = event.yet_to_decide_users.all()

            # create Pagination instance
            pagination = LimitOffsetPagination()

            # set pagination size
            pagination.page_size = 20

            profile_list = User.objects.filter(id__in=yet_to_decide_users).prefetch_related('user_profile',
                                                                                            'user_profile_image',
                                                                                            'user_follower').distinct()

            # Pass pagination query
            paginated_data = pagination.paginate_queryset(
                profile_list, request)

            queryset_dict = {}
            for qs_data in profile_list:
                queryset_dict[qs_data.id] = qs_data

            # Serialize profile data
            profile_details_serializer = InterestedUserProfile(
                profile_list, many=True, context={'queryset': queryset_dict})

            return pagination.get_paginated_response(profile_details_serializer.data)

        except Events.DoesNotExist as e:
            raise NotFound(detail="Event doesn't exist")
        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="User Profile Not Found")
