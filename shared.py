import csv

import json

def init():
    global state, statuses, trek_list, slurps, trashes, beescript
    state = {
        "guild": {},
        "global": {}
    }

    with open('resources/db.json', 'r', encoding="utf8") as file:
        dbs = file.read()
        dbj = json.loads(dbs)


    # load resources from db
    slurps = {"slurs": [dbj["slurs"][k]["slur"] for k in dbj["slurs"]],
              "chances": [dbj["slurs"][k]["chance"] for k in dbj["slurs"]]} #read_slurs(conn)
    statuses = {"statuses": [dbj["statuses"][k]["status"] for k in dbj["statuses"]],
                "chances": [dbj["statuses"][k]["chance"] for k in dbj["statuses"]]} #read_statuses(conn)

    # load static resources
    with open('resources/beemovie.txt', 'r', encoding="utf8") as file:
        beescript = file.read().split("\n\n  \n")
    with open('resources/lists/zene.txt', 'r', encoding="utf8") as file:
        trek_list = file.read().split("\n\n")
    with open('resources/lists/trash.csv', newline='', encoding="utf8") as trash_csv:
        trashes = list(csv.reader(trash_csv, delimiter=','))
