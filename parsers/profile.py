import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()

from django.contrib.auth.models import User
from vacancies.models import UserProfile


def get_user_profile(user: User):
    profile = UserProfile.objects.filter(
        user=user
    ).first()

    if profile is None:
        raise ValueError(
            "Профиль пользователя не найден. "
            "Сначала заполни профиль."
        )

    return profile