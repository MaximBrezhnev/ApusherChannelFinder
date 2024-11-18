"""Модуль для сбора ссылок на профили из комментариев в ТГ."""

import re
import time

import pyrogram
from pyrogram import raw
from pyrogram.enums import ChatType
from pyrogram.raw import functions, types
from pyrogram.types import User


async def find_telegram_accounts(
    link: str,
    min_number_of_subscribers: int,
    number_of_comments: int,
    telegram_session_string: str
) -> list[tuple[str, int]]:
    """Основная функция для поиска ТГ-каналов в комментариях."""

    received_data: set[tuple[str, str]] = set()
    checked_user_ids = set()

    async with (pyrogram.Client(
        "channel_finder_tg_client",
        session_string=telegram_session_string
    ) as client):
        # Получаем `id` канала из ссылки на него
        channel_id = await get_channel_id_from_link(
            client=client, channel_link=link
        )

        # Получаем `id` связанного чата для обсуждения
        chat = await client.get_chat(channel_id)
        if chat.linked_chat:
            discussion_chat_id =  chat.linked_chat.id
        else:
            discussion_chat_id = None

        # Заменяем метод `_parse() на дополненную версию`
        User._parse = custom_parse

        # Обрабатываем все сообщения из дискуссии для обсуждения (т.е. все комментарии ко всем постам) в количестве,
        # переданном при запуске сервиса
        async for message in client.get_chat_history(
            chat_id=discussion_chat_id, limit=number_of_comments
        ):
            # Проверяем, что сообщение является комментарием
            if message.reply_to_message_id:
                try:
                    user = message.from_user

                    # Рассматриваем вариант, когда комментарий оставлен от лица пользователя
                    if user:
                        # Проверяем, что данный пользователь еще не был рассмотрен
                        if user[0].id not in checked_user_ids:
                            time.sleep(0.7)

                            # Получаем раздел `о себе` данного пользователя
                            full_user_object = await client.invoke(
                                functions.users.GetFullUser(
                                    id=types.InputUser(
                                        user_id=user[0].id,
                                        access_hash=user[1]
                                    )
                                )
                            )
                            checked_user_ids.add(user[0].id)
                            user_bio = full_user_object.full_user.about

                            # Проверяем, что раздел `о себе` присутствует
                            if user_bio:
                                # Ищем ссылку на ТГ-канал в данном разделе
                                retrieved_channel_info = await get_channel_link_from_bio(bio=user_bio)

                                if retrieved_channel_info:
                                    # Получаем данные канала из полученной ссылки
                                    retrieved_channel_id = await get_channel_id_from_link(
                                        client=client, channel_link=retrieved_channel_info
                                    )
                                    retrieved_channel = await client.get_chat(chat_id=retrieved_channel_id)

                                    # Проверяем, что полученный канал действительно является каналом, а не ботом /
                                    # супергруппой и т.д.
                                    if retrieved_channel.type == ChatType.CHANNEL:
                                        # Проверяем, что комментарий не принадлежит автору текущего канала
                                        if retrieved_channel.id != channel_id:
                                            subscribers = retrieved_channel.members_count
                                            retrieved_channel_link = f"https://t.me/{retrieved_channel.username}"

                                            # Если количество подписчиков удовлетворяет условию, сохраняем данные канала
                                            if subscribers >= min_number_of_subscribers:
                                                print(retrieved_channel_link, subscribers)
                                                received_data.add(
                                                    (retrieved_channel_link, subscribers)
                                                )
                        # Рассматриваем вариант, когда комментарий оставлен не от лица пользователя
                        elif chat := message.sender_chat:
                            # Проверяем, что комментарий не оставлен самим проверяемым каналом
                            if chat.id != channel_id:
                                # Проверяем, что комментарий оставлен каналом, а не группой, ботом и т.д.
                                if chat.type == ChatType.CHANNEL:
                                    retrieved_channel = await client.get_chat(chat_id=chat.id)
                                    subscribers = retrieved_channel.members_count

                                    # Если число подписчиков удовлетворяет условию, сохраняем данные канала
                                    if subscribers >= min_number_of_subscribers:
                                        received_data.add(
                                            (f"https://t.me/{retrieved_channel.username}", subscribers)
                                        )
                # В случае временной блокировки из-за числа запросов, делаем паузу
                except pyrogram.errors.exceptions.flood_420.FloodWait:
                    print("Таймаут 60 секунд для обхода блокировки...")
                    time.sleep(60)
                    continue
                # В случае ошибки при обработке отдельно взятого комментария, просто пропускаем его
                except:
                    continue

    return list(received_data)


async def get_channel_id_from_link(client: pyrogram.Client, channel_link: str) -> int:
    """Извлекает `id` канала из ссылки на него."""

    parts = channel_link.rstrip("/").split("/")

    if parts[-1].isdigit():
        channel_identifier = parts[-2]
    else:
        channel_identifier = parts[-1]

    if channel_identifier.isdigit():
        try:
            chat = await client.get_chat(int(channel_identifier))
        except Exception:
            chat = await client.get_chat("-100" + str(channel_identifier))
    else:
        chat = await client.get_chat(channel_identifier)

    return chat.id


async def get_channel_link_from_bio(bio: str) -> str | None:
    """Ищет ссылку на ТГ-канал в разделе `о себе`"""

    channel_url_pattern = re.compile(r"t\.me/([A-Za-z0-9_]+)")
    match = channel_url_pattern.search(bio)
    return match.group(0) if match else None


def custom_parse(client, user):
    """
    Дополненный метод `User._parse()` из библиотеки `pyrogram`.
    Помимо сформированного объекта класса `User` возвращает `access_hash`,
    необходимый для того, чтобы была возможность получить bio пользователей,
    у которых отсутствует username и скрыт номер телефона.
    """

    if user is None or isinstance(user, raw.types.UserEmpty):
        return None

    return User(
        id=user.id,
        is_self=user.is_self,
        is_contact=user.contact,
        is_mutual_contact=user.mutual_contact,
        is_deleted=user.deleted,
        is_bot=user.bot,
        is_verified=user.verified,
        is_restricted=user.restricted,
        is_scam=user.scam,
        is_fake=user.fake,
        is_support=user.support,
        is_premium=user.premium,
        first_name=user.first_name,
        last_name=user.last_name,
        **User._parse_status(user.status, user.bot),
        username=user.username,
        language_code=user.lang_code,
        dc_id=getattr(user.photo, "dc_id", None),
        phone_number=user.phone,
        client=client
    ), user.access_hash