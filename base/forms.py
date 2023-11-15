from django.forms import ModelForm
from .models import Room, Message, User
from django.contrib.auth.forms import UserCreationForm


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'topic', 'description']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'bio']
