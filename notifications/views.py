from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import views
from rest_framework.exceptions import NotFound, ValidationError
from .models import DeviceRegistry, Notification
from .serializers import DeviceRegistrySerializer, NotificationSerializer, GetNotificationsListSerializer
from hobnob.standard_response import success_response, error_response
from hobnob.standard_response import success_response2
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
import datetime
from matching.views import UserExploreView

from django.contrib.auth.models import User
from matching.serializers import UserSerializer
from matching.models import UserContacts, SuggesstedUser
from django.db.models import Q
from django.contrib.gis.measure import D
from userprofile.models import UsersContacts, ProfileDetails
from firebase_admin import messaging

import firebase_admin
from firebase_admin import credentials

from datetime import date
from django.core import serializers
import json


# Create your views here.


class DeviceRegisterView(views.APIView):

    def post(self, request):
        # Get Current User
        current_user = request.user

        # Get FCM Device Token
        try:
            device_token = request.data['device_token']
        except:
            raise NotFound(detail="Please send device token")

        # Check if same object exist
        is_device_register = DeviceRegistry.objects.filter(
            device_token=device_token).exists()

        if is_device_register:
            # Get All Objects
            all_device_token = DeviceRegistry.objects.filter(
                device_token=device_token)

            for token in all_device_token:
                token.delete()

        # If not exist create new objects
        device_registry = DeviceRegistry(user=current_user)

        # Make it serialize
        device_registry_serializer = DeviceRegistrySerializer(
            device_registry, data=request.data)

        # Check Validation
        if device_registry_serializer.is_valid():
            # Save Data
            device_registry_serializer.save()

            # Response back user
            response = success_response(device_registry_serializer.data)
            return Response(response, status=status.HTTP_200_OK)

        # Else Not valid
        else:
            # Response Error
            response = error_response(device_registry_serializer.errors)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class NotificationView(generics.ListAPIView):
    model = Notification
    serializer_class = NotificationSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        # Get User
        user = self.request.user

        # Create Notification Instance and filter all notification for User
        notifications = Notification.objects.filter(
            notification_user=user).order_by('-created_at')

        # return data
        return notifications


# class PurchaseList(generics.ListAPIView):
#     serializer_class = NotificationSerializer

#     def get_queryset(self):
#         """
#         This view should return a list of all the purchases
#         for the currently authenticated user.
#         """
#         user = request.user
#         date = datetime.date.today()
#         start_week = date - datetime.timedelta(date.weekday())
#         print("start_week")
#         this_week = Notification.objects.filter(created_at__range=[start_week, date], 
#                         notification_user=user).order_by('-created_at')
#         print("this_week")
#         this_month = Notification.objects.filter(created_at__year=date.year, created_at__month=date.month, 
#                         created_at__day=start_week.day-1 
#                         , notification_user=user).order_by('-created_at')
#         print("this_month")
#         print("this_week", this_week)
#         print("this_month", this_month)
#         this_week_notifications = success_response(this_week)
#         this_month_notifications = success_response(this_month)


#         return Response(status=status.HTTP_200_OK, data={"message": "Success", "this_week": this_week_notifications
#                     ,"this_month":this_month_notifications})

