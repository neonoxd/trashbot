import csv

from utils import read_slurs, read_statuses


def init():
    global state, statuses, trek_list, slurps, trashes, beescript
    from main import conn
    state = {
        "guild": {},
        "global": {}
    }
    # load resources from db
    slurps = read_slurs(conn)
    statuses = read_statuses(conn)

    # load static resources
    with open('resources/beemovie.txt', 'r', encoding="utf8") as file:
        beescript = file.read().split("\n\n  \n")
    with open('resources/lists/zene.txt', 'r', encoding="utf8") as file:
        trek_list = file.read().split("\n\n")
    with open('resources/lists/trash.csv', newline='', encoding="utf8") as trash_csv:
        trashes = list(csv.reader(trash_csv, delimiter=','))
