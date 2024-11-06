from django.urls import path, include
from matching import views

app_name = 'matching'

urlpatterns = [
    path('add_follower', views.AddFollowerView.as_view(), name="add_follower"),
    path('remove_follower/<id>', views.AddFollowerView.as_view(), name="remove_follower"),
    path('followers', views.FollowerList.as_view(), name="followers_list"),
    path('following', views.FollowingList.as_view(), name="following_list"),
    path('other-following/<id>', views.OtherFollowingList.as_view(), name="other_following_list"),
    path('other-followers/<id>', views.OtherFollowerList.as_view(), name="other_following_list"),
    path('explore', views.UserExploreView.as_view(), name="explore_view"),
    path('user-search', views.UserSearchView.as_view(), name="search_view"),
    path('close-friend-search', views.CloseFriendSearchView.as_view(), name="closefriend_search_view"),
    path('location', views.UserLocationView.as_view(), name="user_location"),
    path('return_follower', views.ReturnFollower.as_view(), name="return_follower"),
    path('close_friends', views.CloseFriendsListView.as_view(), name="close_friends"),
    path('close_friends/<id>', views.CloseFriendsListView.as_view(), name="close_friends"),
    path('get_user_contacts_list', views.GetUserContactsList.as_view(), name="get_user_contacts_list"),
    path('get_appusers_pnLst', views.get_appusers_pnLst, name="get_appusers_phonenumbers"),

    path('delete-suggessted-user/<id>',views.delete_suggessted_user,name="delete_suggessted_user"),
    path('delete_follower/<id>',views.DeleteFollower.as_view(),name='delete_follower'),

    path('multiple_close-friend-search', views.MultipleCloseFriendSearchView.as_view(), name="closefriend_search_view"),
    path('multiple_close_friends', views.MultipleCloseFriendsListView.as_view(), name="close_friends"),
    path('multiple_close_friends/<id>', views.MultipleCloseFriendsListView.as_view(), name="close_friends"),

]