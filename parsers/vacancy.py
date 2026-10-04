from dataclasses import dataclass


@dataclass
class VacancyData:
    title: str
    company: str
    url: str
    description: str

    salary_from: int | None = None
    salary_to: int | None = None
    currency: str = ""

    skills: list[str] | None = None
    experience: str = ""
    employment: str = ""
    schedule: str = ""
    work_format: str = ""
    city: str = ""

    responsibilities: str = ""
    requirements: str = ""
    conditions: str = ""