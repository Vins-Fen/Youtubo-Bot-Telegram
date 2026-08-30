from dataclasses import dataclass
from urllib.parse import urlparse, parse_qs
import requests
from googleapiclient.errors import HttpError
from telegram import Update
from telegram.ext import ContextTypes
import os
import logging
from googleapiclient.discovery import build
logger=logging.getLogger(__name__)

YTAPI_KEY= os.getenv("YOUTUBE_TOKEN_API")

@dataclass
class Video:
    titolo: str
    youtuber: str
    link: str
    n_view: int
    n_commenti: int
    n_like: int
    tag: list[str]


def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)

    # 1 Gestione dei classici URL di YouTube
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query_params = parse_qs(parsed_url.query)
        video_ids = query_params.get("v")
        if video_ids:
            return video_ids[0]

    # 2 Gestione degli URL corti (youtu.be/ID)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")

    # 3 Gestione degli embed (youtube.com/embed/ID)
    if "embed" in parsed_url.path:
        return parsed_url.path.split("/")[-1]

    return None  # Se l'URL non è valido o non riconosciuto

def prendi_tag_da_youtube(video_id: str) -> list[str]:
    """
    Chiama l'API di YouTube per ottenere i tag del video
    """
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YTAPI_KEY}"
    response = requests.get(url)
    data = response.json()

    try:
        tags = data["items"][0]["snippet"].get("tags", [])
        return tags
    except (KeyError, IndexError):
        return []

def newVideo(titolo: str, link: str, n_view:int, n_commenti: int, n_like: int) -> Video:
    id=extract_video_id(link)
    tags= prendi_tag_da_youtube(id)
    #li metto nell'oggetto video
    return Video(titolo, link, n_view, n_commenti, n_like, tags)


def get_video_info(link: str):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={link}&key={YTAPI_KEY}"
    response = requests.get(url)
    data = response.json()

    if "items" in data and len(data["items"]) > 0:
        item = data["items"][0]
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})

        title = snippet.get("title")
        views = statistics.get("viewCount")
        likes = statistics.get("likeCount", 0)
        comment_count = statistics.get("commentCount", 0)


        return {"title": title, "link": link, "views": views, "likes": likes, "comments": comment_count}
    else:
        return {"error": "Video Not Found"}


async def get_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        youtube = build('youtube', 'v3', developerKey=YTAPI_KEY)
        if update.message.reply_to_message:
            raw_text = update.message.reply_to_message.text
        else:
            raw_text = update.message.text
        if raw_text.startswith("/tipo"):
            raw_text = raw_text.replace("/tipo", "").strip()

        video_id = extract_video_id(raw_text)
        if not video_id:
            await update.message.reply_text("❌ Errore: link non valido.")
            return "ERRORE"

        request = youtube.videos().list(
            part='snippet',
            id=video_id
        )

        response = request.execute()


        if 'items' in response and len(response['items']) > 0:
            category = response['items'][0]['snippet']['categoryId']
            conversione= get_category_name(category)
            await context.bot.send_message(chat_id=update.message.chat_id, text=f"📌 Categoria video: {conversione}")

        else:
            await update.message.reply_text("❌ Errore: video non trovato.")
            return "ERRORE"

    except HttpError as e:
        logger.error("❌ Errore HTTP:", e)
        await update.message.reply_text("❌ Errore con YouTube API. Riprova più tardi.")
        return "ERRORE"

    except Exception as e:
        logger.error("❌ Errore generico:", e)
        await update.message.reply_text("❌ Si è verificato un errore imprevisto.")
        return "ERRORE"

CATEGORY_MAP = {
    "1": "Film & Animazione",
    "2": "Auto & Veicoli",
    "10": "Musica",
    "15": "Animali",
    "17": "Sport",
    "20": "Gaming",
    "22": "Vlog",
    "23": "Comedy",
    "24": "Intrattenimento",
    "25": "Notizie & Politica",
    "26": "How-to & Style",
    "27": "Istruzione",
    "28": "Scienza & Tecnologia"
}



def get_category_name(category_id):
    return CATEGORY_MAP.get(str(category_id), "Sconosciuto")




