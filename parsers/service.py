from parsers.yandex_parser import YandexParser


def process_vacancy(
    text: str,
    url: str,
):
    parser = YandexParser()

    print("Отправляем вакансию в YandexGPT...")

    vacancy = parser.parse_vacancy(
        text=text,
        url=url,
    )

    print("YandexGPT обработал вакансию.")

    return vacancy