# Currently used aPI================
@api_view(['GET'])
def get_notifications_list(request):
    user = request.user
    date = datetime.date.today()
    # last_monday = date - datetime.timedelta(days=date.weekday())

    start_week = date - datetime.timedelta(days=date.weekday())
    end_week = date + datetime.timedelta(days=-date.weekday(), weeks=1)
    print(f"{user=}")
    print("data", start_week, date, start_week.day)
    # this_week = Notification.objects.filter(notification_user=user)
    # previous query
    # this_week = Notification.objects.filter(notification_user=user,created_at__range=[start_week, end_week]).order_by('-created_at')

    # # new query
    # this_week_list = Notification.objects.filter(notification_user=user,
    #                                              created_at__range=[start_week, end_week]).exclude(
    #     activity_sub_type='message').order_by(
    #     'activity_user_name', 'activity_type', 'activity_name', 'user_image_id', '-created_at').distinct(
    #     'activity_user_name',
    #     'activity_type',
    #     'activity_name', 'user_image_id').values_list(
    #     'id', flat=True)
    #
    # this_week = Notification.objects.filter(id__in=this_week_list).order_by('-created_at')
    # print("this _week", this_week)

    this_week = Notification.objects.filter(notification_user=user, created_at__range=[start_week, end_week]).order_by(
        '-created_at')

    activity = []
    ids = []
    result = list(this_week)
    for n in this_week:
        if n.activity_sub_type in ['event_yettodecide', 'event_going', 'event_interested']:
            print(activity,"====")
            if n.activity_id_id in activity:
                ids.append(n.id)
                # result.remove(n.id)
            else:
                activity.append(n.activity_id_id)
    print(f"{ids=}")
    print(f"{result=}")
    this_week = Notification.objects.filter(notification_user=user, created_at__range=[start_week, end_week]).exclude(activity_sub_type='message',id__in=ids).order_by(
        '-created_at')
    print(this_week.query)
    this_week_serializer = GetNotificationsListSerializer(this_week, many=True)
    # print("sample", this_week)

    # prev query
    # this_month = Notification.objects.filter(created_at__year=date.year, created_at__month=date.month, created_at__day__lte = start_week.day-1,
    #                notification_user=user).order_by('-created_at')

    # new query
    this_month_list = Notification.objects.filter(created_at__year=date.year, created_at__month=date.month,
                                                  created_at__day__lte=start_week.day - 1,
                                                  notification_user=user).exclude(activity_sub_type='message').order_by(
        'activity_user_name',
        '-created_at').distinct(
        'activity_user_name').values_list('id', flat=True)

    this_month = Notification.objects.filter(id__in=this_month_list).order_by('-created_at')

    # print("this month", this_month)

    this_month_serializer = GetNotificationsListSerializer(this_month, many=True)

    # prev query
    # follow_list = Notification.objects.filter(notification_user=user, activity_type = "following", flag=False).order_by('-created_at')

    # new query
    # follow_list_new = Notification.objects.filter(notification_user=user, activity_type="following", flag=False,is_read=False).order_by('activity_user_name','-created_at').distinct('activity_user_name').values_list('id',flat=True)
    # follow_list_new = Notification.objects.filter(notification_user=user, activity_sub_type="following", flag=False,
    #                                               is_read=False).order_by('activity_user_name', '-created_at').distinct(
    #     'activity_user_name').values_list('id', flat=True)
    #
    #
    # follow_list = Notification.objects.filter(id__in=follow_list_new).order_by('-created_at')

    # follow_list_new = Notification.objects.filter(notification_user=user, activity_sub_type="following", flag=False,
    #                                               is_read=False).order_by('activity_user_name', '-created_at').distinct(
    #     'activity_user_name').values('id', 'activity_user', 'notification_user')

    follow_list_new = Notification.objects.filter(notification_user=user, activity_sub_type="following", flag=True,
                                                  is_read=True).order_by('activity_user_name', '-created_at').distinct(
        'activity_user_name').values('id', 'activity_user', 'notification_user')

    ids = []
    for fl in follow_list_new:
        if UserContacts.objects.filter(follower=fl["activity_user"], following=fl["notification_user"]).exists():
            print("not include")
        else:
            ids.append(fl['id'])

    follow_list = Notification.objects.filter(id__in=ids).order_by('-created_at')

    follow_list_serializer = GetNotificationsListSerializer(follow_list, many=True)
    # print("this month serializer", this_month_serializer.data)

    this_week_notifications = success_response2(this_week_serializer.data)
    this_month_notifications = success_response2(this_month_serializer.data)
    follow_list_notifications = success_response2(follow_list_serializer.data)
    # print("this month notifications", this_month_notifications)

    # Check If user exists in db
    suggesteduser_list = SuggesstedUser.objects.filter(user=user).values_list('suggessted_user', flat=True)
    # Get phone of suggessted user
    user_phone = User.objects.filter(id__in=suggesteduser_list).values_list('user_profile__phone')
    # Excluse suggessted user contact and add new one
    contactsLst = [contact.contact_number for contact in
                   UsersContacts.objects.filter(user=user.id).exclude(contact_number__in=user_phone)]
    # Get profile of new contact user and remove users who already following
    users = User.objects.filter(user_profile__active=True, user_profile__phone__in=contactsLst).exclude(
        user_follower__following=user)

    # Check if there is data
    if users:
        # insert record
        for suggess_user in users:
            SuggesstedUser.objects.create(user=user, suggessted_user=suggess_user)

    if suggesteduser_list:
        current_user = User.objects.filter(username=user).prefetch_related(
            'user_profile', 'preference', 'user_profile__interest', 'score', 'geo_location')[0]

        queryset = User.objects.filter(id__in=suggesteduser_list)
        queryset_dict = {}
        for qs_data in queryset:
            queryset_dict[qs_data.id] = qs_data

        user_serializer = UserSerializer(queryset, many=True,
                                         context={'user_id': current_user, 'queryset': queryset_dict})

        # Sorting functions
        # def desirable_score(profile):
        #     return profile['desirable_score']

        # Updated Sorted Data.
        # user_sorted_data = sorted(user_serializer.data, key=desirable_score, reverse=True)
        user_sorted_data = user_serializer.data

        suggesstions = success_response2(user_sorted_data)

    else:
        print("else==========")
        suggesstions = UserExploreView().as_view()(request._request).render().data

    return Response(status=status.HTTP_200_OK, data={"message": "Success", "this_week": this_week_notifications
        , "this_month": this_month_notifications, "follow_list": follow_list_notifications,
                                                     "suggested_section": suggesstions})


