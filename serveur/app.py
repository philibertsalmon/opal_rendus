from backend.school import School

from tornado.websocket import WebSocketHandler
from tornado.web import Application
from tornado.ioloop import IOLoop, PeriodicCallback
import json
from datetime import datetime

ip_server = "172.16.16.8"
port = 3080

#INITIALISATION

# Création d'une School vide
global school
school = School()

# Seulement la première salle/le premier client à se connecter gère le scrap de Oasis et envoie à tous les autres clients les infos, périodiquement, avec une période de rafraichissement de refresh_time minutes.
refresh_time = 1 #min
first_client = True #pour identifier le premier client, celui qui gère les communications Oasis

class RoomSocketHandler(WebSocketHandler):
    def open(self):
        global first_client
        self.first_msg = True
        self.room_id = None #en attendant que la salle envoie son id
        self.callback_stop = False #seul le premier client à se connecter devra stopper la call_back
        if first_client:
            # Le premier client gère le rafraichissement et l'envoi, périodiquement
            first_client = False
            self.callback = PeriodicCallback(self.send_updates, refresh_time * 60000)
            self.callback.start()
            self.callback_stop = True
        print("nouvelle connection")
    
    def send_updates(self):
        """Envoi des données Oasis.
        """
        print("updating...")
        school.update()
        print("sending...")
        print(school.rooms)
        for room in school.rooms.values():
            print(room[0].room_id)
            if room[1]: #booléen qui teste si la connection est toujours active, si la salle ne s'est pas déconnectée
                room[0].send_reservations()
                print("sent")
        # End script at the end of the day
        if datetime.now().hour >= 21:
            quit()
    
    def on_message(self, message):
        print(message)
        message_decode = json.loads(message)
        if self.first_msg:
            # Gère la nouvelle connection
            self.room_id = message_decode["id"]
            self.first_msg = False
            school.new_room(self.room_id, self)
            print(school.rooms)
        else:
            request_type = message_decode["requete"]
            now = datetime.now()

            if request_type == "prise de salle":
                duration = message_decode["duree"]
                school.rooms[self.room_id][0].new_occupation(now, duration)
                print("new occup")
                print(school.rooms[self.room_id][0].occupation)

            elif request_type == "recherche de salle":
                room_to_go = school.search_room(now, message_decode)
                self.write_message(json.dumps({"requete": "salle", "id": room_to_go}))
                print(f"room envoyée : {room_to_go}")
    
    def on_close(self):
        if self.callback_stop:
            self.callback.stop() #TODO : problème, si le premier client se déconnecte dans la journée, beug de tous les autres, plus mis à jour
        school.rooms[self.room_id] = [school.rooms[self.room_id][0], False] # La connection n'est plus active
        print("byebye")


if __name__ == '__main__':
    app = Application([(r'/ws', RoomSocketHandler)])
    app.listen(port, ip_server)
    IOLoop.instance().start()