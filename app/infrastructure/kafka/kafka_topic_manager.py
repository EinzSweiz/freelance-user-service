from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import KafkaConnectionError
from app.infrastructure.logger.logger import AbstractLogger
import asyncio


class KafkaTopicManager:

    def __init__(self, logger: AbstractLogger, bootstrap_servers: str = "kafka:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.logger = logger

    async def create_topics(self, topics: list[str]):
        retries = 5
        delay = 5

        for attempt in range(1, retries + 1):
            try:
                admin_client = AIOKafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
                await admin_client.start()
                self.logger.info("Connected to Kafka as AdminClient")
                break
            except KafkaConnectionError as e:
                self.logger.warning(f"Attempt {attempt}/{retries}: Kafka not ready. Retrying in {delay}s...")
                await asyncio.sleep(delay)
        else:
            self.logger.error("Kafka AdminClient failed after retries.")
            return

        try:
            existing_topics = await admin_client.list_topics()
            new_topics = [
                NewTopic(name=topic, num_partitions=1, replication_factor=1)
                for topic in topics if topic not in existing_topics
            ]
            if new_topics:
                await admin_client.create_topics(new_topics)
                self.logger.info(f"Topics created: {[t.name for t in new_topics]}")
            else:
                self.logger.info("All Kafka topics already exist.")
        except Exception as e:
            self.logger.error(f"Failed to create topics: {e}")
        finally:
            await admin_client.close()