#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import pika
    import time
    import concurrent.futures
    from logger import log
except Exception as e:
    print("Some Modules are missings {}".format_map(e))


class RabbitmqConfigure():
    # Configure Rabbit Mq Server
    # Unconfigured messages go to the unrouted section
    def __init__(self, queue='unrouted-queue', host='localhost', routingKey='unrouted', exchange=''):
        self.queue = queue
        self.host = host
        self.routingKey = routingKey
        self.exchange = exchange

class RabbitMq():

    # Server initialization - uses the object from RabbitmqConfigure
    def __init__(self, server):
        self.server = server
        self._connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.server.host))
        self._channel = self._connection.channel()

    # Publish JSON payload, type = Dictionary - Required to associate the MAC with the extracted information
    def publish(self, payload ={}):
        self._channel.basic_publish(exchange=self.server.exchange,
                      routing_key=self.server.routingKey,
                      body=str(payload))
        for device_mac, information in payload.items():
            log.info('Published in the {}-queue: {} {}'.format(self.server.routingKey, device_mac, information))
    
    def close_connection(self):    
        self._connection.close()

    # Simplified way to publish in rabbitmq, for that we must follow the following standard:
    # queue = default-queue ; exchange = default-exchange ; routingkey = default
    def sender(routingKey,payload):
        server = RabbitmqConfigure(queue='{}-queue'.format(routingKey),
                                    host='localhost',
                                    routingKey=routingKey,
                                    exchange='{}-exchange'.format(routingKey))
        rabbitmq = RabbitMq(server)
        rabbitmq.publish(payload)
        rabbitmq.close_connection()




