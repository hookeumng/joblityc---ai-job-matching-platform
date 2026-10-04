from django.db import models
from django.contrib.auth.models import User


class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    description = models.TextField(blank=True)
    salary_from = models.PositiveIntegerField(null=True, blank=True)
    salary_to = models.PositiveIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    skills = models.TextField(blank=True)
    experience = models.CharField(max_length=100, blank=True)
    employment = models.CharField(max_length=100, blank=True)
    schedule = models.CharField(max_length=100, blank=True)
    work_format = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=255, blank=True)
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    conditions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(
    User,
    on_delete=models.CASCADE,
    related_name="profile",
    null=True,
)

    name = models.CharField(
        max_length=100
    )

    skills = models.TextField(
        help_text="Введите навыки через запятую"
    )

    min_salary = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

class Recommendation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )

    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )

    score = models.PositiveIntegerField(
        default=0
    )

    matched_skills = models.TextField(
        blank=True
    )

    missing_skills = models.TextField(
        blank=True
    )

    reason = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            "user",
            "vacancy",
        )

    def __str__(self):
        return (
            f"{self.user.username} — "
            f"{self.vacancy.title} — "
            f"{self.score}%"
        )