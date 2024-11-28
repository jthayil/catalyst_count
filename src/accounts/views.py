import os
import asyncio
import threading

from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, response
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, login, logout, decorators
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from asgiref.sync import sync_to_async, async_to_sync
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from accounts.forms import EmployeeForm, LoginForm, SignupForm, UserModelForm
from accounts.models import Company
from accounts.serializers import (
    YearSerializer,
    CitySerializer,
    CompanySerializer,
    CountrySerializer,
    IndustrySerializer,
    StateSerializer,
    UserSerializer,
)
from accounts.view_utils import process_csv_file, process_csv_files
from accounts.models import Company

from catalyst_count.decorators import go_home
from catalyst_count.support import itsEmailID


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                userName = form.cleaned_data["email"].split("@")[0]
                user.username = userName
                user.save()
            except Exception as err:
                print(err)
            return redirect("accounts:home")
        else:
            for x in form.errors:
                print(form.errors[x])
    return redirect("accounts:login")


@go_home
def login_view(request):
    if request.method == "POST":
        # Post Form Data Object
        form = LoginForm(request.POST)
        if form.is_valid():
            identityKey = form.cleaned_data["username"]
            authenticationKey = form.cleaned_data["password"]

            # Getting User
            try:
                that = (
                    User.objects.get(email=identityKey)
                    if itsEmailID(identityKey)
                    else User.objects.get(username=identityKey)
                )
            except ObjectDoesNotExist:
                messages.warning(request, "User not registered")
                return response.HttpResponseRedirect(reverse("accounts:login"))

            # Login User
            if that is not None:
                this_user = authenticate(
                    username=that.username, password=authenticationKey
                )
                if this_user is not None:
                    login(request, this_user)
                    if that.first_name and that.last_name:
                        messages.success(request, "Welcome " + that.get_full_name())
                    try:
                        if request.GET.get("next"):
                            return redirect(request.GET.get("next"))
                    except:
                        pass
                    return response.HttpResponseRedirect(reverse("accounts:home"))
            return response.HttpResponseRedirect(reverse("accounts:login"))
        else:
            for x in form.errors:
                messages.warning(request, str(form.errors[x]))

    return render(request, "accounts/login.html", context={})


@decorators.login_required
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@decorators.login_required
def profile_view(request):
    return redirect("accounts:home")


@decorators.login_required
def upload_view(request):
    if request.method == "POST":
        uploaded_file = request.FILES["file"]
        if not uploaded_file:
            return JsonResponse({"error": "No file provided"}, status=400)

        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        fs = FileSystemStorage(location=upload_dir)
        filename = fs.save(uploaded_file.name, uploaded_file)
        fp = os.path.join(upload_dir, filename)
        # asyncio.run(process_csv_files(fp))
        t = threading.Thread(
            target=asyncio.run, args=[process_csv_files(fp)], daemon=True
        )
        t.start()

        return JsonResponse({"status": True})

    return render(request, "accounts/dashboard.html", {"active_upload_data": "active"})


@decorators.login_required
def query_builder_view(request):
    context = {"active_query_builder": "active"}
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            keyword = form.cleaned_data["keyword"]
            industry = form.cleaned_data["industry"]
            year_founded = form.cleaned_data["year_founded"]
            city = form.cleaned_data["city"]
            state = form.cleaned_data["state"]
            country = form.cleaned_data["country"]
            from_year = form.cleaned_data["from_year"]
            to_year = form.cleaned_data["to_year"]

            query = Q()
            if keyword:
                query |= Q(name__icontains=keyword) | Q(domain__icontains=keyword) | Q(linkedin_url__icontains=keyword)
            if industry:
                query |= Q(industry__icontains=industry)
            if year_founded:
                query |= Q(year_founded=year_founded)
            if city:
                query |= Q(city__icontains=city)
            if state:
                query |= Q(state__icontains=state)
            if country:
                query |= Q(country__icontains=country)
            if from_year:
                query |= Q(year_founded__gte=from_year)
            if to_year:
                query |= Q(year_founded__lte=to_year)

            results = Company.objects.filter(query)
            print(results)
            context = {"active_query_builder": "active", "results": results}
    return render(request, "accounts/query_builder.html", context)


@decorators.login_required
def master_user_view(request, pk):
    if request.method == "POST":
        if pk == 0:
            request.POST = request.POST.copy()
            request.POST["password1"] = request.POST["password"]
            request.POST["password2"] = request.POST["password"]
            form = SignupForm(request.POST)
            if form.is_valid():
                form.save()
                status = True
                msg = "Saved Successful"
                return JsonResponse({"status": status, "msg": msg})
            else:
                for x in form.errors:
                    print(x)
        else:
            o_user = User.objects.get(id=pk)
            form = UserModelForm(request.POST, instance=o_user)
            if form.is_valid():
                form.save()
                status = True
                msg = "Saved Successful"
                return JsonResponse({"status": status, "msg": msg})
            else:
                for x in form.errors:
                    print(x)
    return render(request, "accounts/users.html", {"active_users": "active"})