# ================test==========================
# @api_view(['GET'])
# def get_notifications_list(request):
#     user = request.user
#     date = datetime.date.today()
#     # last_monday = date - datetime.timedelta(days=date.weekday())
#
#     start_week = date - datetime.timedelta(days = date.weekday())
#     end_week = date + datetime.timedelta(days=-date.weekday(), weeks=1)
#     print("data", start_week, date, start_week.day)
#
#     # Get Current User
#     current_user = User.objects.get(username=user)
#
#     # Get Min & Max Age Year
#     current_year = datetime.datetime.now().year
#     min_age_year = current_year - current_user.preference.min_age
#     max_age_year = current_year - current_user.preference.max_age
#
#     # this_week = Notification.objects.filter(notification_user=user)
#     #previous query
#     #this_week = Notification.objects.filter(notification_user=user,created_at__range=[start_week, end_week]).order_by('-created_at')
#
#     #new query
#     this_week_list = Notification.objects.filter(notification_user=user,
#                 created_at__range=[start_week, end_week]).order_by('activity_user_name','-created_at').distinct('activity_user_name').values_list('id',flat=True)
#
#
#     this_week =  Notification.objects.filter(id__in=this_week_list).order_by('-created_at')
#     #print("this _week", this_week)
#
#     this_week_serializer = GetNotificationsListSerializer(this_week, many=True)
#     #print("sample", this_week)
#
#     #prev query
#     # this_month = Notification.objects.filter(created_at__year=date.year, created_at__month=date.month, created_at__day__lte = start_week.day-1,
#     #                notification_user=user).order_by('-created_at')
#
#     #new query
#     this_month_list = Notification.objects.filter(created_at__year=date.year, created_at__month=date.month,
#                                              created_at__day__lte=start_week.day - 1,
#                                              notification_user=user).order_by('activity_user_name','-created_at').distinct('activity_user_name').values_list('id',flat=True)
#
#     this_month = Notification.objects.filter(id__in=this_month_list).order_by('-created_at')
#
#     #print("this month", this_month)
#
#     this_month_serializer = GetNotificationsListSerializer(this_month, many=True)
#
#     #prev query
#     # follow_list = Notification.objects.filter(notification_user=user, activity_type = "following", flag=False).order_by('-created_at')
#
#     #new query
#     follow_list_new = Notification.objects.filter(notification_user=user, activity_type="following", flag=False).order_by('activity_user_name','-created_at').distinct('activity_user_name').values_list('id',flat=True)
#     follow_list = Notification.objects.filter(id__in=follow_list_new).order_by('-created_at')
#
#     follow_list_serializer = GetNotificationsListSerializer(follow_list, many=True)
#     # print("this month serializer", this_month_serializer.data)
#
#     this_week_notifications = success_response2(this_week_serializer.data)
#     this_month_notifications = success_response2(this_month_serializer.data)
#     follow_list_notifications = success_response2(follow_list_serializer.data)
#     #print("this month notifications", this_month_notifications)
#
#     #Suggessted Section
#
#     # Check User Interest
#     user_interests = current_user.user_profile.interest.all()
#
#     contactsLst = [contact.contact_number for contact in UsersContacts.objects.filter(user=current_user.id)]
#
#     if len(user_interests) > 0:
#         filter_user = User.objects.filter(geo_location__last_location__distance_lte=(
#         current_user.geo_location.last_location, D(km=current_user.preference.radius)),
#                                           user_profile__dob__year__gte=max_age_year, user_profile__active=True,
#                                           user_profile__dob__year__lte=min_age_year,
#                                           user_profile__interest__in=current_user.user_profile.interest.all()).exclude(
#             Q(user_follower__following=user) | Q(username=user)).order_by('-score__desirable_score',
#                                                                           'geo_location__last_location').prefetch_related(
#             'user_profile', 'display_pic', 'user_profile_image', 'user_profile__interest', 'preference',
#             'user_follower', 'score', 'geo_location').distinct()
#     else:
#         filter_user = User.objects.filter(geo_location__last_location__distance_lte=(
#         current_user.geo_location.last_location, D(km=current_user.preference.radius)),
#                                           user_profile__dob__year__gte=max_age_year, user_profile__active=True,
#                                           user_profile__dob__year__lte=min_age_year).exclude(
#             Q(user_follower__following=user) | Q(username=user)).order_by('-score__desirable_score',
#                                                                           'geo_location__last_location').prefetch_related(
#             'user_profile', 'user_profile_image', 'display_pic', 'user_profile__interest', 'preference',
#             'user_follower', 'score', 'geo_location').distinct()
#
#     filter_user = filter_user.exclude(user_profile__phone__in=contactsLst)
#     print(filter_user,"====")
#
#     #Contact Sync
#     contactsLst = [contact.contact_number for contact in UsersContacts.objects.filter(user=current_user.id)]
#     print(f"{contactsLst=}")
#     # previous query
#     # filter_user2 = User.objects.filter(user_profile__active=True, user_profile__phone__in=contactsLst).prefetch_related('user_profile', 'display_pic', 'user_profile_image','user_profile__interest', 'preference', 'user_follower','score', 'geo_location').distinct()
#
#     # new query
#     filter_user2 = User.objects.filter(user_profile__active=True, user_profile__phone__in=contactsLst).exclude(
#         user_follower__following=user).prefetch_related('user_profile', 'display_pic', 'user_profile_image',
#                                                         'user_profile__interest', 'preference', 'user_follower',
#                                                         'score', 'geo_location').distinct()
#     print(f"{filter_user2=}")
#
#     # Get Mutual Followers
#
#     followerList = [follower.follower for follower in UserContacts.objects.filter(following=user)]
#     print(f"{followerList=}")
#
#     mutual_follower_list = User.objects.filter(user_profile__active=True,
#                                                user_follower__following__in=followerList).exclude(
#         Q(username=user) | Q(username__in=followerList)).prefetch_related('user_profile', 'display_pic',
#                                                                           'user_profile_image',
#                                                                           'user_profile__interest', 'preference',
#                                                                           'user_follower', 'score',
#                                                                           'geo_location').distinct()
#     print(f"{mutual_follower_list=}")
#
#     final_user = filter_user2 | mutual_follower_list
#
#     #both filter_user and final_user combine
#     current_user1 = User.objects.filter(username=user).prefetch_related(
#         'user_profile', 'preference', 'user_profile__interest', 'score', 'geo_location', 'user_following')[0]
#     queryset_dict = {}
#     for qs_data2 in final_user:
#         queryset_dict[qs_data2.id] = qs_data2
#
#     for qs_data in filter_user:
#         queryset_dict[qs_data.id] = qs_data
#
#     contact_serializer = UserSerializer(filter_user, many=True,context={'user_id': current_user1, 'queryset': queryset_dict})
#     serializer = UserSerializer(final_user, many=True, context={'user_id': current_user1, 'queryset': queryset_dict})
#
#     # Sorting functions
#     def desirable_score(profile):
#         return profile['desirable_score']
#
#     # Updated Sorted Data
#     contacts_sorted_data = sorted(
#         contact_serializer.data, key=desirable_score, reverse=True)
#
#     sorted_data = sorted(
#         serializer.data, key=desirable_score, reverse=True)
#
#     total_explore_data = contacts_sorted_data + sorted_data
#
#     # New Change :- As of now only 15 suggestions fetching
#     final_data = []
#     final_data = [d for d in total_explore_data if d not in final_data]
#
#     total_explore_data = final_data[:15]
#     print(f"{total_explore_data=}")
#
#     suggesstions = success_response2(total_explore_data)
#
#     # suggesstions = UserExploreView().as_view()(request._request).render().data
#
#     return Response(status=status.HTTP_200_OK, data={"message": "Success", "this_week": this_week_notifications
#                     ,"this_month":this_month_notifications, "follow_list" : follow_list_notifications,"suggested_section":suggesstions})


