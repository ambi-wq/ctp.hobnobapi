from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import DeviceRegistry, Notification
from .serializers import DeviceRegistrySerializer
import json

import requests


class DeviceRegistryTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_device_registry(self):
        payload = {'device_token': 'fyD39HbN0i6mR2awV_xwza:APA91bH84s-xvlmAWQ3HOY5ey2-2GcxL8o-RKYMa8fDsxO0hJ8j-yd0kNgC9eWtxAoFwzcaDQZb_AOscxouLRocakEOW-JLpgjOJ4CwEP08KpM1XqTXyN73wqmsG0kS-QbeImyJVGVx9'}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/notifications/register_device', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_device_registry_header_missing(self):
        payload = {'device_token': 'fyD39HbN0i6mR2awV_xwza:APA91bH84s-xvlmAWQ3HOY5ey2-2GcxL8o-RKYMa8fDsxO0hJ8j-yd0kNgC9eWtxAoFwzcaDQZb_AOscxouLRocakEOW-JLpgjOJ4CwEP08KpM1XqTXyN73wqmsG0kS-QbeImyJVGVx9'}
        # self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/notifications/register_device', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_device_registry_data_missing(self):
        payload = {}
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.post(
            path='/notifications/register_device', data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class NotificationTestCase(APITestCase):

    def setUp(self):
        index = 2

        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
        payload = "{\r\n    \"email\": \"testuser" + \
            str(index) + "@aumtelecom.com\",\r\n    \"password\": \"hobnob_aum\",\r\n    \"returnSecureToken\": true\r\n}"

        headers = {'Content-Type': 'application/json'}

        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        self.token = response['idToken']

    def test_notification_data(self):
        self.client.credentials(HTTP_AUTHORIZATION="JWT " + str(self.token))
        response = self.client.get(
            path='/notifications/notifications',  format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_notification_data_without_header(self):
        response = self.client.get(
            path='/notifications/notifications', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)