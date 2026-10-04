from django.contrib.auth.models import User

from parsers.sources.hh_search import HHSearchSource
from parsers.sources.hh_page import HHPageSource
from parsers.qwen_parser import QwenParser

from vacancies.services import (
    save_vacancy,
    save_recommendation,
)


def vacancy_matches_query(
    vacancy,
    query: str,
):
    title = vacancy["title"].lower()

    words = [
        word.strip().lower()
        for word in query.split(",")
        if word.strip()
    ]

    if not words:
        return True

    return any(
        word in title
        for word in words
    )


def process_one_vacancy(
    vacancy,
    user_skills,
    min_salary,
    user,
):
    page_source = HHPageSource()
    parser = QwenParser()

    print()
    print(
        f"Обрабатываем: {vacancy['title']}"
    )

    try:
        print("Получаем страницу...")

        text = page_source.get_vacancy_text(
            vacancy["url"]
        )

        print("Страница получена.")
        print("Анализируем вакансию через Qwen...")

        parsed = parser.parse_vacancy(
            text=text,
            url=vacancy["url"],
        )

        print(
            f"✓ Распознано: {parsed.title}"
        )

        print("Оцениваем соответствие профилю...")

        match = parser.match_vacancy(
            vacancy=parsed,
            user_skills=user_skills,
            min_salary=min_salary,
        )

        parsed.match_score = match.get(
            "score",
            0,
        )

        parsed.matched_skills = match.get(
            "matched_skills",
            [],
        )

        parsed.missing_skills = match.get(
            "missing_skills",
            [],
        )

        parsed.match_reason = match.get(
            "reason",
            "",
        )

        print(
            f"✓ Соответствие: "
            f"{parsed.match_score}%"
        )

        print("Сохраняем вакансию...")

        saved_vacancy, created = save_vacancy(
            parsed
        )

        print(
            "Сохраняем рекомендацию "
            "для пользователя..."
        )

        save_recommendation(
            user=user,
            vacancy=saved_vacancy,
            score=parsed.match_score,
            matched_skills=parsed.matched_skills,
            missing_skills=parsed.missing_skills,
            reason=parsed.match_reason,
        )

        print("✓ Рекомендация сохранена.")

        return parsed

    except Exception as error:
        print(
            f"✗ Ошибка при обработке: {error}"
        )

        return None


def find_and_parse_vacancies(
    query: str,
    user_skills: str,
    min_salary: int | None = None,
    limit: int = 20,
    user: User | None = None,
):
    if user is None:
        raise ValueError(
            "Не передан пользователь. "
            "Передай user в find_and_parse_vacancies()."
        )

    search_source = HHSearchSource()

    print("Ищем вакансии на HH.ru...")

    vacancies = search_source.search_vacancies(
        query=query,
        per_page=limit,
    )

    print(
        f"HH.ru нашёл: {len(vacancies)}"
    )

    filtered_vacancies = vacancies

    print(
        "Передаём в AI: "
        f"{len(filtered_vacancies)} вакансий"
    )

    results = []

    for vacancy in filtered_vacancies:
        result = process_one_vacancy(
            vacancy=vacancy,
            user_skills=user_skills,
            min_salary=min_salary,
            user=user,
        )

        if result is not None:
            results.append(result)

    results.sort(
        key=lambda vacancy: vacancy.match_score,
        reverse=True,
    )

    return results