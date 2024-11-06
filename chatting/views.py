from django.shortcuts import render, get_object_or_404
from .models import Room
from userprofile.models import ProfileDetails
from firebase_admin import auth
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.


def index(request):
    return render(request, 'chat/index.html')


def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })


def get_last_10_message(room_id):
    room = get_object_or_404(Room, id=room_id)
    return room.messages.order_by('-timestamp').all()[:10]


def get_user_id(id_token):
    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']
    print(uid)
    return uid


def get_user_contact(user_id):
    user = get_object_or_404(User, username=user_id)
    # return get_object_or_404(ProfileDetails, uuid=user)
    return user


def get_current_room(room_id):
    return get_object_or_404(Room, id=room_id)
