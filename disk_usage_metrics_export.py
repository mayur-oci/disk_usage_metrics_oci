import datetime
import json
import os
import time
from datetime import datetime

import oci
import psutil

node_metadata_json = json.loads(os.popen(
    'curl -sH \'Authorization: Bearer Oracle\' http://169.254.169.254/opc/v2/instance | jq -c .').readline().strip())

disk_to_list_of_mount_pts_map = {}


def get_disk_to_mountpoints_map():
    global disk_to_list_of_mount_pts_map
    lsblk = os.popen('lsblk -J --output KNAME,TYPE,MOUNTPOINT,NAME,MODEL,VENDOR  | jq -c .').readline().strip()
    json_lsblk = json.loads(lsblk)
    # print(json_lsblk)
    assert isinstance(json_lsblk['blockdevices'], list)
    for i in list(range(len(json_lsblk['blockdevices']))):
        assert isinstance(json_lsblk['blockdevices'][i], dict)

        single_entry = json_lsblk['blockdevices'][i]

        if single_entry['type'] == 'disk' and single_entry['model'] == 'BlockVolume':
            assert single_entry['vendor'].strip() == 'ORACLE'

            list_of_mount_points = []
            if single_entry['mountpoint'] is None and 'children' in single_entry:
                assert isinstance(single_entry['children'], list)
                partition_list = single_entry['children']
                for j in list(range(len(partition_list))):
                    partition = partition_list[j]
                    assert partition['type'] == 'part'
                    mount_point = partition['mountpoint']

                    if mount_point is not None:
                        # print(mount_point)
                        list_of_mount_points.append(mount_point)
                    else:
                        print('WARN: Skipping unmounted partitions from disk space calculations')

            # in case of un-partitioned disks/block volumes
            elif single_entry['mountpoint'] is not None:
                assert 'children' not in single_entry
                mount_point = single_entry['mountpoint']
                list_of_mount_points.append(mount_point)
                print('no partition direct disk mountpoint ' + mount_point)

            assert len(list_of_mount_points) > 0
            disk_to_list_of_mount_pts_map[single_entry['name']] = list_of_mount_points

    assert len(disk_to_list_of_mount_pts_map) > 0
    print(disk_to_list_of_mount_pts_map)


def calculate_diskwise_usage():
    global disk_to_list_of_mount_pts_map

    if len(disk_to_list_of_mount_pts_map) == 0 or int(time.time()) % 300 <= 10:
        disk_to_list_of_mount_pts_map = {}
        print('refreshing disk_to_list_of_mount_pts_map ')
        print(disk_to_list_of_mount_pts_map)
        get_disk_to_mountpoints_map()

    disk_to_free_space_percentage = {}
    for disk in disk_to_list_of_mount_pts_map.keys():
        list_of_mount_points = disk_to_list_of_mount_pts_map[disk]
        print(disk)
        print(list_of_mount_points)
        total_space = 0
        total_free_space = 0
        for mount_point in list_of_mount_points:
            mount_point_usage = psutil.disk_usage(mount_point)
            total_space = total_space + mount_point_usage.total
            total_free_space = total_free_space + mount_point_usage.free

        percentage_free_space = total_free_space * 100 / total_space
        metric_value_timestamp_pair = (percentage_free_space, datetime.now())

        disk_to_free_space_percentage[disk] = metric_value_timestamp_pair

    print(disk_to_free_space_percentage)
    return disk_to_free_space_percentage


def post_metric_to_oci(diskname, free_space_pct, timestamp):
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    service_endpoint = 'https://telemetry-ingestion.' + node_metadata_json['region'] + '.oraclecloud.com'
    monitoring_client = oci.monitoring.MonitoringClient(config={},
                                                        signer=signer, service_endpoint=service_endpoint)

    post_metric_data_details = oci.monitoring.models.PostMetricDataDetails(metric_data=[
        oci.monitoring.models.MetricDataDetails(namespace="compute_disk",
                                                compartment_id=node_metadata_json['compartmentId'],
                                                name="disk_free_percentage",
                                                dimensions={'resourceId': node_metadata_json['id'],
                                                            'region': node_metadata_json['region'],
                                                            'availabilityDomain': node_metadata_json[
                                                                'availabilityDomain'], 'diskname': diskname},
                                                datapoints=[oci.monitoring.models.Datapoint(timestamp=timestamp,
                                                                                            value=free_space_pct,
                                                                                            count=1)],
                                                metadata={'unit': 'Percentage'})], batch_atomicity="NON_ATOMIC")

    post_metric_data_response = monitoring_client.post_metric_data(
        post_metric_data_details=post_metric_data_details)


def manager():
    while True:
        disk_to_free_space_percentage = calculate_diskwise_usage()

        for diskname in disk_to_free_space_percentage.keys():
            post_metric_to_oci(diskname, disk_to_free_space_percentage[diskname][0],
                               disk_to_free_space_percentage[diskname][1])
            time.sleep(5)


manager()
