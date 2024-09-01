import json

from aiokafka import AIOKafkaProducer  # type: ignore

from config import config


class KafkaProducer:
    """Класс продьюсера кафка для удобства инициализации."""

    def __init__(self, bootstrap_servers: str):
        """Конструктор класса."""
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    def serializer(self, value):
        """Метод сериализации сообщений."""
        return json.dumps(value).encode('utf-8')

    async def start(self):
        """Метод запуска продьюсера в одном event_loop с приложением."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=self.serializer,
        )
        await self.producer.start()

    async def stop(self):
        """Метод остановки продьюсера."""
        if self.producer:
            await self.producer.stop()

    async def send_message(self, topic: str, user_data: dict[int, str]):
        """Метод для отправки сообщения."""
        if self.producer is None:
            raise RuntimeError('Producer is not started')
        await self.producer.send_and_wait(
            topic,
            value=user_data,
        )

    async def check(self):
        """Метод для проверки доступности кафка."""
        try:
            await self.start()
            await self.producer.client.fetch_all_metadata()
            await self.stop()
        except Exception:
            return False
        return True


producer = KafkaProducer(
    bootstrap_servers=config.service.kafka_url(),  # type: ignore
)
