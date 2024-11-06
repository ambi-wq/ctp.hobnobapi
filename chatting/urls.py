from django.urls import path, include
from chatting import views
from chatting import api_views

app_name = 'chatting'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
    path('room_list', api_views.RoomListView.as_view(), name='room_list'),
    path('room', api_views.RoomView.as_view(), name='room_details'),
    path('room/<room_id>', api_views.RoomView.as_view(), name='room_details'),
]
