from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
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
]