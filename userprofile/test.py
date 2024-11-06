import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth as firebase_auth
import requests

cred = credentials.Certificate("D:\Ambika\Python Workspace\HobNubAPI\ctp.hobnobapi\credentials\serviceAccountKey.json")
firebase_admin.initialize_app(cred)


custom_token = firebase_auth.create_custom_token(
    'WPB4XONlZ8MrFzjHkSmVOPdu5Yv1')

custom_token = custom_token.decode("utf-8")

url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key=AIzaSyA8mJo7AAmiinLfny3Gpq2IXWxEWfIlPUM"
payload = "{\r\n    \"token\": \"" + \
          str(custom_token) + "\",\r\n    \"returnSecureToken\": true\r\n}"

headers = {'Content-Type': 'application/json'}

response = requests.request("POST", url, headers=headers, data=payload)
response = response.json()
print(response['idToken'],"===========")