import discord
import yt_dlp
import asyncio

# 全域記錄播放清單，或你自己用 dict 儲存每個 guild 的播放清單
queues = {}


def get_queue(guild):
    if guild.id not in queues:
        queues[guild.id] = []
    return queues[guild.id]

# 播放下一首音樂的 coroutine
async def play_next(ctx, vc, bot):
    queue = get_queue(ctx.guild)
    if not queue:
        await ctx.send("🎵 播放清單已空。")
        return

    url, title = queue.pop(0)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }

    # 用非同步方式取得音訊 url
    loop = asyncio.get_event_loop()
    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info['url'], info.get('title', '未知標題')
    try:
        audio_url, _ = await loop.run_in_executor(None, extract)
    except Exception as e:
        await ctx.send(f"❌ 解析音訊失敗：{e}")
        return await play_next(ctx, vc, bot)  # 跳過失敗歌曲繼續下一首

    # 建立音訊來源
    source = discord.FFmpegPCMAudio(audio_url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn')
    vc.play(source, after=lambda e: after_playing(e, ctx, vc, bot))

    await ctx.send(f"▶️ 開始播放：{title}")

# after callback 不能是 async，改用這種寫法，把 coroutine 丟給事件迴圈跑
def after_playing(error, ctx, vc, bot):
    if error:
        print(f"播放錯誤：{error}")
    # 用 bot.loop.create_task 保證事件迴圈存在
    bot.loop.create_task(play_next(ctx, vc, bot))

# 播放音樂主函式，直接呼叫播放下一首或特定歌曲
def playing_music(ctx, vc, bot, url, title):
    queue = get_queue(ctx.guild)

    # 先清空清單並插入此曲，表示「立即插播」
    queue.insert(0, (url, title))  # 你可以在此修改 title 或改從 yt_dlp 取得

    # 如果沒在播，啟動播放下一首
    if not vc.is_playing():
        bot.loop.create_task(play_next(ctx, vc, bot))
