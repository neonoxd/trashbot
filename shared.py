import csv
def init():
    global state,statuses,legjob_zene_list,beszolasok,trashes
    state = {
        "attachedChannels": {}
    }
    with open('resources/lists/beszolas.txt', 'r', encoding="utf8") as file:
        beszolasok = file.read().split("\n")
    with open('resources/lists/zene.txt', 'r', encoding="utf8") as file:
        legjob_zene_list = file.read().split("\n\n")
    with open('resources/lists/idle_statuses.txt', 'r', encoding="utf8") as file:
        statuses = file.read().split("\n")
    with open('resources/lists/trash.csv', newline='', encoding="utf8") as csvfile:
        trashread = csv.reader(csvfile, delimiter=',')
        trashes = list(trashread)

