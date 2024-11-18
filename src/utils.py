"""Модуль, содержащий функционал вызова необходимых парсеров и записи результата в файл."""

import csv
import os
import time

from src.instagram import find_instagram_accounts
from src.telegram import find_telegram_accounts
from src.youtube import find_youtube_accounts


async def find_accounts(
    filepath: str,
    min_number_of_subscribers: int,
    number_of_posts: int,
    number_of_comments: int,
    telegram_session_string: str | None,
    instagram_credentials_file: str | None,
    youtube_developer_key: str | None,
    proxy: str | None,
) -> None:
    """
    Вызывает функции парсинга для всех аккаунтов, переданных в рамках файла,
    после чего вызывает функцию записи результата в файл.
    """

    with open(filepath.strip('"'), "r", encoding="utf-8") as file:
        links: list[str] = [line.strip() for line in file]
    all_received_data: list[tuple[str, int]] = []

    # Вызываем в цикле необходимую функцию парсинга для каждой ссылки из файла
    for link in links:
        console_message = f"Сбор данных для {link}..."

        if "instagram.com" in link:
            if instagram_credentials_file is not None:
                try:
                    print(console_message)
                    received_data: list[tuple[str, int]] = find_instagram_accounts(
                        link=link,
                        min_number_of_subscribers=min_number_of_subscribers,
                        number_of_posts=number_of_posts,
                        instagram_credentials_file=instagram_credentials_file,
                        proxy=proxy
                    )
                    all_received_data.extend(received_data)
                except Exception as exc:
                    print(f"Произошла ошибка при сборе данных для аккаунта {link}: {exc}")
                    continue

        elif "youtube.com" in link or "youtu.be" in link:
            if youtube_developer_key is not None:
                try:
                    print(console_message)
                    received_data: list[tuple[str, int]] = find_youtube_accounts(
                        link=link,
                        min_number_of_subscribers=min_number_of_subscribers,
                        number_of_posts=number_of_posts,
                        youtube_developer_key=youtube_developer_key,
                    )
                    all_received_data.extend(received_data)
                except Exception as exc:
                    print(f"Произошла ошибка при сборе данных для аккаунта {link}: {exc}")
                    continue

        elif "t.me" in link or "telegram.me" in link:
            if telegram_session_string is not None:
                try:
                    print(console_message)
                    received_data: list[tuple[str, int]] = await find_telegram_accounts(
                        link=link,
                        min_number_of_subscribers=min_number_of_subscribers,
                        number_of_comments=number_of_comments,
                        telegram_session_string=telegram_session_string
                    )
                    all_received_data.extend(received_data)
                except Exception as exc:
                    print(f"Произошла ошибка при сборе данных для аккаунта {link}: {exc}")
                    continue

        else:
            print(f"{link}: некорректная ссылка на аккаунт")

        # Таймаут между обработкой аккаунтов для обхода блокировок
        time.sleep(15)

    # Запись результата в файл
    create_final_file(links=all_received_data)


def create_final_file(links: list[str]) -> None:
    """Создает на рабочем столе файл с результатами работы сервиса."""

    home_dir = os.path.expanduser("~")
    desktop_dir = os.path.join(home_dir, "Desktop")
    filepath = os.path.join(desktop_dir, "result.csv")

    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["link", "subscribers"])
        writer.writerows(links)



