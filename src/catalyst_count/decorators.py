from django.shortcuts import redirect


def go_home(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:home")
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.profile.role in allowed_roles or request.user.is_staff or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            return redirect("accounts:home")

        return wrapper_func

    return decorator
