import re

from googleapiclient.discovery import build


def find_youtube_accounts(
    link: str,
    min_number_of_subscribers: int,
    number_of_posts: int,
) -> list[tuple[str, int]]:
    # Создаем клиента для работы с youtube
    youtube = build("youtube", "v3", developerKey="AIzaSyC3MF-KJ3gFJaWULMCIR8Bluxw6sgcraqg")

    # Получаем `id` канала, используя ссылку на него
    username = extract_channel_identifier_from_link(link=link)
    search_request = youtube.search().list(
        part="snippet",
        q=username,
        type="channel",
        maxResults=1
    )
    search_response = search_request.execute()
    channel_id = search_response["items"][0]["snippet"]["channelId"]

    # Получаем указанное количество последних видео пользователя
    video_ids = []
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=number_of_posts,
        order="date"
    )
    response = request.execute()
    for item in response.get("items", []):
        if item["id"]["kind"] == "youtube#video":
            video_ids.append(item["id"]["videoId"])

    # Получаем комментарии и информацию о каналах авторов
    received_data: set[tuple[str, int]] = set()
    print(video_ids)  # временный код
    for video_id in video_ids:
        comments_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=2,  # временно
            order="relevance",
        )
        comments_response = comments_request.execute()

        for comment_item in comments_response.get("items", []):
            author_channel_id = comment_item["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"]
            if author_channel_id != channel_id:
                channel_request = youtube.channels().list(
                    part="snippet,statistics",
                    id=author_channel_id
                )
                channel_response = channel_request.execute()

                if channel_response["items"]:
                    author_channel_info = channel_response["items"][0]
                    subscriber_count = int(author_channel_info["statistics"]["subscriberCount"])

                    if subscriber_count >= min_number_of_subscribers:
                        author_channel_link = f"https://www.youtube.com/channel/{author_channel_id}"
                        received_data.add((author_channel_link, subscriber_count))

    return list(received_data)


def extract_channel_identifier_from_link(link: str) -> str:
    username_pattern = re.compile(r"@([^/?]+)")

    user_match = username_pattern.search(link)
    if user_match:
        return user_match.group(1)

