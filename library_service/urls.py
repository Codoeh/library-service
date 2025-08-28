"""
URL configuration for library_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path(
        "api/v1/admin/",
        admin.site.urls
    ),
    path(
        "api/v1/user/",
        include("user.urls", "user"),
        name="user"
    ),
    path(
        "api/v1/books/",
        include("books.urls", "books"),
        name="books"
    ),
    path(
        "api/v1/borrowings/",
        include("borrowings.urls", "borrowings"),
        name="borrowings"
    ),
    path(
        "api/v1/payments/",
        include("payments.urls", "payments"),
        name="payments"
    ),
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
]