# ==================test ends=======================


# class NotificationsListView(views.APIView):

#     def get(self, request):
#         print("user", request.user)
#         # Make query to check if username exists or not
#         is_username_exist = ProfileDetails.objects.filter(
#             username=request.user).exists()
#         # If Exist
#         if is_username_exist:
#             standard_response = success_response({"available": False})
#             return Response(standard_response, status=status.HTTP_200_OK)
#         else:
#             standard_response = success_response({"available": True})
#             return Response(standard_response, status=status.HTTP_200_OK)


# class NotificationListView(generics.ListAPIView):
#     model = Notification
#     serializer_class = NotificationSerializer
#     pagination_class = LimitOffsetPagination

#     def get_queryset(self):
#         # Get User
#         user = self.request.user

#         current_date = datetime.date.today()
#         start_week = date - datetime.timedelta(date.weekday())
#         # Create Notification Instance and filter all notification for User
#         # notifications = Notification.objects.filter(
#         #     notification_user=user, is_read=False).order_by('-created_at')
#         notifications = Notification.objects.filter(created_at__range=[start_week, current_date], 
#                         notification_user=user).order_by('-created_at')
# # end_week = start_week + datetime.timedelta(7)
# # entries = Entry
#         # return data
#         return notifications


class NotificationUpdateView(views.APIView):

    def put(self, request, id):
        # Get User
        current_user = request.user

        try:
            # Query notification based on id
            notification = Notification.objects.get(id=id)

            # Check user is same as notification user
            if notification.notification_user == current_user:
                # Both user same then, mark user as read
                notification.is_read = True
                notification.flag = True

                # save data
                notification.save()

                # Pass to serializer
                notification_serializer = NotificationSerializer(notification)

                # Return data
                response = success_response(notification_serializer.data)
                return Response(response, status=status.HTTP_200_OK)
            else:
                raise ValidationError(
                    detail="User doesn't have permission to update")

        except Notification.DoesNotExist:
            raise NotFound(detail="Notification ID doesn't exist")


