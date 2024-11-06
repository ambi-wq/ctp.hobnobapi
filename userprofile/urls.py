from django.urls import path, include
from userprofile import views

app_name = 'userprofile'

urlpatterns = [

    path('user_images', views.UserPofileImg.as_view(), name='UserPofileImg'),
    path('create_profile', views.create_profile, name='create_profile'),
    path('contacts', views.ContactsView.as_view(), name='contacts'),
    path('get_profile', views.get_profile_details, name='get_profile_details'),
    path('delete_profile', views.delete_profile, name='delete profile'),
    path('update_profile', views.update_profile, name='update_profile_details'),
    path('interest_list', views.InterestCollection.as_view(), name='interest_list'),
    path('add_interest', views.add_user_interest, name='add_user_interest'),
    path('create_spotify', views.create_spotify, name='create_spotify'),
    path('images', views.UserProfileImages.as_view(), name='user_profile_img'),
    path('images/<id>', views.UserProfileImages.as_view(), name='user_profile_img'),
    path('display-pic', views.DisplayPictureView.as_view(), name="display_pic"),
    path('preference', views.UserPreferenceView.as_view(), name='user_preference'),
    path('connect-instagram', views.InstagramView.as_view(),
         name='connect-instagram'),
    path('get_other_user_profile/<id>', views.UserProfileView.as_view(),
         name='get_other_profile_details'),
    path('connect-spotify', views.SpotifyView.as_view(), name='connect-spotify'),
    path('get_top_artists', views.get_top_artists, name='get_top_artists'),
    path('check_username/<username>',
         views.ProfileUsername.as_view(), name='checkusername'),
    path('promptqa', views.UserPromptView.as_view(), name='prompt_view'),
    path('promptqa/<id>', views.UserPromptView.as_view(), name='prompt_view'),
    path('promptquestions', views.UserQuestionsListView.as_view(), name="UserQuestionsView"),
    path('replacequestion', views.UserQuestionReplaceView.as_view(), name="UserQuestionReplaceView"),
    path('downtochill', views.DowntoChillList.as_view(), name="DowntoChill"),

    path('delete_user',views.delete_user,name='delete user'),
    path('add_like/<id>',views.UserImageLiked.as_view(),name="userimageliked"),
    path('remove_like/<id>',views.UserImageLiked.as_view(),name="remove user image liked"),
    path('liked_user/<id>',views.GetUserImageLiked.as_view(),name="get liked user list"),

    path('userimage_comments/<id>',views.SingleUserImagesComment.as_view(),name="single userimage comments"),
    path('userimage_comments',views.SingleUserImagesComment.as_view(),name="add userimage comments"),
    path('userimage_commentslist/<image_id>',views.AllUserImageComments.as_view(),name="all userimage comments"),
    path('like_comment/<comment_id>',views.UserImageCommentLiked.as_view(),name="add comment like"),
    path('all_like_comment/<comment_id>',views.AllUserImageCommentLiked.as_view(),name="all user like comments"),
    path('all_image',views.UserProfileImageDetails.as_view(),name="all user image details"),
    path('other_user_images/<id>',views.OtherUserProfileImageDetails.as_view(),name="other user image details"),
]
