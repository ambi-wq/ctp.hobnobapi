from rest_framework import serializers
from .models import DeviceRegistry, Notification
from userprofile.models import UserImages


class DeviceRegistrySerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceRegistry
        exclude = ['user']


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        exclude = ['notification_user']


class GetNotificationsListSerializer(serializers.ModelSerializer):
    user_image = serializers.SerializerMethodField('get_user_image')
    activity_user_image = serializers.SerializerMethodField('get_activity_user_image')

    class Meta:
        model = Notification
        # fields = '__all__'
        fields = ['id', 'activity_type','activity_sub_type', 'activity_name', 'activity_user_name', 'is_read', 'flag',
            'created_at', 'notification_user', 'activity_id', 'activity_user', 'user_image', 'message','activity_user_image']

    def get_user_image(self, notifications):
        qs = self.context.get("qs")
        user_img = ""
        try:
            return notifications.activity_user.display_pic.images.url
        except:
            return user_img

        # if qs[event.event_id] == event:
        #     requested_user_id = self.context.get("user")
        #     try:
        #         user_img = qs[event.event_id].user.display_pic.images.url
        #         return user_img
        #     except ObjectDoesNotExist:
        #         return user_img

    def get_activity_user_image(self,notifications):
        image = ""
        if notifications.user_image_id:
            image = notifications.user_image_id.images.url
        return image