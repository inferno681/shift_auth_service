from aiokafka import AIOKafkaProducer


def create_producer() -> AIOKafkaProducer:
    """Create AIOKafkaProducer.

    Returns:
        AIOKafkaProducer: The created AIOKafkaProducer instance.
    """

    return AIOKafkaProducer(
        bootstrap_servers='localhost:9092',
    )


producer = create_producer()
