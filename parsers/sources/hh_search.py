import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode


class HHSearchSource:

    def search_vacancies(
        self,
        query: str,
        area: int = 1,
        per_page: int = 20,
    ) -> list[dict]:

        params = {
            "text": query,
            "area": area,
            "page": 0,
            "hhtmFrom": "vacancy_search_list",
        }

        url = (
            "https://hh.ru/search/vacancy?"
            + urlencode(params)
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/154.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        vacancies = []

        links = soup.select(
            'a[data-qa="serp-item__title"]'
        )

        for link in links[:per_page]:

            title = link.get_text(
                " ",
                strip=True,
            )

            vacancy_url = link.get("href")

            if not vacancy_url:
                continue

            vacancies.append(
                {
                    "title": title,
                    "url": vacancy_url,
                }
            )

        return vacancies
