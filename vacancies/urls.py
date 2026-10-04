from django.urls import path

from .views import (
    about_view,
    logout_view,
    profile_view,
    register_view,
    update_vacancies,
    vacancy_detail,
    vacancy_list,
)


urlpatterns = [
    path("", vacancy_list, name="vacancy_list"),
    path("profile/", profile_view, name="profile"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("update/", update_vacancies, name="update_vacancies"),
    path("about/", about_view, name="about"),
    path("<int:vacancy_id>/", vacancy_detail, name="vacancy_detail"),
]