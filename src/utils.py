import csv
import os

from src.instagram import find_instagram_accounts
from src.telegram import find_telegram_accounts
from src.youtube import find_youtube_accounts


def find_accounts(
    filepath: str,
    min_number_of_subscribers: int,
    number_of_posts: int
) -> None:
    with open(filepath, "r") as file:
        links: list[str] = [line.strip() for line in file]

    all_received_data: list[tuple[str, str]] = []
    for link in links:
        console_message = f"Сбор данных для {link}..."

        if "instagram.com" in link:
            print(console_message)
            received_data: list[tuple[str, str]] = find_instagram_accounts(
                link=link,
                min_number_of_subscribers=min_number_of_subscribers,
                number_of_posts=number_of_posts,
            )
            all_received_data.extend(received_data)
        elif "youtube.com" or "youtu.be" in link:
            print(console_message)
            received_data: list[tuple[str, str]] = find_youtube_accounts(
                link=link,
                min_number_of_subscribers=min_number_of_subscribers,
                number_of_posts=number_of_posts,
            )
            all_received_data.extend(received_data)
        elif "t.me" in link or "telegram.me" in link:
            print(console_message)
            received_data: list[tuple[str, str]] = find_telegram_accounts(
                link=link,
                min_number_of_subscribers=min_number_of_subscribers,
                number_of_posts=number_of_posts,
            )
            all_received_data.extend(received_data)
        else:
            print(f"{link}: некорректная ссылка на аккаунт")

    create_final_file(links=all_received_data)


def create_final_file(links: list[str]) -> None:
    home_dir = os.path.expanduser("~")
    desktop_dir = os.path.join(home_dir, "Desktop")
    filepath = os.path.join(desktop_dir, "result.csv")

    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["link", "subscribers"])
        writer.writerows(links)



