from .room import Room
from .scrap_oasis import scrap
import json
from .room_priorities.roomDict import rooms

class School:
    def __init__(self):
        self.rooms:dict[str: [Room, bool]] = {}
    
    def new_room(self, room_id, client):
        self.rooms[room_id] = [Room(room_id, client), True]
    
    def search_room(self, now, data):
        """Retourne la salle la plus proche, libre, selon certains critères optionnels.
        La liste des priorités a été stockée dans priorityLists.txt, cf. README.md"""
        from_room = data["id"]
        tabb = data["tabb"]
        tabn = data["tabn"]
        videop = data["videop"]
        dur = data["dur"]
        try:
            dur=int(dur)
        except:
            dur=10
        with open("/home/pi/serveur/backend/room_priorities/priorityLists.txt", 'r') as file:
            priorityList = json.loads(file.read())[from_room]
        for room2go_id in priorityList :
            try :
                if self.rooms[room2go_id][0].is_available(now, dur) & (tabb & rooms[from_room]['tabb'] | ~tabb) & (tabn & rooms[from_room]['tabn'] | ~tabn) & (videop & (rooms[from_room]['videop']|rooms[from_room]['tele']) | ~videop):
                    return room2go_id
            except KeyError as ke:
                pass
        return ""
    
    def update(self):
        """Scrap Oasis et update les salles"""
        scrap(self)
        print("update done")