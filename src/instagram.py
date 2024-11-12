import os

import instaloader


def find_instagram_accounts(
    link: str,
    min_number_of_subscribers: int,
    number_of_posts: int,
) -> list[tuple[str, str]]:

    received_data: set[tuple[str, str]] = set()
    client: instaloader.Instaloader = _get_client()
    account = instaloader.Profile.from_username(
        client.context, username=_extract_username_from_link(link=link)
    )
    count = 0

    print("Получение постов аккаунта...")
    for post in account.get_posts():
        count += 1
        if count > number_of_posts:
            break

        for comment in post.get_comments():
            received_account_link = f"https://www.instagram.com/{comment.owner.username}/"
            number_of_subscribers: int = _get_followers_count(
                link=received_account_link, client=client
            )
            if number_of_subscribers >= min_number_of_subscribers:
                received_data.add(
                    (received_account_link, number_of_subscribers)
                )

    return list(received_data)


def _get_client() -> instaloader.Instaloader:
    client = instaloader.Instaloader()
    client.login(user="buugol", passwd="KZCKmj8vXpMHFnmQ")

    # proxy_url = "http://bxUkguVJ:CbV6b2uF@45.137.53.163:63676"
    # os.environ["https_proxy"] = proxy_url

    return client


def _extract_username_from_link(link: str) -> str:
    return link.rstrip("/").split("/")[-1]


def _get_followers_count(link: str, client: instaloader.Instaloader) -> int:
    account = instaloader.Profile.from_username(
        client.context, username=_extract_username_from_link(link=link)
    )
    return account.followers