class masters_getusers(generics.ListAPIView):
    api_view = ["GET"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]

    search_fields = "__all__"
    ordering_fields = "__all__"


class accounts_company(generics.ListAPIView):
    api_view = ["GET"]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]

    search_fields = "__all__"
    ordering_fields = "__all__"


@cache_page(60 * 5)
def industry_datalist(request):
    term = request.GET.get("term")
    page = request.GET.get("page", 1)
    low = (int(page) - 1) * 10
    up = int(page) * 10

    dat = cache.get(f"industry_datalist_{page}{term}")
    if dat is None:
        if term:
            dat = (
                Company.objects.filter(industry__icontains=term)
                .distinct("industry")
                .order_by("industry")[low:up]
            )
        else:
            dat = Company.objects.distinct("industry").order_by("industry")[low:up]
        cache.set(f"industry_datalist_{page}{term}", dat, timeout=(60 * 30))
    serializer = IndustrySerializer(dat, many=True)

    data = {
        "results": serializer.data,
        "pagination": {"more": True},
    }
    return JsonResponse(data, safe=False)


@cache_page(60 * 5)
def city_datalist(request):
    term = request.GET.get("term")
    page = request.GET.get("page", 1)
    low = (int(page) - 1) * 10
    up = int(page) * 10

    dat = cache.get(f"city_datalist_{page}{term}")
    if dat is None:
        if term:
            dat = (
                Company.objects.filter(city__icontains=term)
                .distinct("city")
                .order_by("city")[low:up]
            )
        else:
            dat = Company.objects.distinct("city").order_by("city")[low:up]
        cache.set(f"city_datalist_{page}{term}", dat, timeout=(60 * 30))
    serializer = CitySerializer(dat, many=True)

    data = {
        "results": serializer.data,
        "pagination": {"more": True},
    }
    return JsonResponse(data, safe=False)


@cache_page(60 * 5)
def state_datalist(request):
    term = request.GET.get("term")
    page = request.GET.get("page", 1)
    low = (int(page) - 1) * 10
    up = int(page) * 10

    dat = cache.get(f"state_datalist_{page}{term}")
    if dat is None:
        if term:
            dat = (
                Company.objects.filter(state__icontains=term)
                .distinct("state")
                .order_by("state")[low:up]
            )
        else:
            dat = Company.objects.distinct("state").order_by("state")[low:up]
        cache.set(f"state_datalist_{page}{term}", dat, timeout=(60 * 30))
    serializer = StateSerializer(dat, many=True)

    data = {
        "results": serializer.data,
        "pagination": {"more": True},
    }
    return JsonResponse(data, safe=False)


@cache_page(60 * 5)
def country_datalist(request):
    term = request.GET.get("term")
    page = request.GET.get("page", 1)
    low = (int(page) - 1) * 10
    up = int(page) * 10

    dat = cache.get(f"country_datalist_{page}{term}")
    if dat is None:
        if term:
            dat = (
                Company.objects.filter(country__icontains=term)
                .distinct("country")
                .order_by("country")[low:up]
            )
        else:
            dat = Company.objects.distinct("country").order_by("country")[low:up]
        cache.set(f"country_datalist_{page}{term}", dat, timeout=(60 * 30))
    serializer = CountrySerializer(dat, many=True)

    data = {
        "results": serializer.data,
        "pagination": {"more": True},
    }
    return JsonResponse(data, safe=False)


@cache_page(60 * 5)
def year_datalist(request):
    term = request.GET.get("term")
    page = request.GET.get("page", 1)
    low = (int(page) - 1) * 10
    up = int(page) * 10

    dat = cache.get(f"year_founded_datalist_{page}{term}")
    if dat is None:
        if term:
            dat = (
                Company.objects.filter(year_founded__icontains=term)
                .distinct("year_founded")
                .order_by("year_founded")[low:up]
            )
        else:
            dat = Company.objects.distinct("year_founded").order_by("year_founded")[
                low:up
            ]
        cache.set(f"year_founded_datalist_{page}{term}", dat, timeout=(60 * 30))
    serializer = YearSerializer(dat, many=True)

    data = {
        "results": serializer.data,
        "pagination": {"more": True},
    }
    return JsonResponse(data, safe=False)


def test(request):
    data = {
        "results": [{"id": 1, "text": "Option 1"}, {"id": 2, "text": "Option 2"}],
        "pagination": {"more": True},
    }
    return JsonResponse(data, safe=False)


# eof
