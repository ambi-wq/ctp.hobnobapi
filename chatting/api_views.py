from rest_framework import generics
from rest_framework import views
from .serializers import RoomSerializer, ProfileDataSerializer
from .models import Room
from userprofile.models import ProfileDetails
from matching.models import CloseFriendList
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from hobnob.standard_response import success_response, error_response

User = get_user_model()


class RoomListView(views.APIView):

    def get(self, request):
        # Get User
        user = self.request.user
        print("user", user)

        try:
            # Get User Contact
            user_contact = ProfileDetails.objects.get(uuid=user)
            
            # Get All the Room user is participant
            room_list = user.rooms.all()
            # cfl = CloseFriendList.objects.filter(user = user).values_list('user')

            cfl = CloseFriendList.objects.values_list(
                'user', flat=True).filter(close_friend=user)

            available_list = ProfileDetails.objects.filter(uuid__in = cfl, is_available = True)

            pagination = LimitOffsetPagination()

            paginated_data = pagination.paginate_queryset(
                room_list, request)

            # Serialize Data
            room_serializer = RoomSerializer(room_list, many=True)

            profile = ProfileDetails.objects.get(uuid=user)
            profile_serializer = ProfileDataSerializer(profile)

            # return Response(room_serializer.data, status=status.HTTP_200_OK)
            return pagination.get_paginated_response(data = {"roomlist" : room_serializer.data, "available" : profile_serializer.data})
        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="User Profile Doesn't Exist")

        except Room.DoesNotExist as e:
            raise NotFound(detail="No room has been created yet.")


class RoomView(views.APIView):

    def get(self, request, room_id):
        # Get User
        user = request.user

        try:
            # Filter Room based on Room ID
            room = Room.objects.get(id=room_id, participants__in=[user])

            # Get User Contact
            # profile = ProfileDetails.objects.get(uuid=user)

            # If user is participant then serialize data
            room_seralizer = RoomSerializer(room)

            # Send Response back
            response = success_response(room_seralizer.data)
            return Response(response, status=status.HTTP_200_OK)

            # Check requested user is participant or not
            # if profile in room.participants.all():
            #     # If user is participant then serialize data
            #     room_seralizer = RoomSerializer(room)

            #     # Send Response back
            #     response = success_response(room_seralizer.data)
            #     return Response(response, status=status.HTTP_200_OK)
            # else:
            #     # Response user with No permission message
            #     response = error_response("User is unauthorized to this room")
            #     return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        except Room.DoesNotExist as e:
            raise NotFound(detail="No room has been created yet.")

        except ProfileDetails.DoesNotExist:
            raise NotFound(detail="No profile has been created yet.")

    def post(self, request):
        # Get User
        user = request.user

        # try:
        #     # Other User
        #     other_participant = User.objects.get(id=request.data['participant'])
        # except User.DoesNotExist as e:
        #     return Response({"message":"User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND)

        # Get User & Participant User Contact
        user_contact = ProfileDetails.objects.filter(uuid=user)

        if 'participant' not in request.data:
            return Response({"detail": "Please send Participant Object"}, status=status.HTTP_404_NOT_FOUND)

        if len(user_contact) > 0:
            user_contact = user_contact[0]
        else:
            return Response({"detail": "Your Profile doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

        participant_contact = User.objects.filter(
            pk=request.data['participant'])

        if len(participant_contact) > 0:
            participant_contact = participant_contact[0]
        else:
            return Response({"detail": "Participant Profile doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

        # Get or Create Room
        room_count = Room.objects.create()
        room_count.participants.add(user)
        room_count.participants.add(participant_contact)

        # Serializer Room
        room_serializer = RoomSerializer(room_count)

        response = success_response(room_serializer.data)
        return Response(response, status=status.HTTP_201_CREATED)

    def put(self, request, room_id):
        # Get User
        user = request.user

        try:
            # Filter Room based on Room ID
            room = Room.objects.get(id=room_id)

            # Get User & Participant User Contact
            contact = ProfileDetails.objects.get(uuid=user)

            # Check requested user is participant or not
            if contact in room.participants.all():
                # If user is participant then serialize data
                room_seralizer = RoomSerializer(room, data=request.data)

                # CHeck Data validation
                if room_seralizer.is_valid():
                    # Save Validation Data
                    room_seralizer.save()

                    response = success_response(room_seralizer.data)
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = error_response(room_seralizer.errors)
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

            else:
                # Response user with No permission message
                return Response({"detail": "User is unauthorized to see "}, status=status.HTTP_401_UNAUTHORIZED)

        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="Your Profile doesn't exist")
        except Room.DoesNotExist as e:
            raise NotFound(detail="No room has been created yet.")

    def delete(self, request, room_id):
        # Get User
        user = request.user

        try:
            # Filter Room based on Room ID
            room = Room.objects.get(id=room_id)

            # Get User Contact
            contact = ProfileDetails.objects.get(user=user)

            # Check requested user is participant or not
            if contact in room.participants.all():
                # If user is participant then serialize data
                room.delete()

                # Send Response back
                response = success_response(
                    "Room has been deleted succesfully")
                return Response(response, status=status.HTTP_200_OK)
            else:
                # Response user with No permission message
                return Response({"detail": "User is unauthorized to delete chat"}, status=status.HTTP_401_UNAUTHORIZED)

        except Room.DoesNotExist as e:
            raise NotFound(detail="No room has been created yet.")

        except ProfileDetails.DoesNotExist as e:
            raise NotFound(detail="Your Profile doesn't exist")
