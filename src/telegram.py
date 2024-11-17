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
    received_data: set[tuple[str, str]] = set()
    checked_user_ids = set()

    async with (pyrogram.Client(
        "channel_finder_tg_client",
        session_string=telegram_session_string
    ) as client):
        channel_id = await get_channel_id_from_link(
            client=client, channel_link=link
        )

        chat = await client.get_chat(channel_id)
        if chat.linked_chat:
            discussion_chat_id =  chat.linked_chat.id
        else:
            discussion_chat_id = None

        User._parse = custom_parse

        async for message in client.get_chat_history(
            chat_id=discussion_chat_id, limit=number_of_comments
        ):
            if message.reply_to_message_id:
                try:
                    user = message.from_user

                    if user:
                        if user[0].id not in checked_user_ids:
                            time.sleep(0.7)
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

                            if user_bio:
                                retrieved_channel_info = await get_channel_link_from_bio(bio=user_bio)

                                if retrieved_channel_info:
                                    retrieved_channel_id = await get_channel_id_from_link(
                                        client=client, channel_link=retrieved_channel_info
                                    )
                                    retrieved_channel = await client.get_chat(chat_id=retrieved_channel_id)

                                    if retrieved_channel.type == ChatType.CHANNEL:
                                        if retrieved_channel.id != channel_id:
                                            subscribers = retrieved_channel.members_count
                                            retrieved_channel_link = f"https://t.me/{retrieved_channel.username}"

                                            if subscribers >= min_number_of_subscribers:
                                                print(retrieved_channel_link, subscribers)
                                                received_data.add(
                                                    (retrieved_channel_link, subscribers)
                                                )
                        elif chat := message.sender_chat:
                            if chat.id != channel_id:
                                if chat.type == ChatType.CHANNEL:
                                    retrieved_channel = await client.get_chat(chat_id=chat.id)
                                    subscribers = retrieved_channel.members_count

                                    if subscribers >= min_number_of_subscribers:
                                        received_data.add(
                                            (f"https://t.me/{retrieved_channel.username}", subscribers)
                                        )

                except pyrogram.errors.exceptions.flood_420.FloodWait:
                    print("Таймаут для обхода блокировки...")
                    time.sleep(60)
                    continue

                except Exception:
                    continue

    return list(received_data)


async def get_channel_id_from_link(client: pyrogram.Client, channel_link: str) -> int:
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
    channel_url_pattern = re.compile(r"t\.me/([A-Za-z0-9_]+)")
    match = channel_url_pattern.search(bio)
    return match.group(0) if match else None


def custom_parse(client, user):
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