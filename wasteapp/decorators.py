from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def producer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        print(request.user.profile)

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.profile.role != "producer":
            messages.error(request, "Only producers allowed!")
            return redirect("consumer_page")

        return view_func(request, *args, **kwargs)

    return wrapper


def consumer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.profile.role != "consumer":
            messages.error(request, "Only consumers allowed!")
            return redirect("producer_page")

        return view_func(request, *args, **kwargs)

    return wrapper