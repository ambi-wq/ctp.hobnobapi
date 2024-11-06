from django.urls import path, include
from events import views

app_name = 'events'

urlpatterns = [
    path('user-event-search', views.UserEventSearchView.as_view(), name="user-event-search_view"),
    path('event-search', views.EventSearchView.as_view(), name="eventsearch_view"),
    path('report_events', views.report_events, name="report_events"),
    path('event', views.EventView.as_view(), name="event"),
    path('event/<id>', views.EventView.as_view(), name="event_details"),
    path('all_events', views.AllPublicEventsView.as_view(),
         name="all_public_events"),
    path('private-events', views.PrivateEventsView.as_view(), name="private_events"),
    path('public-events', views.PublicEventsView.as_view(), name='public_events'),
    path('hosted-events', views.HostedEventsView.as_view(), name='hosted_events'),
    path('interested-events', views.InterestedEventsView.as_view(),
         name='interested_events'),
    path('interested-events-2/<id>', views.EventInterestedUsersView.as_view(),
         name='interested_events_users'), 
    path('user_events_list', views.UserEventsListView.as_view(),
         name="user_events_list"),
    path('event_img', views.EventImageView.as_view(), name="post_event_img"),
    path('event_img/<id>', views.EventImageView.as_view(), name="get_event_img"),
    path('event_image', views.ImageUploadView.as_view(), name="event_img_upload"),
    # path('event_image_list', views.BulkEventImage.as_view(), name="event_img_url_list"),
    path('add_interest/<event_id>',
         views.AddEventUserInterested.as_view(), name="add_interest"),
    path('upcoming_events', views.UpcomingEventsListView.as_view(),
         name="upcoming_events"),
    path('past_events', views.PastEventsListView.as_view(), name="past_events"),
    path('interested_user/<id>', views.GetInterestedUserList.as_view(),
         name="interested_user"),
    path('currated_events', views.CuratedEventsListView.as_view(),
         name="currated_events"),
    path('currated_events/<pk>', views.CuratedEventsView.as_view(),
         name="currated_events_details"),
    path('comments', views.SingleCommentView.as_view(), name="create_comment"),
    path('comments/<id>', views.SingleCommentView.as_view(), name="comments"),
    path('all_comments/<id>', views.CommentsList.as_view(), name="comments_list"),
    path('reply_comments/<id>', views.CommentReplyList.as_view(),
         name="reply_comments_list"),
    path('event_invitation/<id>',
         views.EventInvitationView.as_view(), name="comments_list"),
    path('others-hosted-events/<id>', views.OthersHostedEventsView.as_view(), name='hosted_events'),

    path('add_going/<event_id>',views.AddEventUserGoing.as_view(),name="add_going"),
    path('add_yet_to_decide/<event_id>',views.AddEventUserYetToDecide.as_view(),name="add_yet_to_decide"),
    path('going-events',views.GoingEventsView.as_view(),name="going_events"),
    path('yet-to-decide-events',views.YetToDecideEventsView.as_view(),name="yet_to_decide_events"),

    path('going_user/<id>',views.GetGoingUserList.as_view(),name="going user list"),
    path('yet_to_decide_user/<id>',views.GetYetToDecideUserList.as_view(),name="going user list"),
]


# OthersHostedEventsView
