from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, MessageForm, MyUserCreationForm, UserForm, TopicForm

HOME_PAGE = 'home'
LOGIN_PAGE = 'login'


def login_page(request):
    page = LOGIN_PAGE
    form = MyUserCreationForm()
    if request.user.is_authenticated:
        return redirect(HOME_PAGE)

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        user_exists = None
        try:
            user_exists = User.objects.get(email=email)
        except User.DoesNotExist as e:
            messages.error(request, f'User {user_exists} does not exist', e)
            return redirect(LOGIN_PAGE)

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect(HOME_PAGE)
        else:
            messages.error(request, 'Incorrect username or password. Please try again.')

    context = {
        'form': form,
        'page': page
    }
    return render(request, 'base/login.html', context)


def logout_page(request):
    logout(request)
    return redirect(HOME_PAGE)


def register_page(request):
    form = MyUserCreationForm()
    context = {'form': form}

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect(HOME_PAGE)
        else:
            print(form.errors)
            messages.error(request, 'An error occurred during registration. Please check the form data.')

    return render(request, 'base/signup.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    rooms_count = rooms.count()
    messages_info = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:3]

    context = {
        'rooms': rooms,
        'topics': topics,
        'rooms_count': rooms_count,
        'message_info': messages_info,
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room_info = get_object_or_404(Room, id=pk)
    message_info = room_info.message_set.all()
    participants = room_info.participants.all()

    if request.method == 'POST':
        if request.user.is_authenticated:
            message_info = Message.objects.create(
                user=request.user,
                room=room_info,
                body=request.POST.get('body')
            )

            room_info.participants.add(request.user)
            return redirect('room', pk=room_info.id)
        else:
            return redirect(LOGIN_PAGE)

    context = {
        'room': room_info,
        'message_info': message_info,
        'participants': participants,
    }
    return render(request, 'base/room.html', context)


@login_required(login_url=LOGIN_PAGE)
def user_profile(request, pk):
    form = UserForm(request.GET, request.FILES, instance=request.user)
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    message_info = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'form': form,
        'user': user,
        'rooms': rooms,
        'message_info': message_info,
        'topics': topics
    }
    return render(request, 'base/profile.html', context)


@login_required(login_url=LOGIN_PAGE)
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )

        return redirect(HOME_PAGE)
    context = {
        'form': form,
        'topics': topics
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url=LOGIN_PAGE)
def handle_room(request, pk, action):
    room_obj = get_object_or_404(Room, id=pk)

    if request.user != room_obj.host:
        return HttpResponse('You have no permissions to modify this room!', status=403)

    if action == 'update':
        form = RoomForm(request.POST or None, instance=room_obj)
        if request.method == 'POST' and form.is_valid():
            form.save()
            return redirect(HOME_PAGE)
        context = {'form': form, 'room': room_obj}
        return render(request, 'base/edit-room.html', context)

    elif action == 'delete':
        if request.method == 'GET':
            context = {'room_obj': room_obj}
            return render(request, 'base/delete.html', context)
        if request.method == 'POST':
            room_obj.delete()
            return redirect(HOME_PAGE)

    return HttpResponse('Invalid action', status=400)


@login_required(login_url=LOGIN_PAGE)
def update_message(request, pk):
    message_obj = Message.objects.get(id=pk)
    form = MessageForm(instance=message_obj)

    if request.user != message_obj.user:
        return HttpResponse('You have no permissions!')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message_obj)
        if form.is_valid():
            form.save()
            return redirect('room', pk=message_obj.room_id)

    context = {'form': form}
    return render(request, 'base/edit-room.html', context)


@login_required(login_url=LOGIN_PAGE)
def delete_message(request, pk):
    message_obj = Message.objects.get(id=pk)

    if request.user != message_obj.user:
        return HttpResponse('You have no permissions!')

    if request.method == 'POST':
        message_obj.delete()
        return redirect('room', pk=message_obj.room_id)

    return render(request, 'base/delete.html', {'message_obj': message_obj})


@login_required(login_url=LOGIN_PAGE)
def delete_activity(request, pk):
    activity_obj = Message.objects.get(id=pk)

    if request.user != activity_obj.user:
        return HttpResponse('You have no permissions!')

    if request.method == 'POST':
        activity_obj.delete()
        return redirect(HOME_PAGE)

    return render(request, 'base/delete.html', {'obj': activity_obj})


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {
        'user': user,
        'form': form
    }
    print(form.errors)

    return render(request, 'base/update_user.html', context)


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    topics = Topic.objects.filter(name__icontains=q)

    topic_counts = {topics: topic.rooms.count() for topic in topics}
    context = {
        'topics': topics,
        'topic_counts': topic_counts
    }
    return render(request, 'base/topic_component.html', context)


def activity_page(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity_component.html', context)
