#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import subprocess
from logger import log
from bands import miband3

# This is runned in python2
# To send the buffer we need to send it in string type and convert it into a dictionary on the publisher side
def miband3_publish(buffer):
    # Sending the information to be published in python3
    bashCommand = 'sudo python3 sender_for_MI3.py '
    bashCommand = bashCommand.split()
    bashCommand.append(buffer)
    # Creating a parallel pipe process
    process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
    output, error = process.communicate()
    if error == None:
        log.info('Mi Band 3 - Publisher successfully executed')
    else:
        log.error("Mi Band 3 - Existing errors: \n{}".format(error))


# Buffer that send's information in this format:
# [('routing-key', {key:value}), ('routing-key', {key:value})...]
buffer =  []
miband3 = miband3()
mac_address = sys.argv[1]
miband3.miband3_menu(mac_address, buffer)

# Sending information in a string that will be converted with an "ast" library
publisher = str(buffer)
miband3_publish(publisher)