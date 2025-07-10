from discord.ui import Select, View
import discord
from music import get_queue, playing_music

class SongSelect(Select):
    def __init__(self, entries, ctx, vc=None, bot=None, mode=None):
        options = []
        for entry in entries:
            label = entry.get('title', '未知標題')
            value = entry.get('webpage_url') or entry.get('url') or entry.get('id') or '無連結'
            options.append(discord.SelectOption(label=label, value=value))
        super().__init__(placeholder="選擇要加入的歌曲", options=options)
        self.ctx = ctx
        self.mode = mode
        self.vc = vc
        self.bot = bot

    async def callback(self, interaction):
        url = self.values[0]
        title = None
        for option in self.options:
            if option.value == url:
                title = option.label
                break
        if self.mode == "add":
            queue = get_queue(self.ctx.guild)
            queue.append((url, title))
            await interaction.response.edit_message(content=f"✅ 已加入清單：{title}", view=None)
        elif self.mode == "play":
            await interaction.response.send_message(f"▶️ 播放：{url}")
            playing_music(self.ctx, self.vc, self.bot, url, title)
