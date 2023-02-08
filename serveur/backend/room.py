import json
from datetime import datetime, timedelta

class Room:
    def __init__(self, room_id, client) :
        self.room_id = room_id
        self.client = client
        self.occupation = None

    def update_reservations(self, data:list[dict]):
        self.reservations = data
        print(f"updated with data : {data}")
    
    def new_occupation(self, now:datetime, duration:int):
        self.occupation = [now, now + timedelta(minutes=duration)]
    
    
    def is_booked(self, now, duration):
        duration_ = timedelta(minutes=duration)
        booked = False
        for reservation in self.reservations:
            début = datetime(year=now.year, month = now.month, day = now.day, hour = int(reservation['from_'][:2]),minute = int(reservation['from_'][3:]))
            fin = datetime(year=now.year, month = now.month, day = now.day, hour = int(reservation['to'][:2]),minute = int(reservation['to'][3:]))
            booked += ((now >= début) & (now <= fin)) | ((now + duration_ >= début) & (now + duration_ <= fin)) | ((now <= début) & (now + duration_ >= fin))
        return booked
    
    def is_occupied(self, now, duration):
        if self.occupation == None:
            return False
        else:
            return (now < self.occupation[1]) | (now + timedelta(minutes=int(duration or 0)) > self.occupation[0])
    
    def is_available(self, now, duration):
        # Par défaut, on ne propose pas de salle à moins de 10 minutes avant la prochaine réservation
        return ~(self.is_booked(now, int(duration or 0)) | self.is_occupied(now, int(duration or 0)))
    
    def send_reservations(self):
        self.client.write_message(json.dumps({"requete": "edt", "reservations": self.reservations}))