import json
import logging
from typing import Callable, Awaitable

import aio_pika
from aio_pika.abc import AbstractRobustChannel

from image_processor.config import get_settings
from image_processor.media.schema import CreateMediaSchema


class Broker:
    def __init__(
        self,
        logger: logging.Logger,
    ):
        self._uri = get_settings().RABBITMQ_URI
        self._queue = None
        self._host = get_settings().RABBITMQ_HOST
        self._port = get_settings().RABBITMQ_PORT
        self._queue_name = get_settings().RABBITMQ_QUEUE_NAME
        self._durable = True
        self._connection = None
        self._channel: AbstractRobustChannel | None = None
        self._logger = logger

    async def connect(self):
        self._connection = await aio_pika.connect_robust(self._uri)
        self._channel = await self._connection.channel()
        self._queue = await self._channel.declare_queue(self._queue_name, durable=self._durable)

    async def publish(
            self,
            message: CreateMediaSchema
    ):
        if not self._connection:
            await self.connect()
        await self._channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(
                    message.model_dump(mode='json')
                ).encode()
            ),
            routing_key=self._queue_name,
        )

    async def close(self):
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def consume(self, callback: Callable[[CreateMediaSchema], Awaitable[None]]):
        self._logger.info(f"Consuming {self._queue_name}")
        if not self._connection:
            await self.connect()

        async with self._queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    self._logger.info(f"Received message: {message.body.decode()}")
                    payload_dict = json.loads(message.body.decode("utf-8"))
                    email_data = CreateMediaSchema(**payload_dict)
                    await callback(email_data)
                    self._logger.info(f"Processed message: {message.body.decode()}")
