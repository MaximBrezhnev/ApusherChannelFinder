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
    telegram_credentials: str | None
) -> None:
    with open(filepath, "r") as file:
        links: list[str] = [line.strip() for line in file]

    all_received_data: list[tuple[str, int]] = []
    for link in links:
        console_message = f"Сбор данных для {link}..."

        if "instagram.com" in link:
            print(console_message)
            received_data: list[tuple[str, int]] = find_instagram_accounts(
                link=link,
                min_number_of_subscribers=min_number_of_subscribers,
                number_of_posts=number_of_posts,
            )
            all_received_data.extend(received_data)
        elif "youtube.com" in link or "youtu.be" in link:
            print(console_message)
            received_data: list[tuple[str, int]] = find_youtube_accounts(
                link=link,
                min_number_of_subscribers=min_number_of_subscribers,
                number_of_posts=number_of_posts,
            )
            all_received_data.extend(received_data)
        elif "t.me" in link or "telegram.me" in link:
            try:
                api_id, api_hash = telegram_credentials.split()
            except:
                print("Введены некорректные данные для парсинга в Телеграм. Парсинг не может быть произведен")
                continue

            print(console_message)

            try:
                received_data: list[tuple[str, int]] = await find_telegram_accounts(
                    link=link,
                    min_number_of_subscribers=min_number_of_subscribers,
                    number_of_posts=number_of_posts,
                    api_id=api_id,
                    api_hash=api_hash,
                )
                all_received_data.extend(received_data)
            except Exception as exc:
                raise exc
                print(f"Произошла ошибка при сборе данных для аккаунта {link}: {exc}")
                continue
        else:
            print(f"{link}: некорректная ссылка на аккаунт")
        time.sleep(30)

    create_final_file(links=all_received_data)


def create_final_file(links: list[str]) -> None:
    home_dir = os.path.expanduser("~")
    desktop_dir = os.path.join(home_dir, "Desktop")
    filepath = os.path.join(desktop_dir, "result.csv")

    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["link", "subscribers"])
        writer.writerows(links)



