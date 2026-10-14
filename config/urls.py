from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("", lambda request: redirect("/vacancies/"), name="home"),
    path("admin/", admin.site.urls),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="vacancies/login.html",
        ),
        name="login",
    ),

    path(
        "vacancies/",
        include("vacancies.urls"),
    ),
    path("accounts/login/", lambda request: redirect("/vacancies/")),
]