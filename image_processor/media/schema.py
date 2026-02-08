from pydantic import Field, HttpUrl, field_validator

from image_processor.models import AppBase


class TextToSpeechSchema(AppBase):
    text: str = Field(min_length=1, max_length=5_000)
    voice: str = Field(min_length=1, max_length=100)


class CreateMediaSchema(AppBase):
    task_name: str = Field(min_length=1, max_length=100)
    video_blocks: dict[str, list[HttpUrl]] = Field(min_length=1, max_length=10)
    audio_blocks: dict[str, list[HttpUrl]] = Field(min_length=1)
    text_to_speech: list[TextToSpeechSchema] = Field(min_length=1)

    @field_validator("video_blocks", "audio_blocks")
    @classmethod
    def list_not_empty(cls, v: dict[str, list[HttpUrl]]) -> dict[str, list[HttpUrl]]:
        for key, url_list in v.items():
            if not url_list:
                raise ValueError(f"The list for block '{key}' cannot be empty.")
        return v
