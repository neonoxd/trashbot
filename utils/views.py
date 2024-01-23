import discord


class SimpleView(discord.ui.View):
    def __init__(self, *items, timeout=180):
        super().__init__(timeout=timeout)
        for item in items:
            self.add_item(item)
