import json
import logging

import aiohttp
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class GoogleDriveClient:
    """Google Drive client that provide uploading big files via resumable connection"""

    UPLOAD_API = "https://www.googleapis.com/upload/drive/v3"

    def __init__(self, token_file: str, logger: logging.Logger):
        self.__token_file = token_file
        self.__creds: Credentials | None = None
        self.__session: aiohttp.ClientSession | None = None
        self._logger = logger

    async def shutdown(self):
        if self.__session:
            await self.__session.close()

    async def setup(self):
        try:
            with open(self.__token_file, "r") as f:
                data = json.load(f)
            self.__creds = Credentials.from_authorized_user_info(
                data, scopes=["https://www.googleapis.com/auth/drive"]
            )
            if not self.__creds.valid:
                self.__creds.refresh(Request())
            self.__session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.__creds.token}"}
            )
            return self
        except Exception as e:
            self._logger.error(f"Failed to setup Google Drive client: {e}")
            raise

    def is_ready(self) -> bool:
        if self.__session is None:
            self._refresh_token()
        return self.__session is not None

    def _refresh_token(self):
        if not self.__creds.valid or self.__creds.expired:
            self.__creds.refresh(Request())

    async def upload_file_in_stream(
        self,
        filename: str,
        mime_type: str = "video/mp4",
    ):
        if not self.is_ready():
            raise Exception("Exception in set up")
        metadata = {"name": filename}

        headers = {
            "X-Upload-Content-Type": mime_type,
            "Content-Type": "application/json; charset=UTF-8",
        }

        async with self.__session.post(
            f"{self.UPLOAD_API}/files?uploadType=resumable",
            headers=headers,
            json=metadata,
        ) as response:
            text = await response.text()
            if response.status != 200:
                raise Exception(f"Failed to start upload: {response.status} | {text}")
            if "Location" not in response.headers:
                raise Exception(
                    f"No Location header in response: {dict(response.headers)} | {text}"
                )
            return response.headers["Location"]

    async def upload_chunk(
        self, upload_url: str, chunk: bytes, start: int, end: int, total: int | str
    ):
        if not self.is_ready():
            raise Exception("Exception in set up")
        headers = {
            "Content-Length": str(len(chunk)),
            "Content-Range": f"bytes {start}-{end}/{total}",
        }

        async with self.__session.put(upload_url, headers=headers, data=chunk) as resp:
            if resp.status not in (200, 201, 308):
                raise Exception(f"Upload failed: {await resp.text()}")
