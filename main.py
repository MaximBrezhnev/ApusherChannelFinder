"""Модуль, через который осуществляется запуск сервиса."""

import asyncio

from src.utils import find_accounts


async def main() -> None:
    file_with_links: str = input("Введите абсолютный путь к файлу, содержащему ссылки на аккаунты для поиска: ")
    min_number_of_subscribers: int = int(
        input("Введите количество подписчиков, начиная с которого нужно учитывать аккаунты: ")
    )

    number_of_posts: int = int(
        input("Укажите количество последних постов, под которыми необходимо искать аккаунты (для ютуба и инстаграма). "
              "Если их парсинг не планируется, введите 0: ")
    )
    number_of_comments: int = int(
        input("Укажите количество комментариев, среди авторов которых надо искать аккаунты (для телеграма). "
              "Если его парсинг не планируется, введите 0: ")
    )

    telegram_session_string = input(
        "Введите строку, содержащую данные сессии (см. инструкцию), для парсинга данных в Телеграм. "
        "Если парсинг в ТГ не планируется, введите `нет`: "
    )
    if telegram_session_string.lower() == "нет":
        telegram_session_string = None

    instagram_credentials = input(
        "Введите через пробел имя пользователя и пароль от аккаунта в Инстаграм. "
        "Если парсинг в Инстаграме не планируется, введите `нет`: "
    )
    if instagram_credentials.lower() == "нет":
        instagram_credentials = None

    youtube_developer_key = input(
        "Введите ключ (см. инструкцию) для парсинга данных в Ютубе. "
        "Если парсинг в Ютубе не планируется, введите `нет`: "
    )
    if youtube_developer_key.lower() == "нет":
        youtube_developer_key = None

    try:
        await find_accounts(
            filepath=file_with_links,
            min_number_of_subscribers=min_number_of_subscribers,
            number_of_posts=number_of_posts,
            telegram_session_string=telegram_session_string,
            instagram_credentials=instagram_credentials,
            youtube_developer_key=youtube_developer_key,
            number_of_comments=number_of_comments
        )
        print("Файл `result.csv` со ссылками на аккаунты успешно сохранен на рабочий стол")
    except Exception as exc:
        print(f"Произошла ошибка в процессе работы сервиса: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
