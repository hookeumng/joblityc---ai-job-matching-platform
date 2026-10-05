from django.shortcuts import get_object_or_404, redirect, render
from parsers.auto_parser import find_and_parse_vacancies

from .models import (
    Recommendation,
    Vacancy,
    UserProfile,
)

from parsers.service import process_vacancy
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth import login, logout
from .forms import RegistrationForm

@login_required
def vacancy_list(request):
    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    if profile is None:
        return redirect(
            "/vacancies/profile/"
        )

    recommendations = (
    Recommendation.objects
        .filter(
            user=request.user,
            score__gte=60,
        )
        .select_related("vacancy")
        .order_by("-score", "-created_at")
    )
    min_salary = request.GET.get(
        "min_salary"
    )

    skill = request.GET.get(
        "skill"
    )

    if not min_salary:
        min_salary = profile.min_salary

    vacancies = []

    for recommendation in recommendations:
        vacancy = recommendation.vacancy

        if (
            min_salary
            and vacancy.salary_from
            and vacancy.salary_from < int(min_salary)
        ):
            continue

        vacancy.match_score = (
            recommendation.score
        )

        vacancy.matched_skills = (
            recommendation.matched_skills
        )

        vacancy.missing_skills = (
            recommendation.missing_skills
        )

        vacancy.match_reason = (
            recommendation.reason
        )

        if vacancy.salary_from:
            vacancy.salary_from_display = (
                f"{vacancy.salary_from:,}"
                .replace(",", " ")
            )

        if vacancy.salary_to:
            vacancy.salary_to_display = (
                f"{vacancy.salary_to:,}"
                .replace(",", " ")
            )

        vacancy.skills_list = [
            item.strip()
            for item in vacancy.skills.split(",")
            if item.strip()
        ]

        vacancies.append(
            vacancy
        )

    if skill:
        skill_words = [
            item.strip().lower()
            for item in skill.split(",")
            if item.strip()
        ]

        if skill_words:
            vacancies = [
                vacancy
                for vacancy in vacancies
                if any(
                    word in vacancy.description.lower()
                    for word in skill_words
                )
            ]

    return render(
        request,
        "vacancies/vacancy_list.html",
        {
            "vacancies": vacancies,
            "min_salary": min_salary or "",
            "skill": skill or "",
            "profile": profile,
            "updated": request.GET.get(
                "updated"
            ),
        },
    )


def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    if vacancy.salary_from:
        vacancy.salary_from_display = (
            f"{vacancy.salary_from:,}".replace(",", " ")
        )

    if vacancy.salary_to:
        vacancy.salary_to_display = (
            f"{vacancy.salary_to:,}".replace(",", " ")
        )

    return render(
        request,
        "vacancies/vacancy_detail.html",
        {"vacancy": vacancy},
    )


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "name": request.user.username,
            "skills": "",
        },
    )

    if request.method == "POST":
        profile.name = request.POST.get("name", "").strip()
        profile.desired_position = request.POST.get(
            "desired_position",
            "",
        ).strip()
        profile.skills = request.POST.get(
            "skills",
            "",
        ).strip()
        profile.city = request.POST.get(
            "city",
            "",
        ).strip()
        profile.work_format = request.POST.get(
            "work_format",
            "any",
        )
        profile.employment = request.POST.get(
            "employment",
            "any",
        )
        profile.experience = request.POST.get(
            "experience",
            "any",
        )
        profile.wishes = request.POST.get(
            "wishes",
            "",
        ).strip()

        min_salary = request.POST.get("min_salary", "").strip()

        profile.min_salary = (
            int(min_salary)
            if min_salary.isdigit()
            else None
        )

        profile.save()

        return redirect("/vacancies/profile/")

    return render(
        request,
        "vacancies/profile.html",
        {
            "profile": profile,
        },
    )

@login_required
def update_vacancies(request):
    profile = UserProfile.objects.filter(
        user=request.user
    ).first()

    if profile is None:
        return redirect("/vacancies/profile/")
    Recommendation.objects.filter(
        user=request.user
    ).delete()

    search_parts = []

    if profile.desired_position:
        search_parts.append(profile.desired_position)

    if profile.skills:
        search_parts.append(profile.skills)

    if profile.city:
        search_parts.append(profile.city)

    search_query = " ".join(search_parts)

    find_and_parse_vacancies(
        query=search_query,
        user_skills=profile.skills,
        min_salary=profile.min_salary,
        limit=20,
        user=request.user,
        desired_position=profile.desired_position,
        city=profile.city,
        work_format=profile.work_format,
        employment=profile.employment,
        experience=profile.experience,
        wishes=profile.wishes,
    )

    return redirect("/vacancies/?updated=1")


def about_view(request):
    return render(
        request,
        "vacancies/about.html",
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect("/vacancies/")

    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
            )

            return redirect("/vacancies/profile/")
    else:
        form = RegistrationForm()

    return render(
        request,
        "vacancies/register.html",
        {
            "form": form,
        },
    )


def logout_view(request):
    logout(request)

    return redirect("/vacancies/")