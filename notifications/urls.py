from django.urls import path, include
from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('register_device', views.DeviceRegisterView.as_view(),
         name="register_device"),
    path('notifications', views.NotificationView.as_view(), name="notifications"),
    #     path('get_notifications_list', views.NotificationsListView.as_view(), name="get_notifications_list"),
    path('get_notifications_list', views.get_notifications_list, name="get_notifications_list"),
    # path('get_notifications_list', views.PurchaseList.as_view, name="get_notifications_list"),

    #   PurchaseList
    #     path('notifications-list', views.NotificationListView.as_view(), name="notifications"),
    path('notifications-read/<id>',
         views.NotificationUpdateView.as_view(), name="notifications_read"),

    path('add_chat_notification', views.AddChatNotification.as_view(), name="add chat notification"),
    path('notification-unread-count', views.NotificationUnread.as_view(), name="notification unread count"),
    path('notification-all-read',views.NotificationAllRead.as_view(),name="notification all read"),
]
