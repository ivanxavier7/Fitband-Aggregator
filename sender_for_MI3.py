#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Returns the data of the object created in python2 to python3
# Converting the string buffer into a dictionary to use the same publisher
try:
    import sys, ast, concurrent.futures
    from rabbitmq_publisher import RabbitMq
except Exception as e:
    print("Some Modules are missings {}".format_map(e))

def publisher(buffer):
    buffer = ast.literal_eval(buffer)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        return [executor.submit(RabbitMq.sender, script, payload) for script, payload in buffer]


buffer = sys.argv[1]
publisher(buffer)