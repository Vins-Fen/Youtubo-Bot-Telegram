import csv
import json
import os
from dataclasses import dataclass, asdict

from googleapiclient.discovery import build

from Video import Video, YTAPI_KEY


@dataclass
class Youtuber:
    yid: str
    user_id: int
    handle: str
    counter_followers: int
    total_views: int


def get_channel_id_from_handle(youtube_handle):
    if youtube_handle.startswith("@"):  # Rimuove il simbolo '@' se presente
        youtube_handle = youtube_handle[1:]

    youtube = build("youtube", "v3", developerKey=YTAPI_KEY)

    try:
        request = youtube.search().list(
            part="snippet",
            q=youtube_handle,
            type="channel",
            maxResults=1
        )
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            channel_id = response["items"][0]["id"]["channelId"]


            return channel_id
        else:
            return None
    except Exception as e:
        print("Errore API YouTube:", e)
        return None



def newYoutuber( id: str, user_id:int, youtube_handle: str, subscriber_count: int, total_views: int) -> Youtuber:
          return Youtuber(id, user_id, youtube_handle, subscriber_count, total_views)






def add_video(self, user_id, video):
            """Aggiunge un video alla lista."""
            if isinstance(video, Video):  # Controlliamo che sia un oggetto Video
                self.videos.append(video)
            else:
                raise ValueError("L'oggetto deve essere di tipo Video.")

def salva_su_file(youtuber: Youtuber, filename: str = "youtubers.json"):
    try:
        # Legge i dati già presenti nel file
        with open(filename, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        # Se il file non esiste, inizializza una lista vuota
        data = []

    # Aggiunge il nuovo youtuber (convertito in dict)
    data.append(asdict(youtuber))

    # Salva nuovamente i dati nel file, formattati con indentazione
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def carica_da_file(filename: str = "youtubers.json"):
   # Carica e restituisce la lista di youtuber salvati nel file JSON.
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return []



def to_dict(self):
    """Converte l'oggetto Youtuber in un dizionario per salvarlo in JSON."""
    return {
        "id": self.yid,
        "handle": self.handle,
        "subscribers": self.counter_followers,
        "total_views": self.total_views,
    }


@staticmethod
def from_dict(data: dict):
    """Crea un oggetto Youtuber da un dizionario."""
    youtuber = Youtuber(
        yid=data["channel_id"],
        handle=data["handle"],
        counter_followers=data["subscribers"],
        total_views=data["total_views"],

    )
    youtuber.videos = [Video.from_dict(v) for v in data.get("videos", [])]  # Ricostruisce la lista di video
    return youtuber
