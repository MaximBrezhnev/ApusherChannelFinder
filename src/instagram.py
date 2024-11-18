import os
import time
import random
import logging

import instagrapi

logging.basicConfig(level=logging.CRITICAL)


def find_instagram_accounts(
    link: str,
    min_number_of_subscribers: int,
    number_of_posts: int,
    username: str,
    password: str,
) -> list[tuple[str, int]]:
    while True:
        try:
            received_data: set[tuple[str, str]] = set()
            checked_users: set[str] = set()

            client: instagrapi.Client = _get_client(username=username, password=password)
            account = client.user_info_by_username(username=_extract_username_from_link(link=link))

            posts, _ = client.user_medias_paginated(
                user_id=account.pk,
                amount=number_of_posts
            )
            for post in posts:
                try:
                    time.sleep(random.uniform(0.5, 0.7))
                    comments = client.media_comments(media_id=post.pk, amount=post.comment_count)
                    for comment in comments:
                        try:
                            if (received_username := comment.user.username) not in checked_users:
                                checked_users.add(received_username)
                                received_account_link = f"https://www.instagram.com/{received_username}/"

                                time.sleep(random.uniform(0.5, 0.7))
                                received_account_followers_count = (
                                    client.user_info_by_username(username=received_username).follower_count
                                )

                                if received_account_followers_count >= min_number_of_subscribers:
                                    print(received_account_link, received_account_followers_count)

                                    received_data.add(
                                        (received_account_link, received_account_followers_count)
                                    )
                        except:
                            print("Comment exception")  # временный код
                            continue
                except:
                    print("Post exception")  # временный код
                    continue
        except instagrapi.exceptions.LoginRequired:
            print("login required")  # временный код
            pass  # тут будут происходить действия при `login required`
        else:
            break

    return list(received_data)


def _get_client(username: str, password: str) -> instagrapi.Client:
    client = instagrapi.Client()
    client.set_proxy("http://bxUkguVJ:CbV6b2uF@45.137.53.163:63676")

    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    session_file_path = os.path.join(current_dir_path, "instagrapi_session.json")

    if os.path.exists(session_file_path):
        client.load_settings(session_file_path)
    else:
        client.login(username, password)
        client.dump_settings(session_file_path)

    return client


def _extract_username_from_link(link: str) -> str:
    return link.rstrip("/").split("/")[-1]
