from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from userprofile.models import ProfileDetails, Interest, UserImages, UserPreference, InstagramConnect, PromptQuestions
from userprofile.serializers import ProfileSerializer, InterestSerializer, UserInterestSerializer, UserImageSerializer, UserPreferenceSerializer, InstagramSerializer
from django.urls import reverse
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth as firebase_auth
import requests

import os
import io

from PIL import Image


# cred = credentials.Certificate("credentials/serviceAccountKey.json")
# firebase_admin.initialize_app(cred)

# Create your tests here.


class BirthdayMissingUserProfileTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'username': 'rahulkhairnarr',
                'gender': 'Male'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class NameMissingUserProfileTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_create_profile(self):
        data = {
            'gender': 'Male',
            'username': 'rahulkhairnarr',
            'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GenderMissingUserProfileTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'username': 'rahulkhairnarr',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UsernameMissingUserProfileTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CreateUserProfileTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetUserProfileTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']
        self.test_create_profile()

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'username': 'rahulkhairnarr',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')

    def test_get_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(path='/profile/get_profile')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetInterestTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_get_interest(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(path='/profile/interest_list')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OppositeGenderMissingPreferenceTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_set_preference(self):
        data = {'min_age': '20',
                'max_age': '30',
                'radius': '50'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/preference', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MinAgeBiggerPreferenceTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_set_preference(self):
        data = {'opposite_gender': 'Female',
                'min_age': '40',
                'max_age': '30',
                'radius': '50'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/preference', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SetUserPreferenceTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_set_preference(self):
        data = {'opposite_gender': 'Female',
                'min_age': '20',
                'max_age': '30',
                'radius': '50'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/preference', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UpdateUserPreferenceTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']
        self.test_set_preference()

    def test_set_preference(self):
        data = {'opposite_gender': 'Female',
                'min_age': '20',
                'max_age': '30',
                'radius': '50'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/preference', data=data, format='json')
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_preference(self):
        data = {'opposite_gender': 'Female',
                'min_age': '21',
                'max_age': '30',
                'radius': '50'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.put(
            path='/profile/preference', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SpotifyAPITestCase(APITestCase):

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
        self.test_connect_spotify()

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'username': 'rahulkhairnarr',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')

    def test_connect_spotify(self):
        payload = {'code': 'AQAsj01rbcGW0EgYdMOAYGyY0_pAMLD_9gbqQCQK6p9Dz52qBhXaWFEb6df6_rkDExm39-7BQbj805X_feZeEgaPlvfZm-9yc4xDCpxD8ESLB_w-Sh2UQq86rF5wTFwkCVmd_MczA5ejz7PjrRTkUISNzNtIOA_HZvHrJXDHJMkWs2Yr362WztM1X7uQQNvnAPYZ7kGzD6IlDQ'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/connect-spotify', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_spotify(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/profile/connect-spotify', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CoverImageTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_cover_photo(self):
        """
        Test if we can upload a photo
        """

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))

        url = '/profile/images'

        photo_file = self.generate_photo_file()

        data = {
            'images': photo_file
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DisplayPictureTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_display_picture(self):
        """
        Test if we can upload a photo
        """

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))

        url = '/profile/display-pic'

        photo_file = self.generate_photo_file()

        data = {
            'images': photo_file
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class UsernameVerificationTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_get_interest(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/profile/check_username/rahulkhairnarr')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PrompQAListTestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_get_promptqa(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/profile/promptqa')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UpdatePrompQATestCase(APITestCase):

    def setUp(self):
        self.custom_token = firebase_auth.create_custom_token(
            'bp56irOEhmQUSRayXAYKth54jYI2')

        self.custom_token = self.custom_token.decode("utf-8")

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"token\": \"" + \
            str(self.custom_token)+"\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        # create test question
        prompt_qa = PromptQuestions.objects.create(
            question="A review by a friend")

        self.qa_id = prompt_qa.id

    def test_update_promptqa(self):
        data = {'answer': 'Test Case',
                'id': self.qa_id}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.put(
            path='/profile/promptqa', data=data, format='json')

    def test_get_promptqa(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/profile/promptqa')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
