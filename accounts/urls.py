from django.urls import path
from . import views



urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('my-contributions/', views.my_contributions_view, name='my_contributions'),
    path('submit-event/', views.submit_event_view, name='submit_event'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('search/', views.search_events, name='search_events'),
    path('event/<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('category/<str:category>/', views.category_events_view, name='category_events'),
    path('event/<int:event_id>/approve/', views.approve_event, name='approve_event'),
    path('event/<int:event_id>/reject/', views.reject_event, name='reject_event'),
    path('event/<int:event_id>/upvote/', views.toggle_upvote, name='toggle_upvote'),
    path('event/<int:event_id>/vote/<str:vote_type>/', views.vote_event, name='vote_event'),
]