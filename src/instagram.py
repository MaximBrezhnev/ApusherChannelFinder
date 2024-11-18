"""Модуль для сбора ссылок на профили из комментариев к постам в Инстаграме."""

import os
import time
import random
import requests

import instagrapi


def find_instagram_accounts(
    link: str,
    min_number_of_subscribers: int,
    number_of_posts: int,
    instagram_credentials_file: str,
    proxy: str | None
) -> list[tuple[str, int]]:
    """Основная функция для поиска профилей в комментариях в Инстаграме."""

    # Загрузка учетных данных для парсинга
    with open(instagram_credentials_file.strip('"'), 'r') as file:
        credentials = [line.strip().split(":") for line in file.readlines()]

    # Инициализация переменных для смены аккаунтов
    blocked_index = -1
    current_index = 0
    checked_users = set()
    received_data = set()

    while True:
        username, password = credentials[current_index]
        try:
            # Создаем клиента для текущего аккаунта
            client: instagrapi.Client = _get_client(username=username, password=password, proxy=proxy)
            account = client.user_info_by_username(username=_extract_username_from_link(link=link))

            posts, _ = client.user_medias_paginated(
                user_id=account.pk,
                amount=number_of_posts
            )
            # Для каждого полученного поста пользователя ищем комментарии
            for post in posts:
                try:
                    time.sleep(random.uniform(0.3, 0.7))
                    comments = client.media_comments(media_id=post.pk, amount=post.comment_count)

                    # Для каждого комментария производим поиск профилей
                    for comment in comments:
                        try:
                            # Проверяем, что пользователь еще не был рассмотрен
                            if (received_username := comment.user.username) not in checked_users:
                                # Проверяем, что автором комментария не является автор поста
                                if received_username != account.username:
                                    checked_users.add(received_username)
                                    received_account_link = f"https://www.instagram.com/{received_username}/"

                                    time.sleep(random.uniform(0.3, 0.7))
                                    received_account_followers_count = (
                                        client.user_info_by_username(username=received_username).follower_count
                                    )
                                    # Если количество подписчиков профиля удовлетворяет условию, сохраняем результат
                                    if received_account_followers_count >= min_number_of_subscribers:
                                        print(received_account_link, received_account_followers_count)

                                        received_data.add(
                                            (received_account_link, received_account_followers_count)
                                        )

                        # Если при обработке отдельного комментария возникает ошибка связанная с блокировкой,
                        # не пропускаем ее для смены аккаунта
                        except (
                            instagrapi.exceptions.LoginRequired,
                            requests.exceptions.ConnectionError,
                            requests.exceptions.RetryError,
                            instagrapi.exceptions.UnknownError,
                            instagrapi.exceptions.ChallengeError,
                        ) as exc:
                            raise exc
                        # Если при обработке отдельного комментария возникает иная ошибка, просто пропускаем его
                        except:
                            continue

                # Если при обработке отдельного поста возникает ошибка связанная с блокировкой,
                # не пропускаем ее для смены аккаунта
                except (
                    instagrapi.exceptions.LoginRequired,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.RetryError,
                    instagrapi.exceptions.UnknownError,
                    instagrapi.exceptions.ChallengeError
                ) as exc:
                    raise exc
                # Если при обработке отдельного поста возникает ошибка, просто пропускаем его
                except:
                    continue

        # Если возникает проблема, связанная с временной блокировкой аккаунта, производим его замену
        except (
            instagrapi.exceptions.LoginRequired,
            requests.exceptions.ConnectionError,
            requests.exceptions.RetryError,
            instagrapi.exceptions.UnknownError,
            instagrapi.exceptions.ChallengeError,
        ):
            print(f"Ошибка 'Login required' для аккаунта {username}. Смена аккаунта...")

            _delete_session_file()
            if blocked_index == -1:
                blocked_index = current_index
            current_index = (current_index + 1) % len(credentials)

            # В случае, если были опробованы уже все аккаунты, прекращаем попытки парсинга
            if current_index == blocked_index:
                print("Аккаунты для парсинга в инстаграм кончились")
                break
        else:
            break

    return list(received_data)


def _get_client(username: str, password: str, proxy: str | None) -> instagrapi.Client:
    """Возвращает клиента для работы с Инстаграмом."""

    client = instagrapi.Client()

    # Устанавливаем прокси, если они были переданы
    if proxy is not None:
        client.set_proxy(proxy)

    session_file_path = os.path.join(os.getenv('TEMP'), f"instagrapi_session.json")

    # Если файл сессии существует, то создаем клиента с его помощью
    if os.path.exists(session_file_path):
        print(f"Вход в аккаунт {username} с помощью файла сессии...")
        client.load_settings(session_file_path)
    # Иначе производим вход в аккаунт и сохраняем файл сессии
    else:
        print(f"Вход в аккаунт {username} с помощью логина и пароля...")
        client.login(username, password)
        client.dump_settings(session_file_path)

    return client


def _extract_username_from_link(link: str) -> str:
    """Извлекаем имя пользователя из ссылки на его аккаунт."""

    return link.rstrip("/").split("/")[-1]


def _delete_session_file():
    """Удаляет файл сессии текущего пользователя."""

    session_file_path = os.path.join(os.getenv('TEMP'), f"instagrapi_session.json")

    if os.path.exists(session_file_path):
        os.remove(session_file_path)
