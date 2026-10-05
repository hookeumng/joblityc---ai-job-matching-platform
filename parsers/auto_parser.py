from django.contrib.auth.models import User

from parsers.sources.hh_search import HHSearchSource
from parsers.sources.hh_page import HHPageSource
from parsers.yandex_parser import YandexParser

from vacancies.services import (
    save_vacancy,
    save_recommendation,
)


def vacancy_matches_profile(
    vacancy,
    desired_position="",
    user_skills="",
):
    title = (vacancy.title or "").lower().strip()

    if desired_position:
        position = desired_position.lower().strip()

        if position == "учитель":
            teaching_words = [
                "учитель",
                "преподаватель",
                "педагог",
                "репетитор",
                "тьютор",
                "эксперт егэ",
            ]

            if not any(
                word in title
                for word in teaching_words
            ):
                return False

    return True

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
    desired_position="",
    city="",
    work_format="any",
    employment="any",
    experience="any",
    wishes="",
):
    page_source = HHPageSource()
    parser = YandexParser()

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
        print("Анализируем вакансию через YandexGPT...")

        parsed = parser.parse_vacancy(
            text=text,
            url=vacancy["url"],
        )

        print(
            f"✓ Распознано: {parsed.title}"
        )
        if not vacancy_matches_profile(
            parsed,
            desired_position=desired_position,
            user_skills=user_skills,
        ):
            print("✗ Вакансия не прошла предварительный фильтр.")
            return

        print("Оцениваем соответствие через YandexGPT...")

        match_result = parser.match_vacancy(
            parsed,
            user_skills=user_skills,
            min_salary=min_salary,
            desired_position=desired_position,
            city=city,
            work_format=work_format,
            employment=employment,
            experience=experience,
            wishes=wishes,
        )

        parsed.match_score = match_result.get(
            "score",
            0,
        )

        parsed.matched_skills = match_result.get(
            "matched_skills",
            [],
        )

        parsed.missing_skills = match_result.get(
            "missing_skills",
            [],
        )

        parsed.match_reason = match_result.get(
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
    query,
    user_skills,
    min_salary=None,
    limit=20,
    user=None,
    desired_position="",
    city="",
    work_format="any",
    employment="any",
    experience="any",
    wishes="",
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
            vacancy,
            user_skills,
            min_salary,
            user,
            desired_position,
            city,
            work_format,
            employment,
            experience,
            wishes,
        )

        if result is not None:
            results.append(result)

    results.sort(
        key=lambda vacancy: vacancy.match_score,
        reverse=True,
    )

    return results