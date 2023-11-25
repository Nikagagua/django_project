from django.forms import ModelForm, forms
from .models import Room, Message, User, Topic
from django.contrib.auth.forms import UserCreationForm


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists')
        return email


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'topic', 'description']


class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ['name']


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'bio']
