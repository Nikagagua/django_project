from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_user, name="logout-user"),
    path("register/", views.register_page, name="register"),
    path("", views.home, name="home"),
    path("room/<int:pk>/", views.room, name="room"),
    path("profile/<int:pk>/", views.user_profile, name="user-profile"),
    path("update-user/", views.update_user, name="update-user"),
    path(
        "reset-password/",
        auth_views.PasswordResetView.as_view(template_name="base/password_reset.html"),
        name="reset_password",
    ),
    path(
        "reset-password-sent/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="base/password_reset_sent.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="base/password_reset_form.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset-password-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="base/password_reset_done.html"
        ),
        name="password_reset_complete",
    ),
    path("create-room/", views.create_room, name="create-room"),
    path("update-room/<int:pk>/", views.update_room, name="update-room"),
    path("delete-room/<int:pk>/", views.delete_room, name="delete-room"),
    path("delete-message/<int:pk>/", views.delete_message, name="delete-message"),
    path("delete-activity/<int:pk>/", views.delete_message, name="delete-activity"),
    path("topics/", views.topics_page, name="topics"),
    path("activity/", views.activity_page, name="activity"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
