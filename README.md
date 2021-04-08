# LulaPy 🦑

## A Python implementation publish-subscribe to multiprocessing

Basic usage:
```python
import lulapy

pubsub = lulapy.begin()
pubsub.subscribe(topic='foo')
pubsub.send(topic='foo', message='Hello, LulaPy!')

data = pubsub.receive()
pubsub.close()
```

Usage with Process:
```python
import lulapy
from multiprocessing import Process


def foo(pb: lulapy.LulaPy_Client):
    pb.send(topic='echo', message='Hello, LulaPy!')
    pb.close()


if __name__ == '__main__':
    pubsub = lulapy.begin()
    pubsub.subscribe('echo')

    Process(target=foo, args=(pubsub.new_client(),)).start()

    data = pubsub.receive()
    print(data)

    pubsub.close()
```
>_Output: {'type': 'message', 'topic': 'echo', 'message': 'Hello, LulaPy!'}_ 

Another example more complex:
```python
from datetime import datetime
from multiprocessing import Process
from time import sleep

import lulapy


def foo(pb: lulapy.LulaPy_Client, _id):
    pb.subscribe(f'foo_{_id}')
    pb.subscribe(f'quit')
    while True:
        data = pb.receive()

        if data['topic'] == 'quit':
            break

        msg, t = data['message']
        print(f'foo_{_id}: {msg} {datetime.now() - t}')
        pb.send(f'foo_{_id+1}', (f'Hello, foo_{_id+1}!', t))

    pb.close()


def p_time(pb: lulapy.LulaPy_Client):
    pb.subscribe(f'quit')
    while True:
        sleep(1)
        data = pb.receive_nowait()
        if data and data['topic'] == 'quit':
            break

        pb.send('foo_0', ('Hello, foo_0!', datetime.now()))

    pb.close()


if __name__ == '__main__':
    pubsub = lulapy.begin()

    [Process(target=foo, args=(pubsub.new_client(), _id)).start()
     for _id in range(10)]
    Process(target=p_time, args=(pubsub.new_client(),)).start()

    sleep(4)
    pubsub.send('quit', '')
    pubsub.close()

```