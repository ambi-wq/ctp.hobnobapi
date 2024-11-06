from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from userprofile.models import ProfileDetails, Interest, UserImages, UserPreference, InstagramConnect
from userprofile.serializers import ProfileSerializer, InterestSerializer, UserInterestSerializer, UserImageSerializer, UserPreferenceSerializer, InstagramSerializer
from events.models import Events, EventComments
from django.urls import reverse
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth as firebase_auth
import requests


class UserExploreAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_get_all_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/match/explore', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_user_header_missing(self):
        response = self.client.get(
            path='/match/explore', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GetUserLocationAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        # Create Profile
        self.test_create_profile()

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')

    def test_get_user_location(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/match/location', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetReturnUserAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_get_return_user_follower(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/match/return_follower', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetCloseUserAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_get_close_user_follower(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/match/close_friends', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetFollowerAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_get__user_follower(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/match/followers', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetFollowingAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_get__user_following(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/match/following', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CreateUserLocationAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_get_user_location(self):
        payload = {"last_location": {
            "latitude": 20.266525399999985, "longitude": 72.98773509999998}}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/match/location', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UpdateUserLocationAPITestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        # Create Profile
        self.test_create_profile()

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')

    def test_get_user_location(self):
        payload = {"last_location": {
            "latitude": 20.266525399999985, "longitude": 72.98773509999998}}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.put(
            path='/match/location', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)


class AddFollowerAPITestCase(APITestCase):

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

        # Create Profile
        self.test_create_profile()

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')

    def test_add_follower(self):
        payload = {'follower': str(self.user.id)}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/match/add_follower', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
