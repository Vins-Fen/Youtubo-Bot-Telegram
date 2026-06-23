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

    # Aggiunge il nuovo youtuber (convertito in dict)
    data.append(asdict(user))

    # Salva nuovamente i dati nel file, formattati con indentazione
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def getUId(user):
    return user.id

def getName(user):
    return user.username

def getRole(user):
    return user.role


def setAdmin(id: int):
    if id==OWNER_ID:
        role = "admin"

def user_exists(user_id: int, filename: str = "users.json") -> bool:
    if not os.path.isfile(filename):
        return False

    with open(filename, mode="r", newline="") as file:
        reader = csv.reader(file)
        next(reader, None)  # Salta l'intestazione
        return any(row[0] == str(user_id) for row in reader)


def to_dict(self):
    return {
        "user_id": self.id,
        "username": self.username,
        "role": self.role,
        "score": self.score
    }


def from_dict(data: dict):
    User(
        id=data["user_id"],
        username=data["username"],
        role=data["role"],
        score=data["score"]
    )


def aumentoscore(user):
    user.score += 1
