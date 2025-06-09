import os
import logging
import json
import time
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

logger = logging.getLogger(__name__)

SERVICE_NAME = os.environ.get('SERVICE_NAME', 'Unknown Service')
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')
TOPIC_NAME = os.environ.get('TOPIC_NAME', 'history-topic')
DATASET_ROOT_DIR = os.environ.get('DATASET_ROOT_DIR')


df = pd.read_csv(f'{DATASET_ROOT_DIR}/history.csv')

def create_kafka_producer(bootstrap_servers, retries=10, delay=3):
    for attempt in range(retries):
        try:
            return KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except NoBrokersAvailable:
            logger.info(f"[Kafka] Broker not ready yet, retrying ({attempt+1}/{retries})...")
            time.sleep(delay)
    raise RuntimeError("Kafka broker not available after retries.")

producer = create_kafka_producer(KAFKA_BROKER)

logger.info(f"[{SERVICE_NAME}] Starting to stream browser history...")
for index, row in df.iterrows():
    timestamp = f"{row['date']} {row['time']}"

    message = {
        'timestamp': timestamp,
        'url': row['url']
    }

    producer.send(TOPIC_NAME, value=message)
    logger.info(f"Sent: {message}")
    time.sleep(0.2)

producer.flush()
producer.close()

logger.info(f"[{SERVICE_NAME}] Finished streaming history.")
