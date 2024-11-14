"""Модуль, через который осуществляется запуск сервиса."""

import asyncio

from src.utils import find_accounts


async def main() -> None:
    file_with_links: str = input("Введите абсолютный путь к файлу, содержащему ссылки на аккаунты для поиска: ")
    min_number_of_subscribers: int = int(
        input("Введите количество подписчиков, начиная с которого нужно учитывать аккаунты: ")
    )
    number_of_posts: int = int(
        input("Укажите количество последних постов, под которыми необходимо искать аккаунты: ")
    )

    telegram_credentials = input(
        "Введите через пробел `api_id` и `api_hash` для парсинга данных в Телеграм. "
        "Если парсинг в ТГ не планируется - введите `нет`: "
    )
    if telegram_credentials.lower() == "нет":
        telegram_credentials = None

    try:
        await find_accounts(
            filepath=file_with_links,
            min_number_of_subscribers=min_number_of_subscribers,
            number_of_posts=number_of_posts,
            telegram_credentials=telegram_credentials,
        )
        print("Файл `result.csv` со ссылками на аккаунты успешно сохранен на рабочий стол")
    except Exception as exc:
        raise exc
        print(f"Произошла ошибка в процессе работы сервиса: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
