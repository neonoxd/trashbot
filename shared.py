import csv


def init():
    global state, statuses, trek_list, slurps, trashes, beescript
    state = {
        "guild": {},
        "global": {}
    }
    # load static resources TODO: make some of them not static
    with open('resources/beemovie.txt', 'r', encoding="utf8") as file:
        beescript = file.read().split("\n\n  \n")
    with open('resources/lists/beszolas.txt', 'r', encoding="utf8") as file:
        slurps = file.read().split("\n")
    with open('resources/lists/zene.txt', 'r', encoding="utf8") as file:
        trek_list = file.read().split("\n\n")
    with open('resources/lists/idle_statuses.txt', 'r', encoding="utf8") as file:
        statuses = file.read().split("\n")
    with open('resources/lists/trash.csv', newline='', encoding="utf8") as trash_csv:
        trashes = list(csv.reader(trash_csv, delimiter=','))
