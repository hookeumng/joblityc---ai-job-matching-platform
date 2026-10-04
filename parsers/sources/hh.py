from parsers.vacancy import VacancyData


class HHParser:
    def parse_vacancy(self, data: dict) -> VacancyData:
        salary = data.get("salary") or {}

        return VacancyData(
            title=data.get("name", ""),
            company=data.get("employer", {}).get("name", ""),
            url=data.get("alternate_url", ""),
            description=data.get("snippet", {}).get("requirement", ""),
            salary_from=salary.get("from"),
            salary_to=salary.get("to"),
            currency=salary.get("currency", ""),
        )

    def parse_vacancies(self, data_list: list[dict]) -> list[VacancyData]:
        return [
            self.parse_vacancy(data)
            for data in data_list
        ]