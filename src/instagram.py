import os
import time

import instagrapi


def find_instagram_accounts(
    link: str,
    min_number_of_subscribers: int,
    number_of_posts: int,
    username: str,
    password: str,
) -> list[tuple[str, int]]:

    received_data: set[tuple[str, str]] = set()
    client: instagrapi.Client = _get_client(username=username, password=password)
    account = client.user_info_by_username(username=_extract_username_from_link(link=link))

    posts, _ = client.user_medias_paginated(
        user_id=account.pk,
        amount=number_of_posts
    )
    for post in posts:
        time.sleep(3)
        comments = client.media_comments(media_id=post.pk, amount=post.comment_count)
        for comment in comments:
            received_account_link = f"https://www.instagram.com/{comment.user.username}/"
            time.sleep(2)
            received_account_followers_count = (
                client.user_info_by_username(username=comment.user.username).follower_count
            )

            if received_account_followers_count >= min_number_of_subscribers:
                received_data.add(
                    (received_account_link, received_account_followers_count)
                )

    return list(received_data)


def _get_client(username: str, password: str) -> instagrapi.Client:
    client = instagrapi.Client()

    current_dir_path = os.path.dirname(os.path.abspath(__file__))
    session_file_path = os.path.join(current_dir_path, "instagrapi.session.json")

    if os.path.exists(session_file_path):
        client.load_settings(session_file_path)
    else:
        client.login(username, password)
        client.dump_settings(session_file_path)

    return client


def _extract_username_from_link(link: str) -> str:
    return link.rstrip("/").split("/")[-1]
