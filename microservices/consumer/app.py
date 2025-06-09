import os
import logging
import faust
import tldextract
from collections import Counter

SERVICE_NAME = os.environ.get('SERVICE_NAME', 'Unknown Service')
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'localhost:9092')
TOPIC_NAME = os.environ.get('TOPIC_NAME', 'history-topic')

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

logger = logging.getLogger(__name__)

app = faust.App(
    'history-stream-app',
    broker=f'kafka://{KAFKA_BROKER}',
    value_serializer='json'
)

history_topic = app.topic(TOPIC_NAME)

domain_counter = Counter()

@app.agent(history_topic)
async def process(history_events):
    async for event in history_events:
        url = event['url']
        ext = tldextract.extract(url)
        root_domain = ext.suffix
        if root_domain:
            domain_counter[root_domain] += 1

        if sum(domain_counter.values()) % 10 == 0:
            logger.info("\n\nTop 5 root domains:")
            for domain, count in domain_counter.most_common(5):
                logger.info(f"{domain} - {count} visits")
            logger.info("==="*20)

if __name__ == '__main__':
    app.main()
