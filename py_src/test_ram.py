# -*- coding: utf-8 -*-

'''
test_ram.py

This script is intended to consume RAM
and monitor it for changed values
'''

#############################################################
#IMPORT MODULES
#############################################################
import os
import sys
import csv
import time
import json
import psutil
from datetime import datetime

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
#############################################################
# SUPPORT FUNCTIONS
#############################################################
def ram_test():

    #load inputs
    with open('data.json') as f:
        data = json.load(f)

    test_cycle_time = data['test_cycle_time']
    ram_pct_to_use = data['ram_pct_to_use']

    host_ip = data['host_ip']
    host_port = data['host_port']
    username = data['username']
    password = data['password']
    org = data['org']
    bucket = data['bucket']
    url = f'http://{host_ip}:{host_port}'

    write_client = influxdb_client.InfluxDBClient(username=username, password=password, url=url, org=org)
    # Define the write api
    write_api = write_client.write_api(write_options=SYNCHRONOUS)

    print(str(time.time()) + ': starting RAM monitor!')

    #allocate available mem
    ram_soaker = []
    ram_info = psutil.virtual_memory()
    ram_pct = int(ram_info[2])
    old_pct = ram_pct

    print('allocating ram...')
    while ram_pct < ram_pct_to_use:

        ram_soaker += ['1' * 512000]
        ram_info = psutil.virtual_memory()
        ram_pct = int(ram_info[2])
        if ram_pct != old_pct:
            print(ram_pct)
            old_pct = ram_pct


    print('...RAM allocation complete!')
    ram_info = psutil.virtual_memory()
    ram_pct = int(ram_info[2])
    print(ram_pct)
    print(len(ram_soaker))

    print('\n\nWatching for changed RAM vals...')

    while True:

        time.sleep(test_cycle_time)

        outliers = [i for i in range(1,len(ram_soaker)) if ram_soaker[i]!=ram_soaker[i-1] ]
        if len(outliers) > 0:
            print('\n\n     RAM STATE CHANGE DETECTED!\n\n')
            upsets=1
        else:
            upsets=0

        ram_info = psutil.virtual_memory()
        ram_pct = ram_info[2]
        ram_pct_used = ram_pct

        timestamp = int(time.time())

        data = {'ram_pct_used': ram_pct_used, 'upsets': upsets}
        for key in data:
            point = Point(measurement_name="network").time(timestamp, WritePrecision.S) \
                .field(key, str(data[key]))
            write_api.write(bucket=bucket, org=org, record=point)


#############################################################
# MAIN CODE
#############################################################
if __name__ == '__main__':
    ram_test()



