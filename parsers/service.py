from parsers.qwen_parser import QwenParser
from parsers.sources.hh_page import HHPageSource
from vacancies.services import save_vacancy


def process_vacancy(url: str) -> None:
    source = HHPageSource()
    parser = QwenParser()

    print("Получаем страницу HH.ru...")

    text = source.get_vacancy_text(url)

    print("Страница получена.")
    print("Отправляем вакансию в Qwen...")

    vacancy_data = parser.parse_vacancy(
        text=text,
        url=url,
    )

    print("Qwen обработал вакансию.")

    vacancy, created = save_vacancy(
        vacancy_data
    )

    if created:
        print(f"Создана вакансия: {vacancy}")
    else:
        print(f"Обновлена вакансия: {vacancy}")