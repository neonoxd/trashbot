cfg = {
    "prefix": "k!",
    "goofies": [232184416259014657],  # unused
    "trashwatch_interval": 120
}

trash_list = {
    "yt": {
        "tibi": "UCxA1n--ZPGIWzFEZ98aLzTQ",
        "nagylaci": "UCxFpm3Qlpbe2Nunm02rtXXw",
        "martin": "UCVXMCQyIAhvbrH0lyRb9MMQ"
    },
    "twitch": {
        "sodi": "235138165",
        "bturbo": "37738094",
        # "test": "23528098"
    }
}

trash_map = {
    "tibi": {"link": "https://youtube.com/channel/{}".format(trash_list["yt"]["tibi"]), "name": "Tibcédesz"},
    "nagylaci": {"link": "https://youtube.com/channel/{}".format(trash_list["yt"]["nagylaci"]), "name": "Nagy Laci"},
    "martin": {"link": "https://youtube.com/channel/{}".format(trash_list["yt"]["martin"]), "name": "Martin Horváth"},
    "sodi": {"link": "https://twitch.tv/sodivlog", "name": "Veknifejű"},
    "bturbo": {"link": "https://twitch.tv/bturbo", "name": "brétúró"},
    #"test": {"link": "https://twitch.tv/avoidingthepuddle", "name": "test"}
}
