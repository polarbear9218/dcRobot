import yt_dlp
import asyncio

async def extract_info(url, ydl_opts):
    loop = asyncio.get_event_loop()
    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
    return await loop.run_in_executor(None, extract)

def is_url(text):
    return text.startswith("http://") or text.startswith("https://")
