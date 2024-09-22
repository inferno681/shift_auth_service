import json

from aiokafka import AIOKafkaProducer  # type: ignore

from config import config


class KafkaProducer:
    """Kafka producer."""

    def __init__(self, bootstrap_servers: str):
        """Kafka producer initialization."""
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    def serializer(self, value):
        """Message serializer."""
        return json.dumps(value).encode('utf-8')

    async def start(self):
        """Kafka producer start method."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=self.serializer,
        )
        await self.producer.start()

    async def stop(self):
        """Kafka producer stop method."""
        if self.producer:
            await self.producer.stop()

    async def send_message(self, topic: str, user_data: dict[int, str]):
        """Send message method."""
        if self.producer is None:
            raise RuntimeError('Producer is not started')
        await self.producer.send_and_wait(
            topic,
            value=user_data,
        )


producer = KafkaProducer(
    bootstrap_servers=config.service.kafka_url,  # type: ignore
)
