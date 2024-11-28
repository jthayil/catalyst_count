from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from accounts import views

router = DefaultRouter()

"""
path('', views.home, name='home')
path('', Home.as_view(), name='home')
path('blog/', include('blog.urls'))
"""
urlpatterns = [
    path("", views.upload_view, name="home"),
    path("accounts/", include("accounts.urls")),
    path('account/', include('allauth.urls')),
    path("admin/", admin.site.urls),
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
