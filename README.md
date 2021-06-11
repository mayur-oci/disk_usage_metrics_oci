



# disk_usage_metrics_oci
This is a simple python script to ingest metric for free disk-space as percentage value, for each of disks/block-volumes attached to an OCI instance, running any Linux flavoured Operating System. It exports metric(free space percentage) to the same region and compartment as of nodes.

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

 1. You can change metric namespace and name
    [here](https://github.com/mayur-oci/disk_usage_metrics_oci/blob/main/disk_usage_metrics_export.py#L96),
    you can also update dimensions.
2. You can use node metadata service to capture almost any field related to OCI node as follows(fyi script already uses it).
```Shell
ubuntu@ubuntu:/$ curl -sH 'Authorization: Bearer Oracle' http://169.254.169.254/opc/v2/instance
{
  "availabilityDomain" : "pqpf:US-SANJOSE-1-AD-1",
  "faultDomain" : "FAULT-DOMAIN-2",
  "compartmentId" : "ocid1.compartment.oc1..aaaaaaaa2z4wup7a4enznwxi3mkk55cperdk3fcotagepjnan5utdb3tvakq",
  "displayName" : "ubuntu",
  "hostname" : "ubuntu",
  "id" : "ocid1.instance.oc1.us-sanjose-1.anzwuljruwpiejqcshxer5x7zcsln2bk27vx4r5oy3qbaftkozjxd4ilbdha",
  "image" : "ocid1.image.oc1.us-sanjose-1.aaaaaaaasgfnf2zpd45xotkww5fqv5xu4fedeypucu7vdc4ph6daxb72bcqa",
  "metadata" : {
    "ssh_authorized_keys" : "ssh-rsa XXX ssh-key-2020-11-09"
  },
  "region" : "us-sanjose-1",
  "canonicalRegionName" : "us-sanjose-1",
  "ociAdName" : "us-sanjose-1-ad-1",
  "regionInfo" : {
    "realmKey" : "oc1",
    "realmDomainComponent" : "oraclecloud.com",
    "regionKey" : "SJC",
    "regionIdentifier" : "us-sanjose-1"
  },
  "shape" : "VM.Standard.E4.Flex",
  "shapeConfig" : {
    "ocpus" : 1.0,
    "memoryInGBs" : 16.0,
    "networkingBandwidthInGbps" : 1.0,
    "maxVnicAttachments" : 2
  },
  "state" : "Running",
  "timeCreated" : 1622582232318,
  "agentConfig" : {
    "monitoringDisabled" : false,
    "managementDisabled" : false,
    "allPluginsDisabled" : false,
    "pluginsConfig" : [ {
      "name" : "Vulnerability Scanning",
      "desiredState" : "DISABLED"
    }, {
      "name" : "Custom Logs Monitoring",
      "desiredState" : "ENABLED"
    }, {
      "name" : "Compute Instance Monitoring",
      "desiredState" : "ENABLED"
    }, {
      "name" : "Bastion",
      "desiredState" : "DISABLED"
    } ]
  },
  "freeformTags" : {
    "os_type" : "ubuntu"
  }
}
```
With `freeform tags`, you can add custom fields to your dimensions of this metric. These are the same tags you have given to node or group of nodes, you are monitoring disk usage of.

## Limitations and Issues

 1. Wont work if a partition belongs multiple block volumes.
 2. Currently refreshing disk_to_list_of_mount_pts_map is not timer thread based.
 3. Not tested for crontab scheduling after reboots and crashes of the node.
 4. Disk/Blockvolume names are not their displaynames as per the OCI-Console but the names as per lsblk command, which is how OS sees them.

 ## Recommended
 1. Use crontab to schedule the script runs from the file `disk_usage_metrics_export.py` even after reboots as follows.
 2. Please test and verify the script giving right disk-free metric values for correctness, for your own environment. There are many ways in which linux disks can be partitioned for filesystem, script is not tested for all possible scenarios.

```
crontab -e
@reboot sleep 30 && python3 /full/path/to/disk_usage_metrics_export.py
```
  2. You can create alarms for absence of a metric in OCI too...in case script is not running or has failed, this alarm can notify sysadmins to set it up again.

 ## Screenshots
 ![Custom Metric for Disk Usage in OCI Console](https://github.com/mayur-oci/disk_usage_metrics_oci/blob/main/image.png?raw=true)
