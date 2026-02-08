import logging
import os
import uuid

import aiohttp

from image_processor.config import get_settings
from image_processor.core.timer import timer


class ElevenLabsClient:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._mapped_name: dict[str, str] = {}

    @timer
    async def get_speech_by_text(
        self, session: aiohttp.ClientSession, text: str, voice_name
    ) -> str:
        if not self._mapped_name:
            ok = await self._fetch_name_id_map()
            if not ok:
                raise Exception("Error when fetching voice id")

        voice_id = self._get_speech_id_by_name(voice_name)
        headers = {
            "xi-api-key": get_settings().ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        filename = f"/tmp/{uuid.uuid4()}.mp3"
        try:
            async with session.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                json=data,
                headers=headers,
                timeout=60,
            ) as response:
                if response.status != 200:
                    self._logger.error(
                        f"Failed on call to ElevenLabs API: {response.status} - {await response.text()}"
                    )
                    raise Exception("Failed on call to ElevenLabs API")
                with open(filename, "wb") as f:
                    f.write(await response.read())
                return filename
        except Exception as e:
            if os.path.exists(filename):
                os.remove(filename)
            raise e

    def _get_speech_id_by_name(self, name: str):
        """Get speech id by name or fallback"""
        speech_id = self._mapped_name.get(name)
        if not speech_id:
            self._logger.warning("Speech id by name not found")
        return speech_id or "JBFqnCBsd6RMkjVDRZzb"

    async def _fetch_name_id_map(self):
        if self._mapped_name:
            return self._mapped_name
        url = "https://api.elevenlabs.io/v1/voices"

        headers = {
            "xi-api-key": get_settings().ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                text = await response.text()
                if response.status == 401:
                    self._logger.warning(f"API KEY is invalid {text}")
                    return False

                if response.status != 200:
                    self._logger.warning("Failed to fetch voice")
                    return False

                data = await response.json()
                mapped_name = {}
                for voice in data.get("voices", []):
                    full_name = voice.get("name", "")
                    voice_id = voice.get("voice_id", "")

                    mapped_name[full_name] = voice_id
                    short_name = full_name.split(" ")[0].split("-")[0].strip()
                    if short_name not in mapped_name:
                        mapped_name[short_name] = voice_id
                self._mapped_name = mapped_name
                return True

    async def is_valid(self) -> bool:
        if self._mapped_name:
            return True
        return await self._fetch_name_id_map()
