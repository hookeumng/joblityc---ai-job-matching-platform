import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")


if not YANDEX_API_KEY:
    raise RuntimeError("YANDEX_API_KEY не найден в .env")

if not YANDEX_FOLDER_ID:
    raise RuntimeError("YANDEX_FOLDER_ID не найден в .env")


client = OpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
)


MODEL = f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-5.1/latest"


def ask_yandex(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content