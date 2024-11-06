# -*- coding: utf-8 -*-

'''
test_networks.py

This script is intended to
check and record network information
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
def network_test():

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

    print(str(time.time()) + ': starting network monitor!')

    onetime_net_info=psutil.net_io_counters(pernic=True)
    old_num_detected_adapters=len(onetime_net_info)

    while True:

        time.sleep(test_cycle_time)

        #grab network information
        net_info = psutil.net_io_counters(pernic=True)
        num_detected_adapters = len(net_info[-1])

        if num_detected_adapters != old_num_detected_adapters:
            print('\n\n     NUMBER OF NETWORK ADAPTERS HAS CHANGED!\n\n')
            print(old_num_detected_adapters)
            print(num_detected_adapters)
            old_num_detected_adapters = num_detected_adapters


        timestamp = int(time.time())

        data = {'net_info':net_info,'num_detected_adapters':num_detected_adapters}
        for key in data:
            point = Point(measurement_name="network").time(timestamp, WritePrecision.S) \
                .field(key, str(data[key]))
            write_api.write(bucket=bucket, org=org, record=point)



#############################################################
# MAIN CODE
#############################################################
if __name__ == '__main__':
    network_test()



