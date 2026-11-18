import asyncio
from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager

async def _fetch_media():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    if current_session:
        info = await current_session.try_get_media_properties_async()
        playback = current_session.get_playback_info()
        
        is_playing = (playback.playback_status == 4) # 4 = Playing
        return {
            "title": info.title or "Sem título",
            "artist": info.artist or "Desconhecido",
            "playing": is_playing
        }
    return None

def get_current_media() -> dict:
    try:
        return asyncio.run(_fetch_media()) or {"title": "Nenhuma mídia", "artist": "-", "playing": False}
    except Exception:
        return {"title": "Nenhuma mídia", "artist": "-", "playing": False}