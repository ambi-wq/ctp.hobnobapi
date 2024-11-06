from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from userprofile.models import ProfileDetails, Interest, UserImages, UserPreference, InstagramConnect
from userprofile.serializers import ProfileSerializer, InterestSerializer, UserInterestSerializer, UserImageSerializer, UserPreferenceSerializer, InstagramSerializer
from events.models import Events, EventComments
from chatting.models import Room
from django.urls import reverse
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth as firebase_auth
import requests

# Create your tests here.

class CreateRoomAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        self.user = User.objects.create(
            is_active=True, username='admin', password='123456789', email='test@hobnob.com')

        profile = ProfileDetails.objects.create(
            uuid=self.user, gender='Male', dob='1995-06-10', full_name='Rahul Khairnar')

        self.profile_id = profile.id

        # Create Profile
        self.test_create_profile()

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')

    def test_add_room(self):
        payload = {'participant': str(self.profile_id)}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/chat/room', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    
    def test_add_room_missing_body(self):
        payload = {}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/chat/room', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    
    def test_add_room_wrong_body(self):
        payload = {'payload': str(self.profile_id)}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/chat/room', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetRoomAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        self.user = User.objects.create(
            is_active=True, username='admin', password='123456789', email='test@hobnob.com')

        profile = ProfileDetails.objects.create(
            uuid=self.user, gender='Male', dob='1995-06-10', full_name='Rahul Khairnar')

        self.profile_id = profile.id

        # Create Profile
        self.test_create_profile()

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')

    def test_add_room(self):
        payload = {'participant': str(self.profile_id)}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/chat/room', data=payload, format='json')
        
        self.room = response.json()['id']

    
    def test_get_all_room(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/chat/room_list', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)