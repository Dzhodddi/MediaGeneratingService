import asyncio
import logging
import os
import uuid
import random
import aiohttp
import ffmpeg
from itertools import product

from image_processor.broker import Broker
from image_processor.core.constants import CHUNK_SIZE, FILE_CHUNK_SIZE
from image_processor.core.timer import timer
from image_processor.google_clients.google_drive_client import GoogleDriveClient
from image_processor.media.elevenlabs_client import ElevenLabsClient
from image_processor.media.schema import CreateMediaSchema


class MediaService:
    def __init__(
        self,
        google_drive_client: GoogleDriveClient,
        broker: Broker,
        logger: logging.Logger,
        eleven_labs_client: ElevenLabsClient,
    ):
        self._google_drive_client = google_drive_client
        self._broker = broker
        self._logger = logger
        self._eleven_labs_client = eleven_labs_client

    async def save_file(self, media_payload: CreateMediaSchema):
        await self._broker.publish(media_payload)

    @timer
    async def process_task(self, payload: CreateMediaSchema):
        video_map, audio_list, speech_list, all_assets = await self._prepare_assets(
            payload
        )
        generated_parts = []

        try:
            sorted_block_keys = sorted(payload.video_blocks.keys())
            block_lists = []
            for key in sorted_block_keys:
                paths = [video_map[u] for u in payload.video_blocks[key]]
                block_lists.append(paths)

            combinations = list(product(*block_lists))
            self._logger.info(f"Found {len(combinations)} combinations to generate.")
            random.shuffle(combinations)
            for i, video_combo in enumerate(combinations):
                selected_audio = random.choice(audio_list)
                selected_speech = random.choice(speech_list)
                part_path = await self._generate_part(
                    i, list(video_combo), selected_audio, selected_speech
                )
                generated_parts.append(part_path)

            await self._stitch_and_upload(generated_parts, payload.task_name)
            self._logger.info(f"Finished processing {payload.task_name}")
        except Exception as e:
            self._logger.error(
                f"Worker error: {e} during consuming {payload.task_name}"
            )
        finally:
            for f in all_assets:
                if os.path.exists(f):
                    os.remove(f)
            for f in generated_parts:
                if os.path.exists(f):
                    os.remove(f)

    async def _prepare_assets(self, payload: CreateMediaSchema):
        temp_files = []
        video_map = {}
        speech_semaphore = asyncio.Semaphore(1)

        async def _get_speech_audio(s, text, voice):
            async with speech_semaphore:
                await asyncio.sleep(0.5)
                return await self._eleven_labs_client.get_speech_by_text(s, text, voice)

        async with aiohttp.ClientSession() as session:
            unique_video_urls = set()
            for urls in payload.video_blocks.values():
                unique_video_urls.update(urls)
            video_urls_list = list(unique_video_urls)

            audio_urls = [url for urls in payload.audio_blocks.values() for url in urls]

            v_tasks = [self._download_file(session, u) for u in video_urls_list]
            a_tasks = [self._download_file(session, u) for u in audio_urls]
            speech_tasks = [
                _get_speech_audio(session, item.text, item.voice)
                for item in payload.text_to_speech
            ]

            results = await asyncio.gather(*(v_tasks + a_tasks + speech_tasks))

            v_paths = results[: len(v_tasks)]
            a_paths = results[len(v_tasks) :]
            speech_paths = results[len(v_tasks) + len(a_tasks) :]

            for url, path in zip(video_urls_list, v_paths):
                video_map[url] = path

            temp_files.extend(v_paths + a_paths + speech_paths)

            return video_map, a_paths, speech_paths, temp_files

    @timer
    async def _generate_part(
        self, index: int, video_paths: list, audio_path: str, speech_path: str
    ) -> str:
        part_filename = f"/tmp/part_{index}.mp4"

        process = await asyncio.create_subprocess_exec(
            *self._get_part_args(video_paths, audio_path, speech_path, part_filename),
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Failed to generate part {index}")

        return part_filename

    @timer
    async def _stitch_and_upload(self, part_files: list, task_name: str):
        list_file_path = "/tmp/concat_list.txt"

        with open(list_file_path, "w") as f:
            for part in part_files:
                f.write(f"file '{part}'\n")

        args = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            list_file_path,
            "-c",
            "copy",
            "-movflags",
            "frag_keyframe+empty_moov",
            "-f",
            "mp4",
            "pipe:1",
        ]

        process = await asyncio.create_subprocess_exec(
            *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )

        upload_url = await self._google_drive_client.upload_file_in_stream(
            filename=f"{task_name}.mp4", mime_type="video/mp4"
        )

        offset = 0
        current_chunk = await self._read_exact_chunk(process.stdout, CHUNK_SIZE)

        while current_chunk:
            next_chunk = await self._read_exact_chunk(process.stdout, CHUNK_SIZE)
            chunk_len = len(current_chunk)

            await self._google_drive_client.upload_chunk(
                upload_url,
                current_chunk,
                offset,
                offset + chunk_len - 1,
                offset + chunk_len if not next_chunk else "*",
            )
            offset += chunk_len
            current_chunk = next_chunk

        await process.wait()

        if os.path.exists(list_file_path):
            os.remove(list_file_path)

    @staticmethod
    async def _download_file(session: aiohttp.ClientSession, url: str) -> str:
        """Download file over network and save into /tmp dir"""
        ext = os.path.splitext(str(url))[1].split("?")[0] or ".mp4"
        filename = f"/tmp/{uuid.uuid4()}{ext}"
        try:
            async with session.get(str(url), timeout=60) as resp:
                if resp.status != 200:
                    raise Exception(f"Download failed {resp.status}: {url}")
                with open(filename, "wb") as f:
                    while True:
                        chunk = await resp.content.read(FILE_CHUNK_SIZE)
                        if not chunk:
                            break
                        f.write(chunk)
            return filename
        except Exception as e:
            if os.path.exists(filename):
                os.remove(filename)
            raise e

    @staticmethod
    def _get_part_args(
        video_paths: list, audio_path: str, speech_path: str, output_filename: str
    ):
        v_streams = [
            ffmpeg.input(path).video.filter("scale", 720, 1280).filter("fps", 30)
            for path in video_paths
        ]

        if len(v_streams) > 1:
            v = ffmpeg.concat(*v_streams, v=1, a=0).node[0]
        else:
            v = v_streams[0]

        video_audio = ffmpeg.input(audio_path, stream_loop=-1).audio.filter(
            "volume", 0.1
        )
        speech_audio = ffmpeg.input(speech_path).audio.filter("volume", 1)
        merged_audio = ffmpeg.filter(
            [video_audio, speech_audio], "amix", inputs=2, duration="longest"
        )
        return (
            ffmpeg.output(
                v,
                merged_audio,
                output_filename,
                format="mp4",
                vcodec="libx264",
                preset="ultrafast",
                acodec="aac",
                ar=44100,
                video_bitrate="2M",
                pix_fmt="yuv420p",
                shortest=None,
                movflags="frag_keyframe+empty_moov",
            )
            .overwrite_output()
            .compile()
        )

    @staticmethod
    async def _read_exact_chunk(stream, size):
        try:
            return await stream.readexactly(size)
        except asyncio.IncompleteReadError as e:
            return e.partial
