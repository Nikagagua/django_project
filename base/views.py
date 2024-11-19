from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm, MessageForm, LoginForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

HOME_PAGE = "home"
LOGIN_PAGE = "login"


def login_page(request):
    page = HOME_PAGE

    if request.user.is_authenticated:
        return redirect(HOME_PAGE)

    login_form = LoginForm()

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        user_email = None
        try:
            user_email = User.objects.get(email=email)
        except ObjectDoesNotExist:
            messages.error(request, f"{user_email} does not exist")
            return exit(1)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect(HOME_PAGE)
        else:
            messages.error(request, "Email or Password does not exit")

    context = {"page": page, "form": login_form}
    return render(request, "base/login.html", context)


def logout_user(request):
    logout(request)
    return redirect(HOME_PAGE)


def register_page(request):
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            messages.success(
                request,
                "Welcome, {}! You have successfully registered and logged in.".format(
                    user.username
                ),
            )
            return redirect("home")
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    if field == "email" and "unique" in error.lower():
                        error_messages.append("Email already exists.")
                    elif field == "username" and "unique" in error.lower():
                        error_messages.append("Username already exists.")
                    elif field == "password1" and "password" in error.lower():
                        error_messages.append(
                            "The password you entered does not meet the requirements. "
                            "Make sure it is at least 8 characters long and contains both letters and numbers."
                        )
                    elif field == "password2" and "match" in error.lower():
                        error_messages.append(
                            "The passwords you entered do not match. Please try again."
                        )
                    else:
                        error_messages.append(error)
            messages.error(request, "\n".join(error_messages))
            context = {"form": form}
            return render(request, "base/signup.html", context)
    else:
        form = MyUserCreationForm()
        context = {"form": form}
        return render(request, "base/signup.html", context)


def home(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""

    topics = Topic.objects.annotate(room_count=Count("room")).order_by("-room_count")

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )[:3]
    show_all_room = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )[3:]

    top_topics = topics[0:5]
    other_topics = topics[5:]
    room_by_topic = {
        topic.id: Room.objects.filter(topic=topic)[0:3] for topic in top_topics
    }
    all_room_by_topic = {
        topic.id: Room.objects.filter(topic=topic)[3:0] for topic in top_topics
    }
    all_room_count = Room.objects.all().count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))[0:3]

    user = request.user if request.user.is_authenticated else None

    context = {
        "user": user,
        "rooms": rooms,
        "topics": top_topics,
        "room_messages": room_messages,
        "other_topics": other_topics,
        "all_room_count": all_room_count,
        "room_by_topic": room_by_topic,
        "show_all_room": show_all_room,
        "all_room_by_topic": all_room_by_topic,
        "q": q,
    }
    return render(request, "base/home.html", context)


@login_required(login_url="login")
def room(request, pk):
    form = MessageForm()
    room_info = Room.objects.get(id=pk)
    room_host = room_info.host.id if room_info.host else None
    room_messages = room_info.message_set.all()
    participants = room_info.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room_info, body=request.POST.get("body")
        )
        room_info.participants.add(request.user)
        return redirect("room", pk=room_info.id)

    context = {
        "room_info": room_info,
        "room_messages": room_messages,
        "participants": participants,
        "room_host": room_host,
        "form": form,
    }
    return render(request, "base/room.html", context)


@login_required(login_url="login")
def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = Room.objects.filter()[0:2]
    show_all_room = Room.objects.filter()[3:]
    room_messages = Message.objects.filter()[0:4]
    topics = Topic.objects.annotate(room_count=Count("room")).order_by("-room_count")
    top_topics = topics[0:5]
    other_topics = topics[5:]
    all_room_count = Room.objects.all().count()
    context = {
        "user": user,
        "rooms": rooms,
        "show_all_room": show_all_room,
        "room_messages": room_messages,
        "topics": top_topics,
        "other_topics": other_topics,
        "all_room_count": all_room_count,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            topic = form.cleaned_data["topic"]
            Room.objects.create(
                host=request.user,
                topic=topic,
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
            )
            return redirect("home")

    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def update_room(request, pk):
    room_info = Room.objects.get(id=pk)
    form = RoomForm(instance=room_info)
    topics = Topic.objects.all()

    if request.user != room_info.host:
        return HttpResponse("You are not allowed here!!")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room_info)
        if form.is_valid():
            topic = form.cleaned_data["topic"]
            room_info.name = form.cleaned_data["name"]
            room_info.topic = topic
            room_info.description = form.cleaned_data["description"]
            room_info.save()
            return redirect("home")

    context = {"form": form, "topics": topics, "room_info": room_info}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def delete_room(request, pk):
    room_info = Room.objects.get(id=pk)

    if request.user != room_info.host:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        room_info.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room_info})


@login_required(login_url="login")
def delete_message(request, pk):
    message_info = Message.objects.get(id=pk)

    if request.user != message_info.user:
        return HttpResponse("Your are not allowed here!!")

    if request.method == "POST":
        message_info.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message_info})


@login_required(login_url="login")
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

    context = {"form": form}
    return render(request, "base/update_user.html", context)


def topics_page(request):
    q = request.GET.get("q") if request.GET.get("q") is not None else ""
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, "base/topic_component.html", {"topics": topics})


def activity_page(request):
    room_messages = Message.objects.all()
    return render(
        request, "base/activity_component.html", {"room_messages": room_messages}
    )