class AddChatNotification(views.APIView):

    def post(self, request):
        try:
            # Request Data
            fromUser = request.data['fromUser']
            toUser = request.data['toUser']
            message = request.data['message']

            fromuser_id = User.objects.get(username=fromUser)
            touser_id = User.objects.get(username=toUser)

            user_profile = ProfileDetails.objects.get(uuid=fromuser_id.id)

            message_body = '''<p style="font-family:'Quicksand'; color:#363636"><b style="color : #080808">{0}</b> has sent you a message : {1}</p>'''.format(
                user_profile.username, message)

            Notification.objects.create(activity_type="user", activity_sub_type="message",
                                        activity_user_name=user_profile.username, message=message_body,
                                        activity_user_id=fromuser_id.id, notification_user_id=touser_id.id)

            # Get User Device List
            device_list = DeviceRegistry.objects.filter(user=touser_id)

            # Build Message
            if device_list.count() > 0:
                registration_tokens = [
                    devices.device_token for devices in device_list]

                title = 'Hobnob'
                body = '{0} has sent you a message : {1}'.format(user_profile.username, message)

                # comment below 2 line while deploying
                # cred = credentials.Certificate("credentials/serviceAccountKey.json")
                # firebase_admin.initialize_app(cred)

                message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data={'type': 'UserChat', 'id': str(fromuser_id.id)},
                    tokens=registration_tokens,
                )

                # Send a message to the device corresponding to the provided
                # registration token.
                response = messaging.send_multicast(message)

                print('User Chat Notification Sent')

            return Response({"message": "Notification sent successfully", "status": True})
        except User.DoesNotExist as ue:
            return Response({"message": "User doesn't exist", "status": False})
        except ProfileDetails.DoesNotExist as pr:
            return Response({"message": "Profile doesn't exist", "status": False})
        except Exception as e:
            print(e)
            return Response({"message": "Something went wrong", "status": False})


class NotificationUnread(views.APIView):

    def get(self, request):
        user = request.user
        date = datetime.date.today()
        count = 0
        notification = Notification.objects.filter(notification_user=user, flag=False, is_read=False,
                                                   created_at__year=date.year, created_at__month=date.month).exclude(
            activity_sub_type='message').values().order_by(
            'activity_user_name', 'activity_type', 'activity_name', 'user_image_id', '-created_at').distinct(
            'activity_user_name',
            'activity_type',
            'activity_name', 'user_image_id')
        count = len(notification)

        if notification:
            # Remove count of showing interst in same event
            for notify in notification:
                if notify['activity_sub_type'] in ['event_yettodecide', 'event_going', 'event_interested']:
                    events = Notification.objects.filter(notification_user=user,
                                                         activity_id_id=notify['activity_id_id']).exclude(
                        id=notify['id'])
                    if events:
                        count -= 1

        return Response(status=status.HTTP_200_OK, data={"count": count})


class NotificationAllRead(views.APIView):

    def put(self, request):
        try:
            user = request.user
            notification = Notification.objects.filter(notification_user=user).update(is_read=True, flag=True)
            return Response(status=status.HTTP_200_OK, data={"message": "notification modified successfully"})
        except Exception as e:
            print(e)
            return Response({"message": "Something went wrong", "status": False})
