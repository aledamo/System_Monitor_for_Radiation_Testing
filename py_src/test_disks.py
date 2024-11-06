# -*- coding: utf-8 -*-

'''
test_disks.py

This script is intended to poll disks
and record related data
'''

#############################################################
#IMPORT MODULES
#############################################################
import json
import psutil

import influxdb_client, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS

#############################################################
# SUPPORT FUNCTIONS
#############################################################
def disk_test():

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

    print(str(time.time()) + ': starting disk monitor!')

    disks = psutil.disk_partitions()
    old_num_detected_disks = len(disks)

    while True:

        time.sleep(test_cycle_time)

        disks = psutil.disk_partitions()
        num_detected_disks = len(disks)
        disk_info = disks
        nvme_temp = psutil.sensors_temperatures()['nvme'][0].current

        # Other info not used yet
        disk_space_total = psutil.disk_usage(disks[1][0])[0]
        disk_space_used = psutil.disk_usage(disks[1][0])[1]
        disk_space_free = psutil.disk_usage(disks[1][0])[2]
        disk_space_used_pct = psutil.disk_usage(disks[1][0])[3]


        if num_detected_disks != old_num_detected_disks:
            print('\n\n     NUMBER OF DISKS HAS CHANGED!\n\n')
            print(old_num_detected_disks)
            print(num_detected_disks)
            old_num_detected_disks = num_detected_disks

        timestamp = int(time.time())

        data = {'num_detected_disks': num_detected_disks, 'disk_info': disk_info, 'nvme_temp': nvme_temp}
        for key in data:
            point = Point(measurement_name="disks").time(timestamp, WritePrecision.S) \
                .field(key, str(data[key]))
            write_api.write(bucket=bucket, org=org, record=point)

#############################################################
# MAIN CODE
#############################################################
if __name__ == '__main__':
    disk_test()



