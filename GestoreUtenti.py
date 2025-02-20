from dataclasses import dataclass
from User import User

@dataclass
class Gesture:
    name: str
    Lutenti: list[User]


def startGesture(self,name: str):
    self.name = name
    self.Lutenti = []
    return self

# Verifico l'admin se presente nella lista
def chack_admins(id_to_check: int):
    for user in User:
        if user.id == id_to_check:
            return True
        else:
            return False

