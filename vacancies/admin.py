from django.contrib import admin

from .models import UserProfile, Vacancy


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'salary_from',
        'salary_to',
        'currency',
        'created_at',
    )
    search_fields = ('title', 'company')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "skills",
        "min_salary",
    )