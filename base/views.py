from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm, MessageForm

HOME_PAGE = 'home'
LOGIN_PAGE = 'login'


def login_page(request):
    form = MyUserCreationForm()
    page = HOME_PAGE

    if request.user.is_authenticated:
        return redirect(HOME_PAGE)

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password1')

        user_exists = None
        try:
            user_exists = User.objects.get(email=email)
        except User.DoesNotExist as e:
            messages.error(request, f'User {user_exists} does not exist: {e}')
            return redirect(LOGIN_PAGE)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    context = {
        'form': form,
        'page': page
    }
    return render(request, 'base/login.html', context)


def logout_user(request):
    logout(request)
    return redirect(HOME_PAGE)


def register_page(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

            context = {'form': form}
            return render(request, 'base/signup.html', context)
    else:
        form = MyUserCreationForm()
        context = {'form': form}
        return render(request, 'base/signup.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )[:3]
    show_all_room = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )[3:]

    topics = Topic.objects.all()[0:5]
    topics_show_all = Topic.objects.all()[5:]
    all_room_count = Room.objects.all().count()
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:4]

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
        'topics_show_all': topics_show_all,
        'show_all_room': show_all_room,
        'all_room_count': all_room_count
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    form = MessageForm()
    room_info = Room.objects.get(id=pk)
    room_host = room_info.host.id if room_info.host else None
    room_messages = room_info.message_set.all()
    participants = room_info.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room_info,
            body=request.POST.get('body')
        )
        room_info.participants.add(request.user)
        return redirect('room', pk=room_info.id)

    context = {
        'room_info': room_info,
        'room_messages': room_messages,
        'participants': participants,
        'room_host': room_host,
        'form': form
    }
    return render(request, 'base/room.html', context)


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics
    }
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data['topic']
            Room.objects.create(
                host=request.user,
                topic=topic,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
            )
            return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    room_info = Room.objects.get(id=pk)
    form = RoomForm(instance=room_info)
    topics = Topic.objects.all()

    if request.user != room_info.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room_info)
        if form.is_valid():
            topic = form.cleaned_data['topic']
            room_info.name = form.cleaned_data['name']
            room_info.topic = topic
            room_info.description = form.cleaned_data['description']
            room_info.save()
            return redirect('home')

    context = {'form': form, 'topics': topics, 'room_info': room_info}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    room_info = Room.objects.get(id=pk)

    if request.user != room_info.host:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        room_info.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room_info})


@login_required(login_url='login')
def delete_message(request, pk):
    message_info = Message.objects.get(id=pk)

    if request.user != message_info.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message_info.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message_info})


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update_user.html', context)


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topic_component.html', {'topics': topics})


def activity_page(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity_component.html', {'room_messages': room_messages})
