import lulapy
from multiprocessing import Process
from time import sleep


def teste_new_client():
    pubsubA = lulapy.begin()
    pubsubB = pubsubA.new_client()
    pubsubC = pubsubB.new_client()
    pubsubA.subscribe('A')
    pubsubB.subscribe('B')

    pubsubA.send('B', 'Olá, B')

    receivedB = pubsubB.receive()
    assert receivedB == {'message': 'Olá, B', 'topic': 'B', 'type': 'message'}

    pubsubB.send('A', 'Olá, A')

    receivedA = pubsubA.receive()
    assert receivedA == {'message': 'Olá, A', 'topic': 'A', 'type': 'message'}

    assert not pubsubA.conn.poll()
    assert not pubsubB.conn.poll()
    assert not pubsubC.conn.poll()


def echo(pb: lulapy.LulaPy_Client):
    pb.subscribe('foo')
    data = pb.receive()
    print(data)
    pb.send(topic='echo', message=data['message'])


def test_comunication_with_process():

    pubsub = lulapy.begin()
    pubsub.subscribe('echo')

    Process(target=echo, args=(pubsub.new_client(),)).start()
    sleep(0.5)
    pubsub.send('foo', 'bar')
    data = pubsub.receive()

    assert data == {'message': 'bar',
                    'topic': 'echo', 'type': 'message'}

    pubsub.close()


def test_create_pubsub_server():
    pubsubA = lulapy.begin()
    pubsubA.subscribe('A')
    pubsubA.send('A', 'Olá mundo')

    received = pubsubA.receive()

    assert received == {'message': 'Olá mundo',
                        'topic': 'A', 'type': 'message'}
