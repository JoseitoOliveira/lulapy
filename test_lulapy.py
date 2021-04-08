from pubsub import create_pubsub_server


def teste_new_client():
    pubsubA = create_pubsub_server()
    pubsubB = pubsubA.new_client()
    pubsubC = pubsubB.new_client()
    pubsubA.subscibe('A')
    pubsubB.subscibe('B')

    pubsubA.send('B', 'Olá, B')

    receivedB = pubsubB.receive()
    assert receivedB == {'message': 'Olá, B', 'topic': 'B', 'type': 'message'}

    pubsubB.send('A', 'Olá, A')

    receivedA = pubsubA.receive()
    assert receivedA == {'message': 'Olá, A', 'topic': 'A', 'type': 'message'}

    assert not pubsubA.conn.poll()
    assert not pubsubB.conn.poll()
    assert not pubsubC.conn.poll()


def test_create_pubsub_server():
    pubsubA = create_pubsub_server()
    pubsubA.subscibe('A')
    pubsubA.send('A', 'Olá mundo')

    received = pubsubA.receive()

    assert received == {'message': 'Olá mundo',
                        'topic': 'A', 'type': 'message'}
