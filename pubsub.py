from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import Any, Callable, Dict, List, Set, Text

connections: List[Connection] = list()
topics: Dict[Any, Set[Connection]] = dict()


def close(data, conn):
    connections.remove(conn)
    for topic in topics.keys():
        topics[topic].remove(conn)

    if not conn.closed:
        conn.close()


def subscribe(data, conn):
    if data['topic'] not in topics:
        topics[data['topic']] = {conn}
    else:
        topics[data['topic']].add(conn)


def pubsub_server(conn: Connection) -> None:
    connections.append(conn)

    funcs: Dict[Text, Callable] = {
        'message': lambda data, conn: [sub.send(data) for sub in topics[data['topic']]],
        'subscribe': subscribe,
        'unsubscribe': lambda data, conn: topics[data['topic']].remove(conn),
        'close': close,
        'add_connection': lambda data, conn: connections.append(data['conn'])
    }

    while True:

        if len(connections) == 0:
            break

        for conn in connections:
            if conn.closed:
                connections.remove(conn)
                for topic in topics.keys():
                    topics[topic].remove(conn)

            elif conn.poll():
                data = conn.recv()
                _type = data['type']

                funcs[_type](data, conn)


def create_pubsub_server():
    parent_conn, child_conn = Pipe()
    Process(target=pubsub_server, args=(parent_conn,)).start()
    return PubSub_Client(child_conn)


class PubSub_Client:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def new_client(self):
        parent_conn, child_conn = Pipe()
        self.conn.send({
            'type': 'add_connection',
            'conn': parent_conn
        })
        return PubSub_Client(child_conn)

    def subscibe(self, topic: Text) -> None:
        self.conn.send({
            'type': 'subscribe',
            'topic': topic
        })

    def unsubscibe(self, topic: Text) -> None:
        self.conn.send({
            'type': 'unsubscibe',
            'topic': topic
        })

    def close(self) -> None:
        self.conn.send({
            'type': 'close'
        })
        self.conn.close()

    def send(self, topic: Text, message: Any) -> None:
        self.conn.send({
            'type': 'message',
            'topic': topic,
            'message': message
        })

    def receive(self):
        return self.conn.recv()
