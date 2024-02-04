
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),
    # path('news/', include('NewsPortal.urls')),
    # path('articles/', include('NewsPortal.urls')),
    path('newsportal/', include('NewsPortal.urls')),
    path('accounts/', include('allauth.urls')),
]
