import os
from dataclasses import dataclass, asdict
import json
import csv
OWNER_ID= os.environ.get('OWNER_ID')

@dataclass
class User:
    id: int
    username: str
    score: int #Classe di tipo reputation
    role: str



def initUser(user_id: int, username: str, role: str = "user") -> User:
    return User(user_id, username, 0, role)



def saveuser(user: User, filename: str = "user.json"):
    if user_exists(user.id, filename):
        return print(f"User {user.id} already exists")
    else:
        try:
            with open(filename, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            # Se il file non esiste, inizializza una lista vuota
            data = []

    data.append(asdict(user))

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def getUId(user):
    return user.id

def getName(user):
    return user.username

def getRole(user):
    return user.role
def load_users(filename: str = "user.json") -> list[dict]:
    if not os.path.isfile(filename):
        return []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def user_exists(
    user_id: int,
    filename: str = "user.json",
) -> bool:
    users = load_users(filename)

    return any(
        user.get("id") == user_id
        for user in users
    )



def aumentoscore(user):
    user.score += 1
