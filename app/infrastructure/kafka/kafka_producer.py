from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
import asyncio
from fastapi import Request
import json
from app.infrastructure.logger.logger import AbstractLogger

class KafkaProducer:
    def __init__(self, bootstrap_servers: str, logger: AbstractLogger):
        self.bootstrap_servers = bootstrap_servers
        self.producer: AIOKafkaProducer = None
        self.logger = logger

    async def connect(self):
        for attempt in range(5):
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                await self.producer.start()
                self.logger.info("Connected to Kafka")
                return
            except Exception as e:
                self.logger.error(f"Failed to connect to Kafka (attempt {attempt+1}): {e}")
                await asyncio.sleep(3)
        raise KafkaConnectionError("Failed to connect to Kafka after 5 attempts")

    async def stop(self):
        if self.producer:
            await self.producer.flush()
            await self.producer.stop()
            self.logger.info("Stopped Kafka producer")

    async def send(self, topic: str, event: dict):
        if not self.producer or self.producer._closed:
            self.logger.error("Kafka producer is not active")
            return

        try:
            self.logger.info(f"Sending event to topic '{topic}': {event}")
            await self.producer.send_and_wait(topic, event)
        except Exception as e:
            self.logger.error(f"Failed to send event to topic '{topic}': {e}")
   
async def get_kafka_producer(request: Request) -> KafkaProducer:
    return request.app.state.kafka_producer


