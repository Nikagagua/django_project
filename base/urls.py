from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register_page, name='register'),

    path('', views.home, name='home'),
    path('room/<int:pk>/', views.room, name='room'),
    path('profile/<int:pk>/', views.user_profile, name='user-profile'),
    path('update-user/', views.update_user, name='update-user'),

    path('create-room/', views.create_room, name='create-room'),
    path('update-room/<int:pk>/<str:action>', views.handle_room, name='update-room'),
    path('delete-room/<int:pk>/<str:action>', views.handle_room, name='delete-room'),
    path('update-message/<int:pk>/', views.update_message, name='update-message'),
    path('delete-message/<int:pk>/', views.delete_message, name='delete-message'),
    path('delete-activity/<int:pk>/', views.delete_activity, name='delete-activity'),

    path('topics/', views.topics_page, name='topics'),
    path('activity/', views.activity_page, name='activity'),
]
