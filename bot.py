import discord
from discord.ext import commands
import asyncio
from config import get_token
from utils import extract_info, is_url
from music import get_queue, playing_music
from SongSelectView import SongSelect
from discord.ui import View

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.command()
async def add(ctx, *, query: str):
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True, 'extract_flat': True, 'default_search': 'ytsearch5'}

    if is_url(query):
        info = await extract_info(query, ydl_opts)
        if not info:
            await ctx.send("❌ 找不到歌曲")
            return
        url = info.get('webpage_url') or info.get('url') or query
        title = info.get('title', '未知標題')
        queue = get_queue(ctx.guild)
        queue.append((url, title))
        await ctx.send(f"✅ 已加入清單：{title}")

    else:
        info = await extract_info(f"ytsearch5:{query}", ydl_opts)
        entries = info.get('entries') if info else None
        if not entries:
            await ctx.send("❌ 找不到歌曲")
            return
        select = SongSelect(entries, ctx, mode='add')
        view = View()
        view.add_item(select)
        await ctx.send("請選擇要加入的歌曲：", view=view)

@bot.command()
async def queue(ctx):
    queue = get_queue(ctx.guild)
    if not queue:
        await ctx.send("清單是空的")
        return
    text = "\n".join(f"{i+1}. {title}" for i, (url, title) in enumerate(queue))
    await ctx.send(f"🎶 目前播放清單：\n{text}")

@bot.command()
async def play(ctx, *, query: str = None):
    if not ctx.author.voice:
        await ctx.send("你要先進語音頻道！")
        return
    voice_channel = ctx.author.voice.channel
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if not vc:
        vc = await voice_channel.connect()
    if vc.is_playing():
        vc.stop()
    queue = get_queue(ctx.guild)

    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True, 'extract_flat': True}

    if query is None:
        if not queue:
            await ctx.send("播放清單是空的，請先加入歌曲。")
            return
        url, title = queue.pop(0)
        await ctx.send(f"開始播放清單第一首：{title}")
        playing_music(ctx, vc, bot, url, title)
        return

    if is_url(query):
        info = await extract_info(query, ydl_opts)
        audio_url = info.get('url', query)
        title = info.get('title', '未知標題')
        await ctx.send(f"開始播放：{title}")
        playing_music(ctx, vc, bot, audio_url, title)
        return

    info = await extract_info(f"ytsearch5:{query}", ydl_opts)
    entries = info.get('entries') if info else None
    if not entries:
        await ctx.send("❌ 找不到歌曲")
        return
    select = SongSelect(entries, ctx, vc=vc, bot=bot, mode='play')
    view = View()
    view.add_item(select)
    await ctx.send("請選擇要撥放的歌曲：", view=view)

@bot.command()
async def skip(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send("跳過！")
    else:
        await ctx.send("沒歌在播～")

@bot.command()
async def pause(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and vc.is_playing():
        vc.pause()
        await ctx.send("已暫停")
    else:
        await ctx.send("目前沒有在播放音樂")

@bot.command()
async def resume(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and vc.is_paused():
        vc.resume()
        await ctx.send("繼續播放")
    else:
        await ctx.send("目前沒有暫停的音樂")

@bot.command()
async def stop(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc and (vc.is_playing() or vc.is_paused()):
        vc.stop()
        await ctx.send("停止播放")
    else:
        await ctx.send("目前沒有在播放音樂")

@bot.command()
async def clear(ctx):
    queue = get_queue(ctx.guild)
    queue.clear()
    await ctx.send("清單已清空")

@bot.command()
async def leave(ctx):
    vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if vc:
        await vc.disconnect()
        await ctx.send("掰囉！")
    else:
        await ctx.send("我不在語音頻道裡喔。")

bot.run(get_token())
