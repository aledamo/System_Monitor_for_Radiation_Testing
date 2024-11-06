# -*- coding: utf-8 -*-

'''
test_cpu.py

This script is intended to 
monitor CPU usage
'''

#############################################################
#IMPORT MODULES
#############################################################

import json
import psutil

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS


#############################################################
# SUPPORT FUNCTIONS
#############################################################
def cpu_test(data_dirname):

    #load inputs
    with open('data.json') as f:
        data = json.load(f)

    test_cycle_time = data['test_cycle_time']

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

    print(str(time.time()) + ': starting CPU monitor!')


    while True:
        time.sleep(test_cycle_time)

        cpu_pct_used = psutil.cpu_percent()
        cpu_freq = psutil.cpu_freq(percpu=False).current
        cpu_count = psutil.cpu_count()
        cpu_temp = psutil.sensors_temperatures()['coretemp'][0].current # Valid on linux only

        timestamp = int(time.time())
        data = {'cpu_pct_used': cpu_pct_used, 'cpu_temp': cpu_temp, 'cpu_freq': cpu_freq,
                'cpu_count': cpu_count}
        for key in data:
            point = Point(measurement_name="cpu").time(timestamp, WritePrecision.S) \
            .field(key, str(data[key]))
            write_api.write(bucket=bucket, org=org, record=point)

#############################################################
# MAIN CODE
#############################################################
if __name__ == '__main__':
    cpu_test()




