from pydantic import Field, HttpUrl

from image_processor.models import AppBase

class MediaList(AppBase):
    url_list: list[HttpUrl] = Field(min_length=1, max_length=10)

class TextToSpeechSchema(AppBase):
    text: str = Field(min_length=1, max_length=5_000)
    voice: str = Field(min_length=1, max_length=100)

class CreateMediaSchema(AppBase):
    task_name: str = Field(min_length=1, max_length=100)
    video_blocks: dict[str, list[HttpUrl]] = Field()
    audio_blocks: dict[str, list[HttpUrl]] = Field()
    text_to_speech: list[TextToSpeechSchema] = Field(min_length=1)
