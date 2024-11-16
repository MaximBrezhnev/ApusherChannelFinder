"""Модуль, через который осуществляется запуск сервиса."""

import asyncio

from src.utils import find_accounts


async def main() -> None:
    file_with_links: str = input("Введите абсолютный путь к файлу, содержащему ссылки на аккаунты для поиска: ")
    min_number_of_subscribers: int = int(
        input("Введите количество подписчиков, начиная с которого нужно учитывать аккаунты: ")
    )
    number_of_posts: int = int(
        input("Укажите количество последних постов, под которыми необходимо искать аккаунты (для ютуба и инстаграма): ")
    )
    number_of_comments: int = int(
        input("Укажите количество комментариев, среди авторов которых надо искать аккаунты (для телеграма): ")
    )

    telegram_credentials = input(
        "Введите через пробел `api_id` и `api_hash` для парсинга данных в Телеграм. "
        "Если парсинг в ТГ не планируется - введите `нет`: "
    )
    if telegram_credentials.lower() == "нет":
        telegram_credentials = None

    instagram_credentials = input(
        "Введите через пробел имя пользователя и пароль от аккаунта в Инстаграм. "
        "Если парсинг в Инстаграме не планируется - введите `нет`:"
    )
    if instagram_credentials.lower() == "нет":
        instagram_credentials_credentials = None



    try:
        await find_accounts(
            filepath=file_with_links,
            min_number_of_subscribers=min_number_of_subscribers,
            number_of_posts=number_of_posts,
            telegram_credentials=telegram_credentials,
            instagram_credentials=instagram_credentials,
            number_of_comments=number_of_comments
        )
        print("Файл `result.csv` со ссылками на аккаунты успешно сохранен на рабочий стол")
    except Exception as exc:
        print(f"Произошла ошибка в процессе работы сервиса: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
