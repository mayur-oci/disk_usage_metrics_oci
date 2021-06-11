


# disk_usage_metrics_oci
This is a simple python script to ingest metric for free space percentage for each of disks/blockvolumes attached to OCI instance running any Linux flavoured Operating System. It exports metric(free space percentage) to the same region and compartment as nodes where it is deployed.

## Prerequisites
Following utilities needs to be preinstalled on OCI instance
 1. Python 3, pip3
 2. python packages namely oci, json, time, psutil, datetime and os
 3. Linux commands lsblk, jq, crontab 
 4. make sure crontab service is enabled. Refer [Crontab Reboot](https://phoenixnap.com/kb/crontab-reboot)
 
## Steps
 1. Create dynamic group(say named DG_X) for nodes for which you want to capture disk usage, similar to one below
 
```
All {instance.compartment.id = 'ocid1.compartment.oc1..XXX'}
```

 2.  Create policy for above dynamic group to allow it to post metrics in the same compartment, similar to one below
```
Allow dynamic-group DG_X to use metrics in compartment [Your Compartmentname where Nodes reside]
```
3. Run the script  `disk_usage_metrics_export.py`  as follows.
```
nohup python3 /full/path/to/disk_usage_metrics_export.py&
```

## Configuration
You can change metric namespace and name [here](https://github.com/mayur-oci/disk_usage_metrics_oci/blob/main/disk_usage_metrics_export.py#L96)

## Limitations and Issues

 1. Wont work if a partition belongs multiple block volumes, can be done with LVM.
 2. Currently refreshing disk_to_list_of_mount_pts_map is not timer thread based.
 3. Not tested for crontab scheduling after reboots and crashes of the node.
 4. Disk/Blockvolume names are not their displaynames but the names as per lsblk command, which are visible at OS-level.

 ## Recommended
 1. Use crontab to schedule the script runs from the file `disk_usage_metrics_export.py` even after reboots as follows.

```
crontab -e
@reboot sleep 30 && python3 /full/path/to/disk_usage_metrics_export.py
```
 
 
