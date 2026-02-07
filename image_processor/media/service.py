import ffmpeg

from image_processor.broker import Broker
from image_processor.core.constants import CHUNK_SIZE
from image_processor.google_clients.google_drive_client import GoogleDriveClient
from image_processor.media.schema import CreateMediaSchema


class MediaService:

    def __init__(
            self,
            google_drive_client: GoogleDriveClient,
            broker: Broker,
    ):
        self._google_drive_client = google_drive_client
        self._broker = broker

    @staticmethod
    def concat_videos(payload: CreateMediaSchema):
        videos = []
        audio = []
        for _, media_list in payload.video_blocks.items():
            videos.extend(media_list)

        for _, audio_list in payload.audio_blocks.items():
            audio.extend(audio_list)

        streams = []
        for video in videos:
            stream = ffmpeg.input(str(video)).video
            stream = stream.filter("scale", 720, 1280).filter("fps", 30)
            streams.append(stream)

        if len(streams) == 1:
           v = streams[0]
        else:
            v = ffmpeg.concat(*streams, v=1, a=0).node[0]

        audio = ffmpeg.input(str(audio[0])).audio.filter('aloop', loop=-1, size=2_000_000_000)
        return (
            ffmpeg.output(
            v,
            audio,
            "pipe:1",
            format="mp4",
            vcodec="libx264",
            acodec="aac",
            pix_fmt="yuv420p",
            shortest=None,
            movflags="frag_keyframe+empty_moov",
            )
            .overwrite_output()
            .run_async(pipe_stdout=True, pipe_stderr=True)
        )

    async def upload_ffmpeg_to_drive(
            self,
            payload: CreateMediaSchema
    ):
        process = self.concat_videos(payload)

        upload_url, error = await self._google_drive_client.upload_file_in_stream(
            filename=payload.task_name,
            mime_type="video/mp4",
        )
        if error:
            return error

        offset = 0
        current_chunk = process.stdout.read(CHUNK_SIZE)
        while True:
            next_chunk = process.stdout.read(CHUNK_SIZE)
            chunk_len = len(current_chunk)
            start = offset
            end = offset + chunk_len - 1
            if not next_chunk:
                total_size = offset + chunk_len
                error = await self._google_drive_client.upload_chunk(
                    upload_url=upload_url,
                    chunk=current_chunk,
                    start=start,
                    end=end,
                    total=total_size
                )
                if error:
                    return error
                break
            else:
                error = await self._google_drive_client.upload_chunk(
                    upload_url=upload_url,
                    chunk=current_chunk,
                    start=start,
                    end=end,
                    total="*",
                )
                if error:
                    return error
            offset += chunk_len
            current_chunk = next_chunk

        process.wait()

    async def save_file(
            self,
            media_payload: CreateMediaSchema,
    ):
        await self._broker.publish(media_payload)
