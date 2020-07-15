#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import os,sys,time,json,subprocess,concurrent.futures,argparse,logging
    from datetime import datetime
    from bluepy.btle import BTLEDisconnectError
    from constants import MUSICSTATE, ALERT_TYPES
    from auth import miband4_auth
    from bands import miband4
    from rabbitmq_publisher import RabbitMq
    from bluepy.btle import Scanner, DefaultDelegate
    from argparse import RawTextHelpFormatter
#    from colorlog import ColoredFormatter
    from logger import log
except Exception as e:
    print("Some Modules are missings {}".format_map(e))


# SCANNER - look for BLE devices and if there is any Mi Band 4 look for the key in the jason file
# Key acquired by pairing in modified xiaomi app
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    
def scanner_ble(miband3_devices, miband3_radius, miband4_devices, miband4_radius):
    scanner = Scanner().withDelegate(ScanDelegate())
    with open('configs.json') as file:
        data = json.load(file)
    # Scanning time
    devices = scanner.scan(data['scan_time'])
    devices_DB = []
    
    for dev in devices:
        try:
            generic_info = dev.getScanData()
            devices_DB.append((generic_info[2][2], dev.addr, dev.rssi))
        except IndexError: pass
       
    # Saving MAC and radius from the bands
    for device in devices_DB:
        if device[0] == 'Mi Band 3':
            miband3_devices.append(device[1])
            miband3_radius.append(device[2])
            buffer.append(('radius', {"MIBAND3 - {}".format(miband3_devices): miband3_radius}))
        elif device[0] == 'Mi Smart Band 4':
            miband4_devices.append(device[1])
            miband4_radius.append(device[2])
            buffer.append(('radius', {"MIBAND4 - {}".format(miband4_devices): miband4_radius}))

# Running python2 inside python3:
def miband3_pipe(MAC):
    script = ["python", "miband3_python2.py", MAC]
    process = subprocess.Popen(" ".join(script),
            shell=True,
            # Python PATH
            env={"/usr/bin/python": "."})


# MIBAND4 - Search for the authentication key
def miband4_keys_DB(miband4_MAC_KEY):
    with open('miband4_auth_keys.json', 'r') as openfile:
        # Reading from json file
        miband4_keys_dict = json.load(openfile)

    for device in miband4_devices:
        try:
            miband4_MAC_KEY.append([device, miband4_keys_dict[device]])
        except:
            log.error(
                "The device with the MAC -> [{}] has a invalid key!\n Please check the file <miband4_auth_keys.json>".format(
                    device))


def measure_temp():
    temp_c = os.popen('vcgencmd measure_temp').readline()
    temp_c = temp_c.replace("temp=",'')
    temp = temp_c.replace(".0'C",'')
    temp = int(temp)
    if temp > 80:
        return log.critical('Device - CPU OVER TEMPERATURE - %s' % temp_c)
    else:
        return log.info('Device - CPU Temperature - %s' % temp_c)




# Argument parser and --help documentation:
parser = argparse.ArgumentParser(description='''
            - Fitband Aggregator -
This script extracts, organizes and sends data to a
RabbitMQ broker from several bands simultaneously.
Supports Mi Band version 3 and 4

Configuration and usage
--------------------------------------------------------
Mi Band 3
After starting the script it will ask
to touch the screen, proceed to authenticate the band.

Mi Band 4
In the file: < miband4_auth_keys.json >
You must insert the mac address with the key extracted in the
"Free My Band" application, Supports multiple devices.

In the file: < Configs.py >
    scan_time   -   Search time for BLE devices
    log_limit   -   Number of daily logs to be filtered and sent.

Server
--------------------------------------------------------
RabbitMQ broker must respect the following configuration:
    Exchange    -  example-exchange
    Queue       -  example-queue
    Routing Key -  example

Needed topics:
    battery
    hardware
    mi4-logs
    radius
    serial
    software
    steps
    time
    unrouted
''' ,formatter_class=RawTextHelpFormatter )
parser._optionals.title = 'Please choose one of the following arguments'
parser.add_argument('-r','--run', action='store_true', default=False, help='run this script')
parser.add_argument('-d','--debug', action='store_true' ,default=False, help='enable debug mode')

args = vars(parser.parse_args())

if __name__=='__main__':
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    elif args['debug']:
        logging.getLogger('concurrent').propagate = True
        args['run'] = True
    else: 
        logging.getLogger("pika").propagate = False
    if args['run']:
        measure_temp()
        miband4 = miband4()
        buffer = []

        # Memory variables
        miband3_devices = []
        miband3_radius = []
        miband4_devices = []
        miband4_radius = []
        miband4_MAC_KEY = []

        # Uploading data to the memory variables
        scanner_ble(miband3_devices, miband3_radius, miband4_devices, miband4_radius)

        # Search for the authentication key associated with the MAC detected in the scan
        for device in miband4_devices:
            miband4_keys_DB(miband4_MAC_KEY)

        # Threads
        with concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                for mac in miband3_devices:
                    results = [executor.submit(miband3_pipe, mac)]
            except:
                log.warning("No Mi Band 3 devices within reach!")
            try:
                for mac, key in miband4_MAC_KEY:
                    print('TESTE -> MAC {} KEY {}'.format(mac,key))
                    results = [executor.submit(miband4.get_buffer, mac, key, buffer)]
            except:
                log.warning("No Mi Band 4 devices within reach!")

        with concurrent.futures.ProcessPoolExecutor() as executor:
            [executor.submit(RabbitMq.sender, script, payload) for script, payload in buffer]

        measure_temp()
        time.sleep(10)
    else:
        parser.print_help(sys.stderr)

