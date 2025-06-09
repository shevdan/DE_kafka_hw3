import faust
import tldextract
from collections import Counter

app = faust.App(
    'history-stream-app',
    broker='kafka://redpanda:29092',
    value_serializer='json'
)

history_topic = app.topic('history-topic')

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
            print("\n\nTop 5 root domains:")
            for domain, count in domain_counter.most_common(5):
                print(f"{domain} - {count} visits")
            print("==="*20)

if __name__ == '__main__':
    app.main()
