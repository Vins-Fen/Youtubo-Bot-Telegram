import json
from dataclasses import dataclass
import requests
from pytube import YouTube

YTAPI_KEY= "AIzaSyDnXyjJ7CltocH4RjDFf7D3S5lKfXHMssM"

@dataclass
class Video:
    titolo: str
    link: str
    n_view: int
    n_commenti: int
    n_like: int


def newVideo(titolo: str, link: str, n_view:int, n_commenti: int, n_like: int) -> Video:
    return Video(titolo, link, n_view, n_commenti, n_like)

def to_dict(self):
    return {
        "titolo": self.titolo,
        "link": self.link,
        "n_view": self.n_view,
        "n_commenti": self.n_commenti,
        "n_like": self.n_like
    }

@staticmethod
def from_dict(data: dict):
    """Crea un oggetto Video da un dizionario."""
    return Video(
        titolo=data["titolo"],
        link=data["link"],
        n_view=data["n_view"],
        n_commenti=data["n_commenti"],
        n_like=data["n_like"]
    )

def get_video_info(link: str):
    # Supponendo che 'link' contenga l'ID del video.
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

        # Puoi aggiungere ulteriori campi se necessari
        return {"title": title, "link": link, "views": views, "likes": likes, "comments": comment_count}
    else:
        return {"error": "Video Not Found"}





