from django.urls import path
from accounts import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.upload_view, name="home"),
    path("profile/", views.profile_view, name="profile"),
    path("query_builder/", views.query_builder_view, name="query_builder"),
    path("master/user/<int:pk>/", views.master_user_view, name="master_user"),
    
    # API
    path("users/list/", views.masters_getusers.as_view(), name="masters_getusers"),
    path("company/", views.accounts_company.as_view(), name="accounts_company"),
    path("industry/", views.industry_datalist, name="industry_datalist"),
    path("city/", views.city_datalist, name="city_datalist"),
    path("state/", views.state_datalist, name="state_datalist"),
    path("country/", views.country_datalist, name="country_datalist"),
    path("year/", views.year_datalist, name="year_datalist"),
    path("test/", views.test, name="test"),
]
