from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import Any, Callable, Dict, List, Set, Text

connections: List[Connection] = list()
topics: Dict[Any, Set[Connection]] = dict()


def close(data, conn: Connection):
    connections.remove(conn)
    for topic in topics.keys():
        if conn in topics[topic]:
            topics[topic].remove(conn)

    if not conn.closed:
        conn.close()


def subscribe(data, conn: Connection):
    if data['topic'] not in topics:
        topics[data['topic']] = {conn}
    else:
        topics[data['topic']].add(conn)


def unsubscribe(data, conn: Connection):
    topics[data['topic']].remove(conn)


def message(data, conn: Connection):
    if data['topic'] in topics:
        [sub.send(data) for sub in topics[data['topic']]]


def add_connection(data, conn: Connection):
    connections.append(data['conn'])


def lulapy_server(conn: Connection) -> None:
    connections.append(conn)

    funcs: Dict[Text, Callable] = {
        'message': message,
        'subscribe': subscribe,
        'unsubscribe': unsubscribe,
        'close': close,
        'add_connection': add_connection
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


def begin():
    parent_conn, child_conn = Pipe()
    broker = Process(target=lulapy_server, args=(parent_conn,))
    broker.start()
    while not broker.is_alive():
        pass
    return LulaPy_Client(child_conn)


class LulaPy_Client:
    def __init__(self, conn: Connection) -> None:
        self.conn = conn

    def new_client(self):
        parent_conn, child_conn = Pipe()
        self.conn.send({
            'type': 'add_connection',
            'conn': parent_conn
        })
        return LulaPy_Client(child_conn)

    def subscribe(self, topic: Text) -> None:
        self.conn.send({
            'type': 'subscribe',
            'topic': topic
        })

    def unsubscribe(self, topic: Text) -> None:
        self.conn.send({
            'type': 'unsubscribe',
            'topic': topic
        })

    def close(self) -> None:
        self.conn.send({
            'type': 'close'
        })

    def send(self, topic: Text, message: Any) -> None:
        self.conn.send({
            'type': 'message',
            'topic': topic,
            'message': message
        })

    def receive_nowait(self):
        if self.conn.poll():
            return self.conn.recv()

    def receive(self):
        return self.conn.recv()
