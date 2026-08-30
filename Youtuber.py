import json
import logging
from dataclasses import asdict, dataclass

from googleapiclient.discovery import build

from Video import YTAPI_KEY

logger = logging.getLogger(__name__)


@dataclass
class Youtuber:
    yid: str
    user_id: int
    handle: str
    counter_followers: int
    total_views: int


def get_channel_id_from_handle(
    youtube_handle: str,
) -> str | None:
    handle = youtube_handle.removeprefix("@")

    youtube = build(
        "youtube",
        "v3",
        developerKey=YTAPI_KEY,
    )

    try:
        response = youtube.search().list(
            part="snippet",
            q=handle,
            type="channel",
            maxResults=1,
        ).execute()

        if not response.get("items"):
            return None

        return response["items"][0]["id"]["channelId"]

    except Exception:
        logger.exception(
            "Errore durante la ricerca del canale YouTube"
        )
        return None


def newYoutuber(
    name: str,
    user_id: int,
    youtube_handle: str,
    subscriber_count: int,
    total_views: int,
) -> Youtuber:
    return Youtuber(
        yid=name,
        user_id=user_id,
        handle=youtube_handle,
        counter_followers=subscriber_count,
        total_views=total_views,
    )


def salva_su_file(
    youtuber: Youtuber,
    filename: str = "youtubers.json",
) -> None:
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            data = []

    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(asdict(youtuber))

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )