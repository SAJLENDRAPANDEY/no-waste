from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from users.models import User

from django.conf import settings
# -------- SIGNUP --------

def signup(request):

    if request.method == "POST":

        username         = request.POST.get("username")
        email            = request.POST.get("email")
        password         = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        role             = request.POST.get("role")

        # ✅ saari fields filled hain?
        if not all([username, email, password, confirm_password, role]):
            return render(request, "signup.html", {"error": "Please fill in all fields"})

        # ✅ password match check
        if password != confirm_password:
            return render(request, "signup.html", {"error": "Passwords do not match"})

        # ✅ username already exists check  <-- yahi IntegrityError fix hai
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already taken. Please choose another."})

        # ✅ email already exists check
        if User.objects.filter(email=email).exists():
            return render(request, "signup.html", {"error": "Email already registered. Please login."})

        # ✅ user banao
        user = User.objects.create_user(
            username = username,
            email    = email,
            password = password,
        )
        user.role = role
        user.save()

        return redirect("login")

    return render(request, "signup.html")


# -------- LOGIN --------

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        # ✅ empty fields check
        if not username or not password:
            return render(request, "login.html", {"error": "Please enter username and password"})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # ✅ role ke hisaab se redirect
            if user.role == "producer":
                return redirect("producer_page")
            else:
                return redirect("consumer_page")

        # ✅ wrong credentials error
        return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")