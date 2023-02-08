import bs4 
from selenium import webdriver
from time import sleep

url = 'https://oasis.mines-paristech.fr/prod/bo/?targetProject=oasis_ensmp&public#codepage=ROOM_MANAGER_VIEW&view=timelineDay'


def scrap(school):
    browser = webdriver.Chrome()
    browser.get(url)

    sleep(20)

    res = browser.page_source
    oasis = bs4.BeautifulSoup(res,'html.parser')  
    browser.close()

    # Mise en forme des données

    table = oasis.find_all('table', class_="table-bordered")[4]
    rooms = table.find_all('tr')

    for room in rooms:
        try:
            room_reservations = []
            room_id = room['data-resource-id']
            events = room.find_all('a', class_="fc-timeline-event fc-h-event fc-event fc-start fc-end")
            for event in events:
                data = event["title"]
                from_ = data[1:6]
                to = data[7:12]
                title = data[14:]
                room_reservations.append({'title': title, 'from_': from_, 'to': to})
            room_reservations = sorted(room_reservations, key=lambda room_reservations: room_reservations['from_'])
            school.rooms[room_id][0].update_reservations(room_reservations)
        except KeyError as ke:
            pass