import json

from parsers.ai.yandex import ask_yandex
from parsers.vacancy import VacancyData


def parse_json_response(result: str) -> dict:
    result = result.strip()

    if result.startswith("```"):
        result = result.replace("```json", "", 1)
        result = result.replace("```", "", 1)
        result = result.strip()

    start = result.find("{")

    if start == -1:
        raise ValueError(
            "YandexGPT не вернул JSON-объект"
        )

    decoder = json.JSONDecoder()

    data, _ = decoder.raw_decode(
        result[start:]
    )

    return data


class YandexParser:
    def parse_vacancy(
        self,
        text: str,
        url: str,
    ) -> VacancyData:

        text = text[:12000]

        prompt = f"""
Ты — AI-модель для анализа вакансий с HH.ru.

Твоя задача — извлечь из текста вакансии структурированную информацию.

Верни ТОЛЬКО корректный JSON.
Не используй Markdown.
Не добавляй пояснения до или после JSON.

Используй строго такую структуру:

{{
    "title": "",
    "company": "",
    "salary_from": null,
    "salary_to": null,
    "currency": "",
    "skills": [],
    "experience": "",
    "employment": "",
    "schedule": "",
    "work_format": "",
    "city": "",
    "responsibilities": "",
    "requirements": "",
    "conditions": ""
}}

Правила:

- salary_from и salary_to должны быть числами или null.
- currency используй как RUR, USD, EUR и т.п.
- skills должен содержать только конкретные технологии,
  языки программирования, фреймворки, базы данных,
  инструменты и профессиональные навыки.
- Не помещай длинные предложения в skills.
- Не придумывай информацию.
- Если информации нет, используй null или пустую строку.
- city — основной город вакансии, а не адрес работодателя.
- responsibilities — основные обязанности.
- requirements — основные требования.
- conditions — основные условия работы.

Текст вакансии:

{text}
"""

        result = ask_yandex(prompt)
        data = parse_json_response(result)

        return VacancyData(
            title=data.get("title", ""),
            company=data.get("company", ""),
            url=url,
            description=data.get("requirements", ""),

            salary_from=data.get("salary_from"),
            salary_to=data.get("salary_to"),
            currency=data.get("currency", ""),

            skills=data.get("skills") or [],
            experience=data.get("experience", ""),
            employment=data.get("employment", ""),
            schedule=data.get("schedule", ""),
            work_format=data.get("work_format", ""),
            city=data.get("city", ""),

            responsibilities=data.get(
                "responsibilities",
                "",
            ),
            requirements=data.get(
                "requirements",
                "",
            ),
            conditions=data.get(
                "conditions",
                "",
            ),
        )

    def match_vacancy(
    self,
    vacancy: VacancyData,
    user_skills: str,
    min_salary: int | None = None,
    desired_position: str = "",
    city: str = "",
    work_format: str = "any",
    employment: str = "any",
    experience: str = "any",
    wishes: str = "",
) -> dict:

        prompt = f"""
Ты — AI-система профессионального подбора вакансий.

Твоя задача — объективно оценить,
насколько вакансия подходит конкретному пользователю.

========================
ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
========================

Желаемая должность:
{desired_position}

Навыки:
{user_skills}

Минимальная желаемая зарплата:
{min_salary}

Город:
{city}

Формат работы:
{work_format}

Тип занятости:
{employment}

Опыт:
{experience}

Дополнительные пожелания:
{wishes}

========================
ВАКАНСИЯ
========================

Название:
{vacancy.title}

Компания:
{vacancy.company}

Зарплата:
от {vacancy.salary_from}
до {vacancy.salary_to}
{vacancy.currency}

Город:
{vacancy.city}

Опыт:
{vacancy.experience}

Формат работы:
{vacancy.work_format}

Занятость:
{vacancy.employment}

График:
{vacancy.schedule}

Навыки:
{", ".join(vacancy.skills or [])}

Требования:
{vacancy.requirements}

Обязанности:
{vacancy.responsibilities}

Условия:
{vacancy.conditions}

========================
ПРАВИЛА ОЦЕНКИ
========================

Оцени вакансию по шкале от 0 до 100.

Учитывай следующие факторы:

1. Совпадение навыков — 35%.

2. Соответствие желаемой должности — 20%.

3. Соответствие опыта — 15%.

4. Соответствие зарплаты — 10%.

5. Соответствие города — 5%.

6. Соответствие формата работы — 10%.

7. Соответствие типа занятости — 5%.

Дополнительные пожелания пользователя используй
как дополнительный фактор при принятии решения.

ВАЖНО:

- Основные навыки пользователя имеют больший вес,
  чем второстепенные навыки вакансии.

- Если совпадают Python, Django, PostgreSQL и Docker,
  это является сильным совпадением.

- Не снижай оценку слишком сильно только из-за
  отсутствия второстепенных инструментов.

- Если вакансия требует множество технологий,
  которых нет у пользователя, оценку необходимо снизить.

- Если вакансия относится к сильно более сложной
  специализации, чем профиль пользователя,
  оценку необходимо снизить.

- Если зарплата пользователя не указана,
  не учитывай зарплату при оценке.

- Если зарплата вакансии не указана,
  не делай предположений о её размере.

- Если формат работы пользователя неизвестен,
  не снижать оценку за формат работы.

- Не придумывай навыки, опыт или требования.

- Оценка должна быть реалистичной.
  Не ставь 80–100 только потому,
  что совпали 2–3 навыка.

========================
ФОРМАТ ОТВЕТА
========================

Верни ТОЛЬКО JSON:

{{
    "score": 0,
    "matched_skills": [],
    "missing_skills": [],
    "reason": ""
}}

Правила JSON:

- score — целое число от 0 до 100.
- matched_skills — навыки пользователя,
  которые действительно нужны вакансии.
- missing_skills — важные навыки вакансии,
  которых нет у пользователя.
- reason — короткое объяснение оценки на русском языке.

ВАЖНЫЕ ПРАВИЛА ПО ПРОФИЛЮ:

- Если желаемая должность сильно отличается
  от названия вакансии и её содержания,
  значительно снижай оценку.

- Если город пользователя указан и вакансия
  находится в другом городе, учитывай это.

- Если пользователь выбрал удалённую работу,
  удалённые вакансии являются предпочтительными.

- Если пользователь указал конкретный формат работы,
  несовпадение формата должно снижать оценку.

- Если пользователь указал конкретный тип занятости,
  учитывай его при оценке.

- Если опыт пользователя отличается от требуемого опыта,
  учитывай это.

- Дополнительные пожелания пользователя могут
  повышать или снижать итоговую оценку.

- Не придумывай данные, которых нет в вакансии
  или профиле.
  
"""

        result = ask_yandex(prompt)

        return parse_json_response(result)