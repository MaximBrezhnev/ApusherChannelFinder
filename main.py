"""Модуль, через который осуществляется запуск сервиса."""

from src.utils import find_accounts


def main() -> None:
    file_with_links: str = input("Введите абсолютный путь к файлу, содержащему ссылки на аккаунты для поиска: ")
    min_number_of_subscribers: int = int(
        input("Введите количество подписчиков, начиная с которого нужно учитывать аккаунты: ")
    )
    number_of_posts: int = int(
        input("Укажите количество последних постов, под которыми необходимо искать аккаунты: ")
    )

    try:
        find_accounts(
            filepath=file_with_links,
            min_number_of_subscribers=min_number_of_subscribers,
            number_of_posts=number_of_posts,
        )
        print("Файл `result.csv` со ссылками на аккаунты успешно сохранен на рабочий стол")
    except Exception as exc:
        print(f"Произошла ошибка в процессе работы сервиса: {exc}")


if __name__ == "__main__":
    main()
