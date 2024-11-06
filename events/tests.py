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

import os
import io

from PIL import Image



# Create your tests here.


class MissingValueEventsTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        self.interest_list = []

        print('I am running')

        # Create Interest
        interest = Interest.objects.create(interest_name="Music")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Dance")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Film")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Comedy")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Art")
        self.interest_list.append(interest.interest_id)

    def test_create_name_missing_event(self):
        print('Name Missing')
        data = {"event_location": {"latitude": 73.79296895116568, "longitude": 19.147243919468494},  "event_type": "Public", "description": "Launch",
                "location": "Pune, IN", "event_date": "2020-08-30", "event_time_from": "08:00:00", "event_time_to": "21:00:00", "event_price": 0.0, "event_interest": []}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/event', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_interest_missing_event(self):
        print('Interest  Missing')
        data = {"event_location": {"latitude": 73.79296895116568, "longitude": 19.147243919468494}, "event_name": "Start Festival", "event_type": "Public", "description": "Launch",
                "location": "Pune, IN", "event_date": "2020-08-30", "event_time_from": "08:00:00", "event_time_to": "21:00:00", "event_price": 0.0}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/event', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_date_time_missing_event(self):
        print('Datetime  Missing')
        data = {"event_location": {"latitude": 73.79296895116568, "longitude": 19.147243919468494}, "event_name": "Start Festival", "event_type": "Public", "description": "Launch",
                "location": "Pune, IN", "event_price": 0.0, "event_interest": []}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/event', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_location_missingcreate_event(self):
        print('Location Missing')
        data = {"event_name": "Start Festival", "event_type": "Public", "description": "Launch",
                "location": "Pune, IN", "event_date": "2020-08-30", "event_time_from": "08:00:00", "event_time_to": "21:00:00", "event_price": 0.0, "event_interest": self.interest_list}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/event', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CreateEventsTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        self.interest_list = []

        # Create Interest
        interest = Interest.objects.create(interest_name="Music")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Dance")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Film")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Comedy")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Art")
        self.interest_list.append(interest.interest_id)

        print(self.interest_list)

    def test_create_event(self):
        print('Event Create 1')
        data = {"event_location": {"latitude": 73.79296895116568, "longitude": 19.147243919468494}, "event_name": "Start Festival", "event_type": "Public", "description": "Launch",
                "location": "Pune, IN", "event_date": "2020-08-30", "event_time_from": "08:00:00", "event_time_to": "21:00:00", "event_price": 0.0, "event_interest": self.interest_list}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/event', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class GetAllPublicEventsTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        self.interest_list = []

        # Create Interest
        interest = Interest.objects.create(interest_name="Music")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Dance")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Film")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Comedy")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Art")
        self.interest_list.append(interest.interest_id)

        print("Interest list 2", self.interest_list)

        # # Create Profile
        self.test_create_profile()

        # # Set Pref
        self.test_set_preference()

        # Create Events
        self.test_set_preference()

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')

        print('Profile', response.json())

    def test_set_preference(self):
        data = {'opposite_gender': 'Both',
                'min_age': '20',
                'max_age': '50',
                'radius': '100'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/preference', data=data, format='json')

        print('Pref', response.json())

    def test_create_event(self):
        print('Event Create 2')
        data = {"event_location": {"latitude": 72.9877350999, "longitude": 20.147243919468494}, "event_name": "Start Festival", "event_type": "Public", "description": "Launch",
                "location": "Pune, IN", "event_date": "2020-08-30", "event_time_from": "08:00:00", "event_time_to": "21:00:00", "event_price": 0.0, "event_interest": [1, 2, 3]}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/event', data=data, format='json')

        print('Event Created', response.json())

    def test_get_all_public_events(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/all_events', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_upcoming_events(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/upcoming_events', format='json')
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_past_events(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/past_events', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_user_events(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/user_events_list', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_curated_events(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/currated_events', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllPublicEventsMissingHeaderTestCase(APITestCase):

    def test_get_all_public_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/all_events', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_upcoming_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/upcoming_events', format='json')
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_past_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/past_events', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_user_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/user_events_list', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_curated_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/currated_events', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CommentsTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        user = User.objects.create(
            is_active=True, username='admin', password='123456789', email='test@hobnob.com')

        print("User Comment", user)

        self.interest_list = []

        # Create Interest
        interest = Interest.objects.create(interest_name="Music")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Dance")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Film")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Comedy")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Art")
        self.interest_list.append(interest.interest_id)

        # Create Profile
        profile = ProfileDetails.objects.create(
            uuid=user, gender='Male', dob='1995-06-10', full_name='Rahul Khairnar')

        # Set Pref
        pref = UserPreference.objects.create(
            user=user, opposite_gender='Female')

        # Create Events
        events = Events.objects.create(user=user, event_name='Test', event_type='Public', description='Description',
                                       location='Mumbai', event_date='2020-09-30', event_time_from='14:00', event_time_to='21:00')
        events.event_interest.add(interest)

        print(events.event_id)
        self.event_id = events.event_id

    def test_create_event(self):
        print('Event Create 2')
        data = {'event': str(self.event_id), 'comment': 'Test Comment'}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/comments', data=data, format='json')

        print('Event Created', response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CommentsMissingDataTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        user = User.objects.create(
            is_active=True, username='admin', password='123456789', email='test@hobnob.com')

        print("User Comment", user)

        self.interest_list = []

        # Create Interest
        interest = Interest.objects.create(interest_name="Music")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Dance")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Film")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Comedy")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Art")
        self.interest_list.append(interest.interest_id)

        # Create Profile
        profile = ProfileDetails.objects.create(
            uuid=user, gender='Male', dob='1995-06-10', full_name='Rahul Khairnar')

        # Set Pref
        pref = UserPreference.objects.create(
            user=user, opposite_gender='Female')

        # Create Events
        events = Events.objects.create(user=user, event_name='Test', event_type='Public', description='Description',
                                       location='Mumbai', event_date='2020-09-30', event_time_from='14:00', event_time_to='21:00')
        events.event_interest.add(interest)

        print(events.event_id)
        self.event_id = events.event_id

    def test_create_event_comment_missing(self):
        data = {'event': str(self.event_id)}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/comments', data=data, format='json')

        print('Event Created', response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_event(self):
        print('Event Create 2')
        data = {'comment': 'Test Comment'}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/comments', data=data, format='json')

        print('Event Created', response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CommentsReplyTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        user = User.objects.create(
            is_active=True, username='admin', password='123456789', email='test@hobnob.com')

        print("User Comment", user)

        self.interest_list = []

        # Create Interest
        interest = Interest.objects.create(interest_name="Music")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Dance")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Film")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Comedy")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Art")
        self.interest_list.append(interest.interest_id)

        # Create Profile
        profile = ProfileDetails.objects.create(
            uuid=user, gender='Male', dob='1995-06-10', full_name='Rahul Khairnar')

        # Set Pref
        pref = UserPreference.objects.create(
            user=user, opposite_gender='Female')

        # Create Events
        events = Events.objects.create(user=user, event_name='Test', event_type='Public', description='Description',
                                       location='Mumbai', event_date='2020-09-30', event_time_from='14:00', event_time_to='21:00')
        events.event_interest.add(interest)

        print(events.event_id)
        self.event_id = events.event_id

        comments = EventComments.objects.create(
            event=events, comment_user=user, comment="Nice")

        self.comment_id = comments.comment_id

    def test_create_comments(self):
        print('Event Create 2')
        data = {'event': str(
            self.event_id), 'comment': 'Test Comment', 'reply': str(self.comment_id)}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/comments', data=data, format='json')

        print('Event Created', response.json())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CommentsListTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        user = User.objects.create(
            is_active=True, username='admin', password='123456789', email='test@hobnob.com')

        print("User Comment", user)

        self.interest_list = []

        # Create Interest
        interest = Interest.objects.create(interest_name="Music")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Dance")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Film")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Comedy")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Art")
        self.interest_list.append(interest.interest_id)

        # Create Profile
        profile = ProfileDetails.objects.create(
            uuid=user, gender='Male', dob='1995-06-10', full_name='Rahul Khairnar')

        # Set Pref
        pref = UserPreference.objects.create(
            user=user, opposite_gender='Female')

        # Create Events
        events = Events.objects.create(user=user, event_name='Test', event_type='Public', description='Description',
                                       location='Mumbai', event_date='2020-09-30', event_time_from='14:00', event_time_to='21:00')
        events.event_interest.add(interest)

        print(events.event_id)
        self.event_id = events.event_id

        comments = EventComments.objects.create(
            event=events, comment_user=user, comment="Nice")

        self.comment_id = comments.comment_id

    def test_get_all_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/all_comments/' + str(self.event_id),  format='json')

        print('Event Created', response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/comments/' + str(self.comment_id),  format='json')

        print('Event Created', response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.delete(
            path='/events/comments/' + str(self.comment_id),  format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GetPublicPrivateEventsTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        self.interest_list = []

        # Create Interest
        interest = Interest.objects.create(interest_name="Music")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Dance")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Film")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Comedy")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Art")
        self.interest_list.append(interest.interest_id)

        print("Interest list 2", self.interest_list)

        # # Create Profile
        self.test_create_profile()

        # # Set Pref
        self.test_set_preference()

        # Create Events
        self.test_set_preference()

    def test_create_profile(self):
        data = {'full_name': 'Rahul Khairnar',
                'gender': 'Male',
                'dob': '1995-06-10'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/create_profile', data=data, format='json')

        print('Profile', response.json())

    def test_set_preference(self):
        data = {'opposite_gender': 'Both',
                'min_age': '20',
                'max_age': '50',
                'radius': '100'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/profile/preference', data=data, format='json')

        print('Pref', response.json())

    def test_create_event(self):
        print('Event Create 2')
        data = {"event_location": {"latitude": 72.9877350999, "longitude": 20.147243919468494}, "event_name": "Start Festival", "event_type": "Public", "description": "Launch",
                "location": "Pune, IN", "event_date": "2020-08-30", "event_time_from": "08:00:00", "event_time_to": "21:00:00", "event_price": 0.0, "event_interest": [1, 2, 3]}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/event', data=data, format='json')

        print('Event Created', response.json())

    def test_get_all_public_events(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/public-events', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_private_events(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/private-events', format='json')
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_interested_events(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/interested-events', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_curated_events(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/currated_events', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetAllPublicEventsMissingHeaderTestCase(APITestCase):

    def test_get_all_interested_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/interested-events', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_peivate_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/private-events', format='json')
        print(response.status_code)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_public_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/public-events', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_user_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/user_events_list', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_curated_events(self):
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/events/currated_events', format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AddEventImageTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

        self.interest_list = []

        # Create Interest
        interest = Interest.objects.create(interest_name="Music")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Dance")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Film")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Comedy")
        self.interest_list.append(interest.interest_id)
        interest = Interest.objects.create(interest_name="Art")
        self.interest_list.append(interest.interest_id)

        print(self.interest_list)

    def test_create_event(self):
        data = {"event_location": {"latitude": 73.79296895116568, "longitude": 19.147243919468494}, "event_name": "Start Festival", "event_type": "Public", "description": "Launch",
                "location": "Pune, IN", "event_date": "2020-08-30", "event_time_from": "08:00:00", "event_time_to": "21:00:00", "event_price": 0.0, "event_interest": self.interest_list}

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/events/event', data=data, format='json')

        return response.json()

    def generate_photo_file(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_add_event_img(self):
        """
        Test if we can upload a photo
        """

        event_id = self.test_create_event()['event_id']

        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))

        url = '/events/event_img'

        photo_file = self.generate_photo_file()

        data = {
            'event': event_id,
            'event_img': photo_file
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
