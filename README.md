# LulaPy 🦑

## A Python implementation publish-subscribe to multiprocessing

Basic usage:
```python
import lulapy

pubsub = lulapy.begin()
pubsub.subscribe(topic='foo')
pubsub.send(topic='foo', message='Hello, LulaPy!')

data = pubsub.receive()
```