import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message
from django.core import serializers
from django.contrib.auth import get_user_model
from .views import get_last_10_message, get_user_id, get_user_contact, get_current_room


User = get_user_model()


class ChatConsumer(WebsocketConsumer):

    user_id = None

    def fetch_messages(self, data):
        try:
            messages = get_last_10_message(self.room_name)
            content = {
                'command': 'messages',
                'messages': self.messages_to_json(messages)
            }

            self.send_message(content)
        except:
            content = {
                'command': 'error',
                'messages': "Room doesn't exists"
            }
            self.send_message(content)

    def new_messages(self, data):
        user_contact = get_user_contact(self.user_id)
        message = Message.objects.create(
            contact=user_contact,
            content=data['message']
        )

        current_room = get_current_room(self.room_name)
        current_room.messages.add(message)
        current_room.save()

        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }

        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'contact': message.contact.user_profile.full_name,
            'content': message.content,
            'display_pic': message.contact.display_pic.images.url,
            'timestamp': str(message.timestamp)
        }

    commands = {
        "fetch_messages": fetch_messages,
        "new_messages": new_messages
    }

    def connect(self):
        query = (self.scope['query_string']).decode("utf-8")
        user_id = query.split('=')[1]
        self.user_id = user_id

        print("User ID ", self.user_id)

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
