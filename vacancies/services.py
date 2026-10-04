from django.contrib.auth.models import User

from .models import Recommendation, Vacancy
from parsers.vacancy import VacancyData


def save_vacancy(data: VacancyData) -> tuple[Vacancy, bool]:
    vacancy, created = Vacancy.objects.update_or_create(
        url=data.url,
        defaults={
            "title": data.title,
            "company": data.company,
            "description": data.description,

            "salary_from": data.salary_from,
            "salary_to": data.salary_to,
            "currency": data.currency,

            "skills": ", ".join(data.skills or []),
            "experience": data.experience,
            "employment": data.employment,
            "schedule": data.schedule,
            "work_format": data.work_format,
            "city": data.city,

            "responsibilities": data.responsibilities,
            "requirements": data.requirements,
            "conditions": data.conditions,
        },
    )

    return vacancy, created


def save_recommendation(
    user: User,
    vacancy: Vacancy,
    score: int,
    matched_skills: list[str],
    missing_skills: list[str],
    reason: str,
) -> Recommendation:
    recommendation, created = (
        Recommendation.objects.update_or_create(
            user=user,
            vacancy=vacancy,
            defaults={
                "score": score,
                "matched_skills": ", ".join(
                    matched_skills
                ),
                "missing_skills": ", ".join(
                    missing_skills
                ),
                "reason": reason,
            },
        )
    )

    return recommendation